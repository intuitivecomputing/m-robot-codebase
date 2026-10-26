from __future__ import annotations
from typing import Any, Dict
from .hardware import ServoMotor, _pca     # reuse board instance

class Robot:
    def __init__(self, cfg: Dict[str, Any]):
        self.servos: Dict[str, ServoMotor] = {
            name: ServoMotor(
                channel=spec["channel"],
                robot_range=tuple(spec["range"]),
                offset=spec.get("offset", 0.0),
                flip=spec.get("flip", False),
                servo_range=tuple(spec["servo_range"]) if "servo_range" in spec else None,
                default_angle=spec.get("default", 0.0),
                pulse_range_us=tuple(spec["pulse"]) if "pulse" in spec else (500, 2500),
            )
            for name, spec in cfg.get("motors", {}).items()
        }

    # ───── simple facade – unchanged ─────────────────────────────────────
    def set_motor_angle(self, motor: str, angle: float):
        if motor in self.servos: self.servos[motor].set_angle(angle)
    def get_motor_angle(self, motor: str) -> float:
        return self.servos[motor].get_angle() if motor in self.servos else 0.0
    def snapshot(self): return {m: s.get_angle() for m, s in self.servos.items()}
    def cleanup(self):
        for s in self.servos.values(): s.stop()
        _pca.deinit()
