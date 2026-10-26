"""Autonomous story delivery node built on standard ROS 2 patterns."""

from __future__ import annotations

import base64
import io
import json
from collections import deque
from dataclasses import dataclass, fields
from enum import Enum, auto
from typing import Deque, get_type_hints, Iterable, List, Optional, Sequence

import rclpy
from pydub import AudioSegment
from rclpy.action import ActionClient
from rclpy.duration import Duration
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from std_msgs.msg import Bool

from m_interfaces.action import AudioPlay

from m_commons.animation import AnimationScheduler
from m_commons.configuration import ConfigurationError, StoryManagerConfig
from m_commons.story_models import AnimationCue, BodyTimeline, NarrativeChunk, StoryDocument


def _decode_audio_to_wav(audio_b64: str) -> bytes:
    try:
        raw_bytes = base64.b64decode(audio_b64.split(",")[-1])
        audio = AudioSegment.from_file(io.BytesIO(raw_bytes), format="mp3")
        buffer = io.BytesIO()
        audio.export(buffer, format="wav")
        return buffer.getvalue()
    except Exception as exc:
        raise ValueError(f"Failed to decode audio: {exc}")


@dataclass(frozen=True)
class StoryDeliveryConfig:
    """Configuration controlling the autonomous delivery loop."""

    story_filename: str
    start_delay: float
    cooldown_seconds: float
    loop_story: bool


class DeliveryState(Enum):
    """Lifecycle states for the autonomous delivery loop."""

    WAITING_START = auto()
    STARTING_NEXT = auto()
    WAITING_AUDIO = auto()
    COOLDOWN = auto()
    FINISHED = auto()


