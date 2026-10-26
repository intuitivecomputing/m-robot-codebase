from typing import List, Dict
import random

# ---------------------------------------------------------------------------
# Timing & utility helpers
# ---------------------------------------------------------------------------

def _clamp(val: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(max_val, val))

# joint limits matching motor controller configuration
HEAD_YAW_MIN, HEAD_YAW_MAX = -90.0, 90.0
HEAD_PITCH_MIN, HEAD_PITCH_MAX = -40.0, 40.0
ARM_MIN, ARM_MAX = -45.0, 135.0
BASE_ROT_MIN, BASE_ROT_MAX = -120.0, 120.0

# ---------------------------------------------------------------------------
# 1. beat - Forward/downward arm pulse
# ---------------------------------------------------------------------------

def beat(start_at: float = 0.0) -> List[Dict]:
    """
    Beat gesture: forward/downward pulse from neutral (0° → 60° → 0°).
    Randomly chooses left or right arm and 1-2 pulses.
    Duration: ~0.8–1.6 s.
    """
    stages: List[Dict] = []
    t = float(start_at)
    
    # Randomly choose arm
    arm = random.choice(["arm_left", "arm_right"])
    
    # Randomly choose 1 or 2 pulses
    num_pulses = random.randint(1, 2)
    
    # Pulse parameters
    neutral_angle = 0.0
    pulse_angle = _clamp(60.0, ARM_MIN, ARM_MAX)
    seg_duration = 0.5  # Each segment is 0.5s, so 1 pulse = 1.0s, 2 pulses = 2.0s
    
    for _ in range(num_pulses):
        # neutral -> forward
        stages.append({
            "at": t,
            "pose": {arm: float(pulse_angle)},
            "duration": float(seg_duration),
        })
        t += seg_duration
        
        # forward -> neutral
        stages.append({
            "at": t,
            "pose": {arm: float(neutral_angle)},
            "duration": float(seg_duration),
        })
        t += seg_duration
    
    return stages

# ---------------------------------------------------------------------------
# 2. open_encourage - Both arms open outward
# ---------------------------------------------------------------------------

def open_encourage(start_at: float = 0.0) -> List[Dict]:
    """
    Open encourage gesture: both arms open outward to ~90–110°, hold, then back.
    Duration: ~1.2–1.8 s.
    """
    stages: List[Dict] = []
    t = float(start_at)
    
    neutral_angle = 0.0
    # Random angle between 90-110
    open_angle = _clamp(random.uniform(90.0, 110.0), ARM_MIN, ARM_MAX)
    
    move_duration = 1.0
    hold_duration = random.uniform(0.4, 0.6)  # Variable hold time
    
    # neutral -> open
    stages.append({
        "at": t,
        "pose": {"arm_left": float(open_angle), "arm_right": float(open_angle)},
        "duration": float(move_duration),
    })
    t += move_duration
    
    # hold position
    stages.append({
        "at": t,
        "pose": {"arm_left": float(open_angle), "arm_right": float(open_angle)},
        "duration": float(hold_duration),
    })
    t += hold_duration
    
    # open -> neutral
    stages.append({
        "at": t,
        "pose": {"arm_left": float(neutral_angle), "arm_right": float(neutral_angle)},
        "duration": float(move_duration),
    })
    t += move_duration
    
    return stages

# ---------------------------------------------------------------------------
# 3. invite - Single arm palm-up gesture
# ---------------------------------------------------------------------------

def invite(start_at: float = 0.0) -> List[Dict]:
    """
    Invite gesture: palm-facing-up feeling, single arm forward/up to ~40–50°, gentle return.
    Randomly chooses left or right arm.
    Duration: ~0.8–1.4 s.
    """
    stages: List[Dict] = []
    t = float(start_at)
    
    # Randomly choose arm
    arm = random.choice(["arm_left", "arm_right"])
    
    neutral_angle = 0.0
    invite_angle = _clamp(random.uniform(50.0, 60.0), ARM_MIN, ARM_MAX)
    
    move_out_duration = random.uniform(0.6, 0.8)
    move_back_duration = random.uniform(0.7, 1.0)
    
    # neutral -> invite
    stages.append({
        "at": t,
        "pose": {arm: float(invite_angle)},
        "duration": float(move_out_duration),
    })
    t += move_out_duration
    
    # invite -> neutral
    stages.append({
        "at": t,
        "pose": {arm: float(neutral_angle)},
        "duration": float(move_back_duration),
    })
    t += move_back_duration
    
    return stages

