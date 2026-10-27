#!/usr/bin/env bash
set -euo pipefail

log() { printf "\n\033[1;32m==>\033[0m %s\n" "$*"; }
warn() { printf "\n\033[1;33m[WARN]\033[0m %s\n" "$*"; }
die() { printf "\n\033[1;31m[ERR]\033[0m %s\n" "$*"; exit 1; }

# ---- Config you may want to tweak ----
NVM_VERSION="v0.39.7"
NODE_MAJOR="21"

# Camera virtcam defaults
VIDEO_NR="10"
WIDTH="640"
HEIGHT="480"
FPS="30"
ROI="0,0,1,1"
PIXFMT="yuv420p"
MODE="3280:2464:10:P"

ENV_FILE="/etc/default/libcamera-virtcam"
SERVICE_FILE="/etc/systemd/system/libcamera-ffmpeg@.service"

REQ_FILE="${HOME}/Documents/m-motor-control/requirements.txt"
# ---------------------------
# Enable I2C
# ---------------------------
log "Enabling I2C interface (raspi-config non-interactive)"
if command -v raspi-config >/dev/null; then
  sudo raspi-config nonint do_i2c 0
  log "I2C enabled via raspi-config."
else
  warn "raspi-config not found. Skipping I2C enable step."
fi

VENV_DIR="${HOME}/motor_env"

# Must be run as normal user (uses sudo as needed)
if [[ "${EUID}" -eq 0 ]]; then
  die "Run as a normal user, not root. This script uses sudo where needed."
fi
command -v sudo >/dev/null || die "sudo not found."

log "Installing basic tools (vim, curl, etc.)"
sudo apt-get update
sudo apt-get install -y vim curl ca-certificates gnupg lsb-release apt-transport-https

# ---------------------------
# Node + npm via NVM
# ---------------------------
log "Installing NVM (${NVM_VERSION})"
# Install nvm if not already present
if [[ ! -d "${HOME}/.nvm" ]]; then
  curl -o- "https://raw.githubusercontent.com/nvm-sh/nvm/${NVM_VERSION}/install.sh" | bash
else
  warn "~/.nvm already exists; skipping NVM install."
fi

# Load nvm into this shell
export NVM_DIR="${HOME}/.nvm"
# shellcheck disable=SC1091
source "${NVM_DIR}/nvm.sh"

log "Installing Node ${NODE_MAJOR} and setting default"
nvm install "${NODE_MAJOR}"
nvm use "${NODE_MAJOR}"
nvm alias default "${NODE_MAJOR}"

log "Node install check"
node -v || true
npm -v || true

# ---------------------------
# Docker (Debian)
# ---------------------------
log "Installing Docker (Docker CE repo)"
# Add Docker’s official GPG key
sudo install -m 0755 -d /usr/share/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
sudo chmod a+r /usr/share/keyrings/docker-archive-keyring.gpg

# Add the repo
CODENAME="$(lsb_release -cs)"
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian ${CODENAME} stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

log "Adding user to docker group"
sudo usermod -aG docker "${USER}"

warn "NOTE: Docker group change usually requires logging out/in (or a new shell)."
warn "After this script finishes, you can run: newgrp docker"
warn "Then (in the directory containing your image tar): docker load -i <image_name>.tar"

# ---------------------------
# Camera stream to /dev/video${VIDEO_NR}
# ---------------------------
log "Installing camera + v4l2 loopback tooling"
sudo apt-get update
sudo apt-get install -y v4l2loopback-dkms v4l-utils rpicam-apps ffmpeg

log "Making v4l2loopback persistent"
echo v4l2loopback | sudo tee /etc/modules-load.d/v4l2loopback.conf >/dev/null
echo "options v4l2loopback exclusive_caps=1 video_nr=${VIDEO_NR} card_label=\"rpicam\"" \
  | sudo tee /etc/modprobe.d/v4l2loopback.conf >/dev/null

