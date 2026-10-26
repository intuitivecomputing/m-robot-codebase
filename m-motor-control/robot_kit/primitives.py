from typing import List, Dict, Literal

Speed = Literal["high", "medium", "low"]
Side = Literal["left", "right", "both"]

# ---------------------------------------------------------------------------
# Timing & utility helpers
# ---------------------------------------------------------------------------

def _clamp(val: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(max_val, val))

def _speed_factor(speed: Speed) -> float:
    """
    Smaller factor = faster motion.
    """
    speed = speed.lower()
    if speed == "high":
        return 0.5
    if speed == "low":
        return 1.5
    return 1.0  # medium default

def _base_duration(speed: Speed, base: float = 0.5) -> float:
    """
    Base duration for a single segment, modulated by speed.
    """
    return base * _speed_factor(speed)

# joint limits from the body2code prompt
HEAD_YAW_MIN, HEAD_YAW_MAX = -60.0, 60.0
HEAD_PITCH_MIN, HEAD_PITCH_MAX = -30.0, 30.0
ARM_MIN, ARM_MAX = -30.0, 120.0
BASE_ROT_MIN, BASE_ROT_MAX = -90.0, 90.0

# ---------------------------------------------------------------------------
# 1. HeadYawTo(angle, speed)
# ---------------------------------------------------------------------------

def HeadYawTo(angle: float, speed: Speed, start_at: float = 0.0) -> List[Dict]:
    """
    Absolute yaw: rotate head to `angle` degrees (left/right).
    """
    angle = _clamp(angle, HEAD_YAW_MIN, HEAD_YAW_MAX)
    duration = _base_duration(speed, base=0.5)

    return [
        {
            "at": float(start_at),
            "pose": {"head_yaw": float(angle)},
            "duration": float(duration),
        }
    ]

# ---------------------------------------------------------------------------
# 2. HeadPitchTo(angle, speed)
# ---------------------------------------------------------------------------

def HeadPitchTo(angle: float, speed: Speed, start_at: float = 0.0) -> List[Dict]:
    """
    Absolute pitch: tilt head to `angle` degrees (up/down).
    """
    angle = _clamp(angle, HEAD_PITCH_MIN, HEAD_PITCH_MAX)
    duration = _base_duration(speed, base=0.5)

    return [
        {
            "at": float(start_at),
            "pose": {"head_pitch": float(angle)},
            "duration": float(duration),
        }
    ]

# ---------------------------------------------------------------------------
# 3. HeadNod(amplitude, speed, cycles)
#    Simple down-up nod around neutral (0° pitch).
# ---------------------------------------------------------------------------

def HeadNod(amplitude: float, speed: Speed, cycles: int, start_at: float = 0.0) -> List[Dict]:
    """
    Nods the head `cycles` times with given amplitude.
    Convention here: nod 'down' is negative pitch (following your example),
    and we return to 0° between peaks.
    """
    stages: List[Dict] = []
    t = float(start_at)
    amplitude = abs(amplitude)
    down_angle = _clamp(-amplitude, HEAD_PITCH_MIN, HEAD_PITCH_MAX)
    neutral_angle = 0.0

    seg_duration = _base_duration(speed, base=0.3)

    for _ in range(max(1, cycles)):
        # down
        stages.append(
            {
                "at": t,
                "pose": {"head_pitch": float(down_angle)},
                "duration": float(seg_duration),
            }
        )
        t += seg_duration
        # up (back to neutral)
        stages.append(
            {
                "at": t,
                "pose": {"head_pitch": float(neutral_angle)},
                "duration": float(seg_duration),
            }
        )
        t += seg_duration

    return stages

# ---------------------------------------------------------------------------
# 4. HeadShake(amplitude, speed, cycles)
#    Left-right shake around neutral yaw (0°).
# ---------------------------------------------------------------------------

def HeadShake(amplitude: float, speed: Speed, cycles: int, start_at: float = 0.0) -> List[Dict]:
    """
    Shakes head left-right `cycles` times.
    Pattern per cycle: center -> left -> right -> center.
    """
    stages: List[Dict] = []
    t = float(start_at)
    amplitude = abs(amplitude)

    left_angle = _clamp(-amplitude, HEAD_YAW_MIN, HEAD_YAW_MAX)
    right_angle = _clamp(+amplitude, HEAD_YAW_MIN, HEAD_YAW_MAX)
    center_angle = 0.0

    seg_duration = _base_duration(speed, base=0.25)

    for _ in range(max(1, cycles)):
        # center -> left
        stages.append(
            {
                "at": t,
                "pose": {"head_yaw": float(left_angle)},
                "duration": float(seg_duration),
            }
        )
        t += seg_duration
        # left -> right
        stages.append(
            {
                "at": t,
                "pose": {"head_yaw": float(right_angle)},
                "duration": float(seg_duration),
            }
        )
        t += seg_duration
        # right -> center
        stages.append(
            {
                "at": t,
                "pose": {"head_yaw": float(center_angle)},
                "duration": float(seg_duration),
            }
        )
        t += seg_duration

    return stages