class StoryDelivery(Node):
    """Deliver a story automatically on node startup."""

    def __init__(self) -> None:
        super().__init__("story_delivery")

        # Load base configuration using from_node
        self._manager_config = StoryManagerConfig.from_node(self)

        # Declare parameters with defaults from StoryDeliveryConfig
        defaults = StoryDeliveryConfig(
            story_filename=self._manager_config.default_story,
            start_delay=1.0,
            cooldown_seconds=1.0,
            loop_story=False,
        )
        for field in fields(StoryDeliveryConfig):
            self.declare_parameter(field.name, getattr(defaults, field.name))

        # Initialize StoryDeliveryConfig using declared parameters
        self._config = StoryDeliveryConfig(
            **{
                field.name: self.get_parameter(field.name).value
                for field in fields(StoryDeliveryConfig)
            }
        )

        self.pub_speaking = self.create_publisher(Bool, "robot_speaking", 10)

        self._story_template = self._load_story_chunks()
        self._story_queue: Deque[NarrativeChunk] = deque(self._story_template)

        self._animation = AnimationScheduler(self)
        self._audio_client = ActionClient(self, AudioPlay, "audio_play")

        self._cooldown_deadline: Optional[rclpy.time.Time] = None
        self._next_start_time: Optional[rclpy.time.Time] = None
        if self._story_queue:
            self._state = DeliveryState.WAITING_START
            self._next_start_time = self.get_clock().now() + Duration(seconds=self._config.start_delay)
            self.get_logger().info(
                "Story ready (%d chunks); starting in %.2f seconds" % (
                    len(self._story_queue),
                    self._config.start_delay,
                )
            )
        else:
            self._state = DeliveryState.FINISHED
            self.get_logger().error("No narrative chunks available; story delivery is idle")

        self._timer = self.create_timer(0.1, self._on_timer_tick)

    # ------------------------------------------------------------------
    # Story loading
    # ------------------------------------------------------------------
    def _load_story_chunks(self) -> List[NarrativeChunk]:
        try:
            story_path = self._manager_config.resolve_story_path(self._config.story_filename)
        except ConfigurationError as exc:
            self.get_logger().error(f"Unable to resolve story file '{self._config.story_filename}': {exc}")
            return []

        try:
            with story_path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            self.get_logger().error(f"Failed to load story '{story_path}': {exc}")
            return []

        chunks: List[NarrativeChunk] = []

        if isinstance(payload, dict):
            document = StoryDocument.from_dict(payload)
            for chunk in document.chunks:
                if isinstance(chunk, NarrativeChunk):
                    chunks.append(chunk)
                else:
                    self.get_logger().debug("Skipping non-narrative chunk in story document")
        else:
            self.get_logger().error(f"Unrecognised story payload format: {type(payload)}")

        return chunks

    def _parse_programs(self, items: Iterable[object]) -> List[AnimationCue]:
        programs: List[AnimationCue] = []
        for entry in items:
            if not isinstance(entry, (list, tuple)) or len(entry) != 2:
                continue
            program, delay = entry
            try:
                programs.append(AnimationCue(str(program), float(delay)))
            except (TypeError, ValueError):
                continue
        return programs

    def _parse_timelines(self, items: Iterable[object]) -> List[BodyTimeline]:
        timelines: List[BodyTimeline] = []
        for entry in items:
            if not isinstance(entry, (list, tuple)) or len(entry) != 2:
                continue
            timeline, delay = entry
            try:
                timelines.append(BodyTimeline(str(timeline), float(delay)))
            except (TypeError, ValueError):
                continue
        return timelines

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------
    def _on_timer_tick(self) -> None:
        now = self.get_clock().now()

        if self._state == DeliveryState.WAITING_START:
            if self._next_start_time is None or now >= self._next_start_time:
                self._state = DeliveryState.STARTING_NEXT
                self._start_next_chunk()
            return

        if self._state == DeliveryState.STARTING_NEXT:
            self._start_next_chunk()
            return

        if self._state == DeliveryState.COOLDOWN:
            if self._cooldown_deadline and now >= self._cooldown_deadline:
                self._state = DeliveryState.STARTING_NEXT
                self._cooldown_deadline = None
            return

    def _start_next_chunk(self) -> None:
        if not self._story_queue:
            self._finish_story()
            return

        chunk = self._story_queue.popleft()
        self._animation.clear()

        self.get_logger().info(f"Audio story payload: {chunk.audio_b64[:20]}")

        for cue in chunk.face_programs:
            self._animation.schedule_face_program(cue)
        for timeline in chunk.body_programs:
            self._animation.schedule_body_timeline(timeline)

        if chunk.content:
            self.get_logger().info(f"Narrative: {chunk.content[:120]}")

        if not chunk.audio_b64:
            self.pub_speaking.publish(Bool(data=False))
            self._enter_cooldown()
            return
    
        try:
            wav_bytes = _decode_audio_to_wav(chunk.audio_b64)
        except Exception as exc:  # noqa: BLE001 - propagate decoding issues to logs
            self.get_logger().error(f"Failed to decode audio: {exc}")
            self.pub_speaking.publish(Bool(data=False))
            self._enter_cooldown()
            return

        goal = AudioPlay.Goal()
        goal.data = wav_bytes

        self.pub_speaking.publish(Bool(data=True))
        send_future = self._audio_client.send_goal_async(goal)
        send_future.add_done_callback(self._on_audio_goal_response)
        self._state = DeliveryState.WAITING_AUDIO

    def _on_audio_goal_response(self, future) -> None:
        try:
            goal_handle = future.result()
        except Exception as exc:  # noqa: BLE001
            self.get_logger().error(f"Audio goal failed: {exc}")
            self.pub_speaking.publish(Bool(data=False))
            self._enter_cooldown()
            return

        if not goal_handle.accepted:
            self.get_logger().error("Audio goal rejected")
            self.pub_speaking.publish(Bool(data=False))
            self._enter_cooldown()
            return

        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self._on_audio_completed)

    def _on_audio_completed(self, future) -> None:
        try:
            future.result()
        except Exception as exc:  # noqa: BLE001
            self.get_logger().error(f"Audio playback failed: {exc}")
        finally:
            self.pub_speaking.publish(Bool(data=False))
            self._enter_cooldown()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _enter_cooldown(self) -> None:
        self._animation.reset_to_neutral()
        self._cooldown_deadline = self.get_clock().now() + Duration(seconds=self._config.cooldown_seconds)
        self._state = DeliveryState.COOLDOWN

    def _finish_story(self) -> None:
        self._animation.reset_to_neutral()
        self.pub_speaking.publish(Bool(data=False))

        if self._config.loop_story and self._story_template:
            self.get_logger().info("Story finished; restarting after %.2f seconds", self._config.start_delay)
            self._story_queue = deque(self._story_template)
            self._state = DeliveryState.WAITING_START
            self._next_start_time = self.get_clock().now() + Duration(seconds=self._config.start_delay)
        else:
            self.get_logger().info("Story delivery completed")
            self._state = DeliveryState.FINISHED

    def destroy_node(self) -> bool:
        self._animation.shutdown()
        return super().destroy_node()


def main(args: Optional[Sequence[str]] = None) -> None:
    rclpy.init(args=args)
    node = StoryDelivery()
    executor = MultiThreadedExecutor()
    executor.add_node(node)

    try:
        executor.spin()
    finally:
        executor.remove_node(node)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