# ---------------------------------------------------------------------------
# 4. invite_double - Both arms palm-up gesture
# ---------------------------------------------------------------------------

def invite_double(start_at: float = 0.0) -> List[Dict]:
    """
    Double invite gesture: both arms with palm-facing-up feeling, forward/up to ~40°, gentle return.
    Duration: ~0.8–1.4 s.
    """
    stages: List[Dict] = []
    t = float(start_at)
    
    neutral_angle = 0.0
    invite_angle = _clamp(55.0, ARM_MIN, ARM_MAX)
    
    move_out_duration = random.uniform(0.6, 0.8)
    move_back_duration = random.uniform(0.7, 1.0)
    
    # neutral -> invite
    stages.append({
        "at": t,
        "pose": {"arm_left": float(invite_angle), "arm_right": float(invite_angle)},
        "duration": float(move_out_duration),
    })
    t += move_out_duration
    
    # invite -> neutral
    stages.append({
        "at": t,
        "pose": {"arm_left": float(neutral_angle), "arm_right": float(neutral_angle)},
        "duration": float(move_back_duration),
    })
    t += move_back_duration
    
    return stages

# ---------------------------------------------------------------------------
# 5. point_arm - Extend arm to point
# ---------------------------------------------------------------------------

def point_arm(start_at: float = 0.0) -> List[Dict]:
    """
    Point gesture: extend arm toward ~80–90° to the side and slightly forward.
    Randomly chooses left or right arm.
    Duration: ~0.8–1.2 s.
    """
    stages: List[Dict] = []
    t = float(start_at)
    
    # Randomly choose arm
    arm = random.choice(["arm_left", "arm_right"])
    
    neutral_angle = 0.0
    point_angle = _clamp(random.uniform(80.0, 90.0), ARM_MIN, ARM_MAX)
    
    move_out_duration = random.uniform(0.8, 1.0)
    move_back_duration = random.uniform(0.7, 0.9)
    
    # neutral -> point
    stages.append({
        "at": t,
        "pose": {arm: float(point_angle)},
        "duration": float(move_out_duration),
    })
    t += move_out_duration
    
    # point -> neutral
    stages.append({
        "at": t,
        "pose": {arm: float(neutral_angle)},
        "duration": float(move_back_duration),
    })
    t += move_back_duration
    
    return stages

# ---------------------------------------------------------------------------
# 6. body_shift - Torso rotation shift
# ---------------------------------------------------------------------------

def body_shift(start_at: float = 0.0) -> List[Dict]:
    """
    Body shift: slow rotate torso ~5–10°, hold, then return.
    Duration: 1.5-2.0s.
    """
    stages: List[Dict] = []
    t = float(start_at)
    
    neutral_angle = 0.0
    # Random direction and magnitude
    shift_angle = _clamp(random.uniform(15.0, 25.0) * random.choice([-1, 1]), BASE_ROT_MIN, BASE_ROT_MAX)
    
    move_duration = random.uniform(0.7, 0.9)
    hold_duration = random.uniform(0.5, 0.8)
    return_duration = random.uniform(0.6, 0.8)
    
    # neutral -> shift
    stages.append({
        "at": t,
        "pose": {"base_rotation": float(shift_angle)},
        "duration": float(move_duration),
    })
    t += move_duration
    
    # hold
    stages.append({
        "at": t,
        "pose": {"base_rotation": float(shift_angle)},
        "duration": float(hold_duration),
    })
    t += hold_duration
    
    # shift -> neutral
    stages.append({
        "at": t,
        "pose": {"base_rotation": float(neutral_angle)},
        "duration": float(return_duration),
    })
    t += return_duration
    
    return stages

# ---------------------------------------------------------------------------
# 7. head_tilt - Head tilt plus rotation
# ---------------------------------------------------------------------------