# ---------------------------------------------------------------------------
# 5. HeadTilt(angle, speed)
#    Simple pitch-based tilt (can be used as a static “listening” tilt).
# ---------------------------------------------------------------------------

def HeadTilt(angle: float, speed: Speed, start_at: float = 0.0) -> List[Dict]:
    """
    Tilts head in pitch to an absolute `angle`.
    (If you want micro-tilts, you can call this with small angles.)
    """
    angle = _clamp(angle, HEAD_PITCH_MIN, HEAD_PITCH_MAX)
    duration = _base_duration(speed, base=0.4)

    return [
        {
            "at": float(start_at),
            "pose": {"head_pitch": float(angle)},
            "duration": float(duration),
        }
    ]

# ---------------------------------------------------------------------------
# 6. TorsoYawTo(angle, speed)
#    Maps to base_rotation.
# ---------------------------------------------------------------------------

def TorsoYawTo(angle: float, speed: Speed, start_at: float = 0.0) -> List[Dict]:
    """
    Rotates the torso (base_rotation) to an absolute heading.
    """
    angle = _clamp(angle, BASE_ROT_MIN, BASE_ROT_MAX)
    duration = _base_duration(speed, base=0.7)

    return [
        {
            "at": float(start_at),
            "pose": {"base_rotation": float(angle)},
            "duration": float(duration),
        }
    ]

# ---------------------------------------------------------------------------
# 7. TorsoOscillate(amplitude, speed, cycles)
#    Slow left-right oscillation around center.
# ---------------------------------------------------------------------------

def TorsoOscillate(amplitude: float, speed: Speed, cycles: int, start_at: float = 0.0) -> List[Dict]:
    """
    Oscillates the torso left/right around 0°.
    Each cycle: center -> +amplitude -> -amplitude -> center.
    """
    stages: List[Dict] = []
    t = float(start_at)
    amplitude = abs(amplitude)

    left_angle = _clamp(-amplitude, BASE_ROT_MIN, BASE_ROT_MAX)
    right_angle = _clamp(+amplitude, BASE_ROT_MIN, BASE_ROT_MAX)
    center_angle = 0.0

    seg_duration = _base_duration(speed, base=0.6)

    for _ in range(max(1, cycles)):
        # center -> right
        stages.append(
            {
                "at": t,
                "pose": {"base_rotation": float(right_angle)},
                "duration": float(seg_duration),
            }
        )
        t += seg_duration
        # right -> left
        stages.append(
            {
                "at": t,
                "pose": {"base_rotation": float(left_angle)},
                "duration": float(seg_duration),
            }
        )
        t += seg_duration
        # left -> center
        stages.append(
            {
                "at": t,
                "pose": {"base_rotation": float(center_angle)},
                "duration": float(seg_duration),
            }
        )
        t += seg_duration

    return stages

# ---------------------------------------------------------------------------
# 8. ArmTo(side, angle, speed)
# ---------------------------------------------------------------------------

def _side_to_joint(side: Side) -> List[str]:
    side = side.lower()
    if side == "left":
        return ["arm_left"]
    if side == "right":
        return ["arm_right"]
    if side == "both":
        return ["arm_left", "arm_right"]
    raise ValueError(f"Invalid side: {side}")

def ArmTo(side: Side, angle: float, speed: Speed, start_at: float = 0.0) -> List[Dict]:
    """
    Absolute arm movement: move one or both arms to `angle`.
    """
    angle = _clamp(angle, ARM_MIN, ARM_MAX)
    duration = _base_duration(speed, base=0.6)

    joints = _side_to_joint(side)
    pose = {joint: float(angle) for joint in joints}

    return [
        {
            "at": float(start_at),
            "pose": pose,
            "duration": float(duration),
        }
    ]

# ---------------------------------------------------------------------------
# 9. ArmPulse(side, amplitude, speed)
#    Short up-down pulse around neutral (0°).
# ---------------------------------------------------------------------------

def ArmPulse(side: Side, amplitude: float, speed: Speed, start_at: float = 0.0) -> List[Dict]:
    """
    Pulses the arm(s) up from neutral to `amplitude` and back to 0°.
    """
    stages: List[Dict] = []
    t = float(start_at)
    amplitude = abs(amplitude)
    up_angle = _clamp(amplitude, ARM_MIN, ARM_MAX)
    neutral_angle = 0.0

    joints = _side_to_joint(side)
    seg_duration = _base_duration(speed, base=0.35)

    # neutral -> up
    pose_up = {joint: float(up_angle) for joint in joints}
    stages.append(
        {
            "at": t,
            "pose": pose_up,
            "duration": float(seg_duration),
        }
    )
    t += seg_duration

    # up -> neutral
    pose_neutral = {joint: float(neutral_angle) for joint in joints}
    stages.append(
        {
            "at": t,
            "pose": pose_neutral,
            "duration": float(seg_duration),
        }
    )
    t += seg_duration

    return stages
