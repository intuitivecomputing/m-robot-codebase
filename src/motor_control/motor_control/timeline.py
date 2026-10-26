from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Any

class Keyframe:
    def __init__(self, at: float, targets: Dict[str, float], *, easing=None, duration=0.0):
        self.at, self.targets, self.easing = at, targets, easing
        self.duration = max(0.0, duration)

class Timeline:
    def __init__(self, total_seconds: float = 1.0):
        self.total_seconds = total_seconds
        self.keyframes: List[Keyframe] = []

    # ---------- original helpers (verbatim) ------------------------------
    @classmethod
    def from_script(cls, frames: List[Dict[str, Any]]):
        use_abs = any(
            (isinstance(f.get("at"), (int, float)) and f["at"] > 1)
            or "duration" in f or "end_time" in f for f in frames
        )
        length = 1.0
        if use_abs:
            length = 0.0
            for f in frames:
                at = float(f["at"]); span = float(f.get("duration", 0.0))
                if "end_time" in f: span = float(f["end_time"]) - at
                length = max(length, at + span)
            if length <= 0: length = 1.0
        tl = cls(total_seconds=length)
        for f in frames:
            at_abs = float(f["at"])
            span_abs = float(f.get("duration", 0.0))
            if "end_time" in f: span_abs = float(f["end_time"]) - at_abs
            if span_abs < 0: raise ValueError("end_time before at")
            at_n  = at_abs / tl.total_seconds if use_abs else at_abs
            dur_n = span_abs / tl.total_seconds if use_abs else span_abs
            tl.add_keyframe(at=at_n, pose=f["pose"], easing=f.get("easing"), duration=dur_n)
        return tl

    def add_keyframe(self, *, at: float, pose: Dict[str, float], easing=None, duration=0.0):
        self.keyframes.append(Keyframe(at, pose, easing=easing, duration=duration))
        self.keyframes.sort(key=lambda k: k.at)

    def motor_frames(self):
        buckets: Dict[str, List[Tuple[float, float, Optional[Any], float]]] = {}
        for k in self.keyframes:
            for m, ang in k.targets.items():
                # Default to "easeInOutSine" if no easing is specified
                ease = k.easing.get(m) if isinstance(k.easing, dict) else k.easing
                if ease is None:
                    ease = "easeInOutSine"
                buckets.setdefault(m, []).append((k.at, ang, ease, k.duration))
        for lst in buckets.values(): lst.sort(key=lambda x: x[0])
        return buckets
