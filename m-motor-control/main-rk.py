import time
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

def demo():
    robot = Robot(ROBOT_CFG)
    anim  = RobotAnimator(robot)

    # tiny “wave” timeline
    wave = Timeline.from_script([
            {"at": 0.0, "pose": {"arm_left": 0}, "easing": "easeInOutPoly"},
            {"at": 0.5, "pose": {"arm_left": 80}, "end_time": 2.6, "easing": "easeInOutPoly"},
            {"at": 1.5, "pose": {"arm_right": 40}, 'duration': 1.5, "easing": "easeInOutPoly"},
        ])
    complex_expression = Timeline.from_script([
            # === Step 1 ===
            {"at": 0.0, "pose": {
                "head_yaw": -10, "head_pitch": 5,
                "arm_left": 30, "arm_right": 45
            }, "duration": 0.6, "easing": "easeInOutSine"},

            # === Step 2 ===
            {"at": 0.6, "pose": {"base_rotation": 15}, "duration": 0.6, "easing": "easeInOutSine"},

            {"at": 0.6, "pose": {"arm_left": 50}, "duration": 0.35, "easing": "easeInOutSine"},
            {"at": 0.95, "pose": {"arm_left": 30}, "duration": 0.35, "easing": "easeInOutSine"},
            {"at": 1.3, "pose": {"arm_left": 50}, "duration": 0.35, "easing": "easeInOutSine"},
            {"at": 1.65, "pose": {"arm_left": 30}, "duration": 0.35, "easing": "easeInOutSine"},

            {"at": 0.75, "pose": {"arm_right": 25}, "duration": 0.35, "easing": "easeInOutSine"},
            {"at": 1.1, "pose": {"arm_right": 45}, "duration": 0.35, "easing": "easeInOutSine"},
            {"at": 1.45, "pose": {"arm_right": 25}, "duration": 0.35, "easing": "easeInOutSine"},
            {"at": 1.8, "pose": {"arm_right": 45}, "duration": 0.35, "easing": "easeInOutSine"},

            {"at": 0.6, "pose": {"head_yaw": 10, "head_pitch": -5}, "duration": 0.6, "easing": "easeInOutSine"},
            {"at": 1.2, "pose": {"head_pitch": 0}, "duration": 0.6, "easing": "easeInOutSine"},

            # === Step 3 ===
            {"at": 2.0, "pose": {"base_rotation": -20}, "duration": 0.8, "easing": "easeInOutSine"},
            {"at": 2.0, "pose": {"arm_left": 10}, "duration": 0.4, "easing": "easeInOutSine"},
            {"at": 2.4, "pose": {"arm_left": 40}, "duration": 0.4, "easing": "easeInOutSine"},
            {"at": 2.0, "pose": {"arm_right": 55}, "duration": 0.8, "easing": "easeOutElastic"},
            {"at": 2.0, "pose": {"head_pitch": -10}, "duration": 0.25, "easing": "easeInOutSine"},
            {"at": 2.25, "pose": {"head_pitch": 5}, "duration": 0.25, "easing": "easeInOutSine"},
            {"at": 2.5, "pose": {"head_pitch": -10}, "duration": 0.25, "easing": "easeInOutSine"},
            {"at": 2.75, "pose": {"head_pitch": 5}, "duration": 0.25, "easing": "easeInOutSine"},

            # === Step 4 ===
            {"at": 3.0, "pose": {"base_rotation": 10}, "duration": 0.5, "easing": "easeInOutSine"},
            {"at": 3.5, "pose": {"base_rotation": -10}, "duration": 0.5, "easing": "easeInOutSine"},
            {"at": 4.0, "pose": {"base_rotation": 10}, "duration": 0.5, "easing": "easeInOutSine"},
            {"at": 4.5, "pose": {"base_rotation": -10}, "duration": 0.5, "easing": "easeInOutSine"},

            {"at": 3.0, "pose": {"arm_left": 50}, "duration": 0.3},
            {"at": 3.6, "pose": {"arm_left": 30}, "duration": 0.3},
            {"at": 4.2, "pose": {"arm_left": 50}, "duration": 0.3},

            {"at": 3.2, "pose": {"arm_right": 25}, "duration": 0.3},
            {"at": 3.8, "pose": {"arm_right": 45}, "duration": 0.3},
            {"at": 4.4, "pose": {"arm_right": 25}, "duration": 0.3},

            {"at": 3.0, "pose": {"head_yaw": 0}, "duration": 0.5},
            {"at": 3.5, "pose": {"head_yaw": -15}, "duration": 0.5},
            {"at": 4.0, "pose": {"head_yaw": 0}, "duration": 0.5},

            # === Step 5 ===
            {"at": 5.0, "pose": {"head_pitch": -10, "head_yaw": 0}, "duration": 0.6, "easing": "easeInOutSine"},
            {"at": 5.0, "pose": {"arm_left": 60, "arm_right": 60}, "duration": 1.0, "easing": "easeOutElastic"},
        ])

    try:
        anim.play_timeline(complex_expression)
        while anim._thread and anim._thread.is_alive():
            time.sleep(0.1)
    finally:
        anim.stop_all()
        robot.cleanup()

if __name__ == "__main__":
    demo()
