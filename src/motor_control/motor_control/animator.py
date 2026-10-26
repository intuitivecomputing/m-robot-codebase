from __future__ import annotations
import time, threading
from typing import Dict, List, Optional, Any
from .constants import MIN_STEP_TIME
from .timeline import Timeline
from .robot import Robot
from .easing import EASING, ease_linear

# ───── internal runtime timeline ----------------------------------------
class _ActiveTimeline:
    def __init__(self, timeline: Timeline, *, duration_s: float, start: float,
                 baseline: Dict[str, float], weight=1.0,
                 fade_in=0.0, fade_out=0.0, priority=0):
        self.timeline, self.duration_s, self.start = timeline, duration_s, start
        self.baseline, self.weight = baseline, weight
        self.fade_in, self.fade_out, self.priority = fade_in, fade_out, priority
        self._frames = timeline.motor_frames()

    def progress(self, now: float) -> float:
        return min(1.0, max(0.0, (now - self.start) / self.duration_s))
    def finished(self, now: float) -> bool:
        return now >= self.start + self.duration_s + self.fade_out
    def envelope(self, now: float) -> float:
        w = self.weight
        if self.fade_in>0 and self.start<=now<self.start+self.fade_in:
            w *= (now-self.start)/self.fade_in
        t_end = self.start + self.duration_s
        if self.fade_out>0 and t_end<=now<t_end+self.fade_out:
            w *= 1-(now-t_end)/self.fade_out
        return max(0.0, min(self.weight, w))

    def angles_at(self, now: float) -> Dict[str, float]:
        p = self.progress(now); out: Dict[str, float] = {}
        for m, fr in self._frames.items():
            base = self.baseline.get(m, 0.0); prev_ang = base
            for at, ang, ease, dur in fr:
                if dur == 0:
                    if p < at: break
                    prev_ang = ang; continue
                seg_start, seg_end = at, at+dur
                if p < seg_start: break
                if seg_start <= p <= seg_end:
                    rel = (p - seg_start) / dur
                    fn = EASING.get(ease, ease_linear)
                    out[m] = prev_ang + (ang - prev_ang) * fn(rel); break
                prev_ang = ang
            else:
                out[m] = prev_ang
        return out

# ───── public animator ---------------------------------------------------
class RobotAnimator:
    def __init__(self, robot: Robot):
        self.robot = robot
        self._tls: List[_ActiveTimeline] = []
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def play_timeline(self, timeline: Timeline, *, duration: Optional[float] = None,
                      crossfade: float = 0.3, weight: float = 1.0, priority: int = 0):
        now = time.time()
        duration = duration if duration is not None else timeline.total_seconds
        if duration <= 0: raise ValueError("duration must be positive")
        for tl in self._tls:
            if tl.priority <= priority: tl.fade_out = max(tl.fade_out, crossfade)
        baseline = self.robot.snapshot()
        self._tls.append(_ActiveTimeline(
            timeline, duration_s=duration, start=now, baseline=baseline,
            weight=weight, fade_in=crossfade, priority=priority))
        if not self._thread or not self._thread.is_alive():
            self._stop.clear()
            self._thread = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()

    def _loop(self):
        next_tick = time.time()
        while not self._stop.is_set():
            now = time.time()
            self._tls[:] = [tl for tl in self._tls if not tl.finished(now)]
            if not self._tls: break
            blended: Dict[str,float] = {}; sums: Dict[str,float] = {}
            for tl in self._tls:
                w = tl.envelope(now)
                if w == 0: continue
                for m,a in tl.angles_at(now).items():
                    blended[m] = blended.get(m,0.0)+a*w
                    sums[m]    = sums.get(m,0.0)+w
            for m,a in blended.items():
                self.robot.set_motor_angle(m, a/sums[m])
            next_tick += MIN_STEP_TIME
            time.sleep(max(0.0, next_tick - time.time()))
        self._stop.clear()

    def stop_all(self):
        self._stop.set()
        if self._thread and self._thread.is_alive(): self._thread.join()
        self._tls.clear()