def head_tilt(start_at: float = 0.0) -> List[Dict]:
    """
    Head tilt: combined head tilt and rotation (15-20deg), then return.
    Duration: ~0.8–1.5 s.
    """
    stages: List[Dict] = []
    t = float(start_at)
    
    neutral_yaw = 0.0
    neutral_pitch = 0.0
    
    # Random tilt direction and magnitude
    tilt_yaw = _clamp(random.uniform(15.0, 20.0) * random.choice([-1, 1]), HEAD_YAW_MIN, HEAD_YAW_MAX)
    tilt_pitch = _clamp(random.uniform(10.0, 15.0) * random.choice([-1, 1]), HEAD_PITCH_MIN, HEAD_PITCH_MAX)
    
    move_duration = random.uniform(0.8, 1.0)
    return_duration = random.uniform(0.6, 0.8)
    
    # neutral -> tilt
    stages.append({
        "at": t,
        "pose": {"head_yaw": float(tilt_yaw), "head_pitch": float(tilt_pitch)},
        "duration": float(move_duration),
    })
    t += move_duration
    
    # tilt -> neutral
    stages.append({
        "at": t,
        "pose": {"head_yaw": float(neutral_yaw), "head_pitch": float(neutral_pitch)},
        "duration": float(return_duration),
    })
    t += return_duration
    
    return stages

# ---------------------------------------------------------------------------
# 8. ack_nod - Acknowledgment nod (2 cycles)
# ---------------------------------------------------------------------------

def ack_nod(start_at: float = 0.0) -> List[Dict]:
    """
    Acknowledgment nod: down–up–down (~15–18°), two cycles.
    Duration: ~0.8–1.5 s.
    """
    stages: List[Dict] = []
    t = float(start_at)
    
    neutral_angle = 0.0
    down_angle = _clamp(-random.uniform(15.0, 18.0), HEAD_PITCH_MIN, HEAD_PITCH_MAX)
    
    # 2 cycles, each with down and up
    seg_duration = random.uniform(0.4, 0.6)

    for _ in range(2):
        # neutral -> down
        stages.append({
            "at": t,
            "pose": {"head_pitch": float(down_angle)},
            "duration": float(seg_duration),
        })
        t += seg_duration

        # down -> neutral
        stages.append({
            "at": t,
            "pose": {"head_pitch": float(neutral_angle)},
            "duration": float(seg_duration),
        })
        t += seg_duration

    # Ensure final neutral pose explicitly (avoid any chance of ending non‑neutral)
    last_pose = stages[-1].get("pose", {}) if stages else {}
    last_pitch = float(last_pose.get("head_pitch", neutral_angle))
    if abs(last_pitch - neutral_angle) > 1e-6:
        # small return duration to settle to neutral
        return_dur = float(random.uniform(0.1, 0.25))
        stages.append({
            "at": t,
            "pose": {"head_pitch": float(neutral_angle)},
            "duration": return_dur,
        })
        t += return_dur

    return stages

# ---------------------------------------------------------------------------
# 9. slow_nod - Slow single nod (1 cycle)
# ---------------------------------------------------------------------------

def slow_nod(start_at: float = 0.0) -> List[Dict]:
    """
    Slow nod: down–up–down (~15–18°), one cycle.
    Duration: ~0.8–1.2s.
    """
    stages: List[Dict] = []
    t = float(start_at)
    
    neutral_angle = 0.0
    down_angle = _clamp(-random.uniform(15.0, 18.0), HEAD_PITCH_MIN, HEAD_PITCH_MAX)
    
    # 1 cycle with down and up
    seg_duration = random.uniform(0.8, 1.0)  # Total: 2 segments * 0.8-1.0 = 1.6-2.0s
    
    # neutral -> down
    stages.append({
        "at": t,
        "pose": {"head_pitch": float(down_angle)},
        "duration": float(seg_duration),
    })
    t += seg_duration
    
    # down -> neutral
    stages.append({
        "at": t,
        "pose": {"head_pitch": float(neutral_angle)},
        "duration": float(seg_duration),
    })
    t += seg_duration
    
    return stages

# ---------------------------------------------------------------------------
# 10. ReturnToNeutral - Return all joints to neutral
# ---------------------------------------------------------------------------

def ReturnToNeutral(start_at: float = 0.0) -> List[Dict]:
    """
    Returns all joints to their neutral positions (0 degrees).
    Duration: 1.0s.
    """
    neutral_pose = {
        "head_yaw": 0.0,
        "head_pitch": 0.0,
        "base_rotation": 0.0,
        "arm_left": 0.0,
        "arm_right": 0.0,
    }

    return [
        {
            "at": float(start_at),
            "pose": neutral_pose,
            "duration": 1.0,
        }
    ]
