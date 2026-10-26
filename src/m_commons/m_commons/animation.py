"""Animation scheduling utilities for ROS nodes."""

from __future__ import annotations

import json
from typing import Callable, Dict, List, Optional

from rclpy.callback_groups import CallbackGroup
from rclpy.node import Node
from rclpy.timer import Timer
from rclpy.task import Future
from std_msgs.msg import String

from m_interfaces.srv import SetPose

from .story_models import AnimationCue, BodyTimeline


class AnimationScheduler:
    """Schedule facial expressions and body poses using ROS primitives."""

    def __init__(self, node: Node, callback_group: CallbackGroup | None = None) -> None:
        self._node = node
        self._callback_group = callback_group or node.default_callback_group
        self._face_pub = node.create_publisher(String, "face_expression", 10)
        self._pose_cli = node.create_client(SetPose, "set_pose")
        self._active_timers: List[Timer] = []
        self._pose_futures: List[Future] = []

    def clear(self) -> None:
        """Cancel all scheduled animations without resetting the robot pose."""

        for timer in list(self._active_timers):
            timer.cancel()
        self._active_timers.clear()

    def reset_to_neutral(self) -> None:
        """Reset the face expression and send the neutral body pose."""

        self.clear()
        self._reset_face()
        self._reset_body()

    def _reset_face(self) -> None:
        """Reset the face expression to neutral."""
        self._face_pub.publish(String(data="reset"))

    def _reset_body(self) -> None:
        """Send the neutral body pose."""

        self.clear()
        neutral_pose = {
            "base_rotation": 0.0,
            "head_pitch": 0.0,
            "arm_left": 0.0,
            "arm_right": 0.0,
            "head_yaw": 0.0,
        }
        self._send_pose(neutral_pose, duration=1.0)

    def schedule_face_program(self, cue: AnimationCue) -> None:
        """Schedule a face program to run after ``cue.delay`` seconds."""

        self._create_oneshot_timer(cue.delay, lambda: self._publish_face_program(cue.program_json))

    def schedule_body_timeline(self, timeline: BodyTimeline) -> None:
        """Schedule execution of a body timeline."""

        try:
            parsed = json.loads(timeline.timeline_json)
        except json.JSONDecodeError as exc:
            self._node.get_logger().error(f"Invalid body timeline JSON: {exc}")
            return

        for entry in parsed:
            if not isinstance(entry, dict):
                continue
            pose = entry.get("pose", {})
            if not pose:
                continue
            duration = float(entry.get("duration", 1.0))
            offset = float(entry.get("at", 0.0))
            delay = max(0.0, timeline.delay + offset)
            self._create_oneshot_timer(delay, lambda p=pose, d=duration: self._send_pose(p, d))

    def shutdown(self) -> None:
        """Cancel timers and drop outstanding references."""

        self.clear()
        self._pose_futures.clear()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _create_oneshot_timer(self, delay: float, callback: Callable[[], None]) -> None:
        timer_ref: Timer | None = None

        def wrapper() -> None:
            try:
                callback()
            finally:
                if timer_ref is not None:
                    timer_ref.cancel()
                    if timer_ref in self._active_timers:
                        self._active_timers.remove(timer_ref)

        timer_ref = self._node.create_timer(delay, wrapper, callback_group=self._callback_group)
        self._active_timers.append(timer_ref)

    def _publish_face_program(self, program_json: str) -> None:
        try:
            payload = json.loads(program_json)
            program = payload.get("program", "") if isinstance(payload, dict) else ""
        except json.JSONDecodeError:
            program = ""
        if program:
            self._face_pub.publish(String(data=f"exec:{program}"))
        else:
            self._face_pub.publish(String(data="reset"))

    def _send_pose(self, joints: Dict[str, float], duration: float) -> None:
        if not joints:
            return
        if not self._pose_cli.wait_for_service(timeout_sec=1.0):
            self._node.get_logger().warning("set_pose service unavailable; skipping pose command")
            return
        request = SetPose.Request()
        request.joint_names = list(joints.keys())
        request.joint_angles = [float(value) for value in joints.values()]
        request.duration = float(duration)
        future = self._pose_cli.call_async(request)
        self._pose_futures.append(future)
