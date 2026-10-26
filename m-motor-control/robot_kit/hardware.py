from __future__ import annotations
import time
from typing import Optional, Tuple
import busio, board 
from adafruit_pca9685 import PCA9685

from .constants import MIN_STEP_TIME, ANGLE_EPS

# ───── low-level PWM board setup ──────────────────────────────────────────
_i2c = busio.I2C(board.SCL, board.SDA)
_pca = PCA9685(_i2c)
_pca.frequency = 250                         # Hz

def _pulse_to_duty(pulse_us: float) -> int:
    return int(pulse_us * 65535 / (1_000_000 / _pca.frequency))

class ServoMotor:
    """One PWM hobby servo with offset, flip & range guarding."""
    def __init__(
        self, channel: int, robot_range: Tuple[float, float], *,
        offset: float = 0.0, flip: bool = False,
        servo_range: Optional[Tuple[float, float]] = None,
        default_angle: float = 0.0,
        pulse_range_us: Tuple[int, int] = (500, 2500),
    ) -> None:
        self.channel = channel
        self.robot_min, self.robot_max = robot_range
        self.offset, self.flip = offset, flip
        if servo_range is None:
            lo = offset - self.robot_max if flip else offset + self.robot_min
            hi = offset - self.robot_min if flip else offset + self.robot_max
        else:
            lo, hi = servo_range
        if lo > hi: lo, hi = hi, lo
        self.servo_min, self.servo_max = lo, hi
        self.min_pulse, self.max_pulse = pulse_range_us
        self.current_coord: Optional[float] = None
        self._last_update = 0.0
        self.set_angle(default_angle, force=True)

    # ───── helpers – unchanged ────────────────────────────────────────────
    def _robot_to_servo(self, angle: float) -> float:
        return (self.offset - angle) if self.flip else (self.offset + angle)
    def _servo_to_duty(self, s_angle: float) -> int:
        pulse = self.min_pulse + (s_angle - self.servo_min) / (
            self.servo_max - self.servo_min) * (self.max_pulse - self.min_pulse)
        return _pulse_to_duty(pulse)

    def set_angle(self, robot_angle: float, *, force: bool = False):
        robot_angle = max(self.robot_min, min(self.robot_max, robot_angle))
        now = time.time()
        if not force and self.current_coord is not None:
            if abs(robot_angle - self.current_coord) < ANGLE_EPS: return
            if now - self._last_update < MIN_STEP_TIME:          return
        raw = max(self.servo_min, min(self.servo_max, self._robot_to_servo(robot_angle)))
        _pca.channels[self.channel].duty_cycle = self._servo_to_duty(raw)
        self.current_coord, self._last_update = robot_angle, now

    def get_angle(self) -> float:
        return self.current_coord if self.current_coord is not None else 0.0
    def stop(self): _pca.channels[self.channel].duty_cycle = 0