log "Writing shared env file: ${ENV_FILE}"
sudo tee "${ENV_FILE}" >/dev/null <<EOF
VIDEO_NR=${VIDEO_NR}
WIDTH=${WIDTH}
HEIGHT=${HEIGHT}
FPS=${FPS}
ROI=${ROI}
PIXFMT=${PIXFMT}
MODE=${MODE}
EOF

log "Writing systemd unit: ${SERVICE_FILE}"
sudo tee "${SERVICE_FILE}" >/dev/null <<'EOF'
[Unit]
Description=libcamera (rpicam-vid) → V4L2 (FFmpeg) on /dev/video%I
After=multi-user.target
Wants=multi-user.target

[Service]
Type=simple
EnvironmentFile=/etc/default/libcamera-virtcam
ExecStartPre=/usr/sbin/modprobe v4l2loopback exclusive_caps=1 video_nr=%I card_label=rpicam
ExecStartPre=/bin/sh -c 'for i in $(seq 1 10); do [ -e /dev/video%I ] && exit 0; sleep 0.2; done; exit 0'
ExecStart=/bin/bash -lc '\
  ROI_ARG=""; [ -n "$ROI" ] && ROI_ARG="--roi $ROI"; \
  MODE_ARG=""; [ -n "$MODE" ] && MODE_ARG="--mode $MODE"; \
  exec /usr/bin/rpicam-vid \
      --width ${WIDTH} \
      --height ${HEIGHT} \
      --mode ${MODE} \
      --roi ${ROI} \
      --codec yuv420 \
      -t 0 -o - \
    | /usr/bin/ffmpeg -loglevel warning -nostdin -y \
      -f rawvideo -pixel_format ${PIXFMT} -video_size ${WIDTH}x${HEIGHT} -framerate ${FPS} -i - \
      -vf "setsar=1" \
      -f v4l2 -pix_fmt ${PIXFMT} /dev/video%I \
'
Restart=on-failure
RestartSec=1

[Install]
WantedBy=multi-user.target
EOF

log "Enabling camera stream service: libcamera-ffmpeg@${VIDEO_NR}.service"
sudo systemctl daemon-reload
sudo systemctl enable --now "libcamera-ffmpeg@${VIDEO_NR}.service"

log "Quick status checks"
systemctl status "libcamera-ffmpeg@${VIDEO_NR}" --no-pager || true
v4l2-ctl -d "/dev/video${VIDEO_NR}" --all | head || true

warn "To preview stream locally:"
warn "  ffplay -f v4l2 -i /dev/video${VIDEO_NR}"
warn "To test raw host camera stream (optional):"
warn "  rpicam-vid --width ${WIDTH} --height ${HEIGHT} --mode ${MODE} --roi ${ROI} --codec yuv420 -t 0 -o - >/dev/null"


# ---------------------------
# Unzip m-motor-control.zip before venv
# ---------------------------
ZIP_SRC="${HOME}/Documents/m-motor-control.zip"
UNZIP_DST="${HOME}/Documents"
if [[ -f "${ZIP_SRC}" ]]; then
  log "Unzipping ${ZIP_SRC} to ${UNZIP_DST}"
  unzip -o "${ZIP_SRC}" -d "${UNZIP_DST}"
else
  warn "Zip file not found at: ${ZIP_SRC}"
fi

# ---------------------------
# Motor control venv
# ---------------------------
log "Creating Python venv at ${VENV_DIR}"
python3 -m venv "${VENV_DIR}"

log "Installing motor control requirements"
# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"
python -m pip install --upgrade pip
if [[ -f "${REQ_FILE}" ]]; then
  pip install -r "${REQ_FILE}"
else
  warn "Requirements file not found at: ${REQ_FILE}"
  warn "Skipping pip install -r. Put the file there and run:"
  warn "  source '${VENV_DIR}/bin/activate' && pip install -r '${REQ_FILE}'"
fi
deactivate || true

log "Done."
warn "If Docker permissions don't work yet, log out/in or run: newgrp docker"

log "Setup complete. Rebooting in 5 seconds (Ctrl+C to cancel)..."
sleep 5
sudo reboot

