#!/usr/bin/env python3
"""ROS 2 Audio Playback Action Server (renovated).

Implements a non‑blocking `AudioPlay` action server that streams WAV data to the
system audio device while publishing smooth progress feedback and supporting
clean cancel / pre‑empt semantics.

Public interface
----------------
Action:  m_interfaces/AudioPlay
Goal:    bytes  data   # raw WAV file bytes
Result:  int8   result_code # 0 = success, 1 = canceled, 2 = error
Feedback float32 progress   # 0 ‑ 100 [%]

Parameters
----------
feedback_rate_hz  (double, default 4.0)  – How often to publish feedback.
volume            (double, default 1.0)  – Linear gain applied before playback.
device_name       (string, default "default") – Simpleaudio device name.
"""

import io
import os
import threading
import time
from typing import Optional

# Configure ALSA to use ReSpeaker Lite (card 2, device 0)
# ReSpeaker Lite only supports: 16kHz, 16-bit, stereo
os.environ["ALSA_PCM_DEVICE"] = "0"
os.environ["ALSA_PCM_CARD"] = "2"

import rclpy
from rclpy.action import (
    ActionServer,
    CancelResponse,
    GoalResponse,
)
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from action_msgs.msg import GoalStatus

# Replace this import with the correct generated package for your project.
# If your action package name is e.g. `audio_interfaces`, change accordingly.
from m_interfaces.action import AudioPlay  # type: ignore

from pydub import AudioSegment
import simpleaudio as sa


class AudioPlaybackServer(Node):
    """Non‑blocking AudioPlay Action Server."""

    def __init__(self) -> None:
        super().__init__("audio_playback_action", automatically_declare_parameters_from_overrides=True)

        # Declare parameters with defaults.
        self.declare_parameter("feedback_rate_hz", 4.0)
        self.declare_parameter("volume", 1.0)
        self.declare_parameter("device_name", "default")

        # Re‑entrant callback group so timer + action callbacks can interleave.
        self._cb_group = ReentrantCallbackGroup()

        self._action_server = ActionServer(
            self,
            AudioPlay,
            "audio_play",
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            callback_group=self._cb_group,
        )

        self._active_goal_handle: Optional[rclpy.action.server.ServerGoalHandle] = None
        self._playback_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        self.get_logger().info("AudioPlaybackServer initialised.")

    # --------------------------------------------------------------------- #
    #                         Action Server callbacks                       #
    # --------------------------------------------------------------------- #

    def goal_callback(self, goal_request: AudioPlay.Goal) -> int:
        """Accept or reject an incoming goal.

        Reject if another goal is currently executing.
        """
        if self._active_goal_handle is not None and self._active_goal_handle.status == GoalStatus.STATUS_EXECUTING:
            self.get_logger().warn("Rejecting goal – another goal is active.")
            return GoalResponse.REJECT

        self.get_logger().info("Accepted new goal ({} bytes)".format(len(goal_request.data)))
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle: rclpy.action.server.ServerGoalHandle) -> int:
        """Handle a cancel request from a client."""
        self.get_logger().info("Cancel request received.")
        # Signal playback thread to stop.
        self._stop_event.set()
        return CancelResponse.ACCEPT

    def execute_callback(self, goal_handle: rclpy.action.server.ServerGoalHandle) -> AudioPlay.Result:
        """Main execution thread for a goal.

        Runs in its own thread thanks to ActionServer's internal executor.
        """
        self._active_goal_handle = goal_handle
        self._stop_event.clear()

        wav_bytes = goal_handle.request.data
        volume = float(self.get_parameter("volume").value)
        feedback_period = 1.0 / float(self.get_parameter("feedback_rate_hz").value)

        # ---------------------------------------------------------------- #
        # Decode WAV bytes with pydub.
        # ---------------------------------------------------------------- #
        try:
            audio_seg = AudioSegment.from_file(io.BytesIO(wav_bytes), format="wav")
            if volume != 1.0:
                audio_seg += 20 * (volume - 1.0)  # Rough linear gain adjustment.
        except Exception as exc:  # pylint: disable=broad-except
            self.get_logger().error(f"Failed to parse WAV: {exc}")
            goal_handle.abort()
            return AudioPlay.Result(result_code=2)

        # ---------------------------------------------------------------- #
        # Normalize audio format for ReSpeaker Lite (16kHz, 16-bit, stereo)
        # ---------------------------------------------------------------- #
        try:
            # Convert to ReSpeaker Lite compatible format
            audio_seg = audio_seg.set_frame_rate(16000).set_sample_width(2).set_channels(2)
        except Exception as exc:  # pylint: disable=broad-except
            self.get_logger().error(f"Failed to normalize audio format: {exc}")
            goal_handle.abort()
            return AudioPlay.Result(result_code=2)

        duration_s = audio_seg.duration_seconds

        # Start audio playback.
        try:
            play_obj = sa.play_buffer(
                audio_seg.raw_data,
                num_channels=audio_seg.channels,
                bytes_per_sample=audio_seg.sample_width,
                sample_rate=audio_seg.frame_rate,
            )
        except Exception as exc:  # pylint: disable=broad-except
            self.get_logger().error(f"Failed to start audio playback: {exc}")
            goal_handle.abort()
            return AudioPlay.Result(result_code=2)

        # ---------------------------------------------------------------- #
        # Feedback publishing loop.
        # ---------------------------------------------------------------- #
        start_t = time.perf_counter()
        last_feedback_t = 0.0

        result_code: int = 0  # Assume success.
        try:
            while play_obj.is_playing():
                now_t = time.perf_counter()

                # Check for cancel request.
                if goal_handle.is_cancel_requested:
                    self.get_logger().info("Goal canceled by client.")
                    self._stop_event.set()
                    play_obj.stop()
                    goal_handle.canceled()
                    result_code = 1
                    break

                # Publish feedback at requested rate.
                if now_t - last_feedback_t >= feedback_period:
                    elapsed_s = now_t - start_t
                    progress = min(100.0, (elapsed_s / duration_s) * 100.0)
                    feedback_msg = AudioPlay.Feedback(progress=progress)
                    goal_handle.publish_feedback(feedback_msg)
                    last_feedback_t = now_t

                # Respect stop_event set by cancel_callback.
                if self._stop_event.is_set():
                    play_obj.stop()

                time.sleep(0.01)  # Small sleep to avoid busy‑wait.

            # Playback naturally finished.
            if result_code == 0 and not goal_handle.is_cancel_requested:
                goal_handle.publish_feedback(AudioPlay.Feedback(progress=100.0))
                goal_handle.succeed()

        except Exception as exc:  # pylint: disable=broad-except
            self.get_logger().error(f"Playback error: {exc}")
            play_obj.stop()
            goal_handle.abort()
            result_code = 2

        finally:
            self._active_goal_handle = None

        return AudioPlay.Result(result_code=result_code)

    # --------------------------------------------------------------------- #
    #                          Shutdown handling                            #
    # --------------------------------------------------------------------- #

    def destroy_node(self) -> None:  # noqa: D401
        """Cleanup resources on node shutdown."""
        self._stop_event.set()
        super().destroy_node()


def main() -> None:
    rclpy.init()
    node = AudioPlaybackServer()

    # MultiThreadedExecutor allows timers / service calls during execute_callback.
    executor = MultiThreadedExecutor()
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        node.get_logger().info("Shutdown request (Ctrl‑C).")

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":  # pragma: no cover
    main()
