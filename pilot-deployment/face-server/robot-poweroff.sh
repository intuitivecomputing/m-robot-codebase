#!/bin/bash
set -euo pipefail

log() {
  echo "[robot-poweroff] $*"
}

log "Poweroff requested. Stopping storytelling robot service..."

# Stop the main service (which should stop Firefox/Node and the docker container)
if systemctl is-active --quiet storytelling_robot.service; then
  systemctl stop storytelling_robot.service
else
  log "storytelling_robot.service not active"
fi

# Best-effort: ensure the session container is stopped if it remains.
if command -v docker >/dev/null 2>&1; then
  if docker ps --format '{{.Names}}' | grep -qx 'ella_robot_session'; then
    log "Stopping remaining docker container ella_robot_session..."
    docker stop -t 45 ella_robot_session || true
  fi
fi

log "Powering off host now"
systemctl poweroff
