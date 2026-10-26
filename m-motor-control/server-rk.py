import time
import threading
import atexit
import signal
from flask import Flask, request, jsonify
from flask_cors import CORS
from robot_kit import Robot, RobotAnimator, Timeline

# ── Robot configuration ──────────────────────────────────────────
ROBOT_CFG = {
    "motors": {
        # ── 270 ° servos ─────────────────────────────────────────
        "base_rotation": {
            "channel": 0,
            "range": [-120, 120],     # robot coordinates
            "offset": 140,            # raw‑servo angle that *is* robot 0 °
            "servo_range": [0, 270],  # ← true hardware span
        },
        "head_pitch": {
            "channel": 2,
            "range": [-40, 40],
            "offset": 0,
            "servo_range": [0, 270],
        },
        "head_yaw": {
            "channel": 4,
            "range": [-90, 90],
            "offset": 135,
            "servo_range": [0, 270],
        },

        # ── 180 ° servos (the two arms) ─────────────────────────
        "arm_left": {
            "channel": 8,
            "range": [-45, 135],
            "offset": 135,
            "flip": True,
            "servo_range": [0, 180],
        },
        "arm_right": {
            "channel": 10,
            "range": [-45, 135],
            "offset": 45,
            "servo_range": [0, 180],
        },
    }
}

# ── Flask app setup ──────────────────────────────────────────────
app = Flask(__name__)
CORS(app)
# Instantiate robot + animator once at startup so we can reuse the same
# hardware connection for every request.
robot = Robot(ROBOT_CFG)
animator = RobotAnimator(robot)
_anim_lock = threading.Lock()  # make sure we don’t step on ourselves


# ── Helper: shutdown cleanup ─────────────────────────────────────

def _cleanup(*_):
    """Stop any running animations and release hardware on shutdown."""
    with _anim_lock:
        try:
            animator.stop_all()
        finally:
            robot.cleanup()

# Clean up on normal process exit *and* on SIGINT/SIGTERM so that Ctrl‑C
# or Docker ‘stop’ does the right thing.
atexit.register(_cleanup)
for _sig in (signal.SIGINT, signal.SIGTERM):
    signal.signal(_sig, _cleanup)


# ── Routes ───────────────────────────────────────────────────────

@app.route("/animate", methods=["POST"])
def animate_route():
    """POST /animate  ⇒  {"script": [ …keyframes… ]}

    * Accepts a JSON body containing a `script` list of key‑frame dictionaries.
    * Converts it to a `Timeline` via `Timeline.from_script`.
    * Starts the timeline on the background animation thread.
    """
    data = request.get_json(force=True, silent=True) or {}
    script = data.get("script")

    if not isinstance(script, list):
        return jsonify({"error": "Request JSON must include a *list* field 'script'."}), 400

    try:
        timeline = Timeline.from_script(script)
    except Exception as exc:
        return jsonify({"error": f"Invalid script: {exc}"}), 400

    # Play the timeline – protected by a lock so concurrent POSTs don’t collide.
    with _anim_lock:
        try:
            animator.play_timeline(timeline)
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    return jsonify({"status": "started"}), 202


@app.route("/health", methods=["GET"])
def health_route():
    """Simple liveness probe."""
    return jsonify({"status": "ok"}), 200


# ── Main entry‑point ─────────────────────────────────────────────

if __name__ == "__main__":
    # Listen on all interfaces so it works inside containers / on LAN.
    app.run(host="127.0.0.1", port=5000)