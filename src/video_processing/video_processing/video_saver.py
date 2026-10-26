#!/usr/bin/env python3
"""ROS 2 node for recording video and audio streams with synchronized muxing.

Implements direct-write architecture:
- Video frames written immediately to OpenCV VideoWriter
- Audio frames streamed directly to WAV file (no buffering)
- Thread-safe via Lock synchronization
- Post-recording: ffmpeg muxes video+audio into MP4
"""

from __future__ import annotations

import os
import shutil
import subprocess
import threading
import wave
from dataclasses import dataclass, fields
from datetime import datetime
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
import rclpy
from cv_bridge import CvBridge
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Float32MultiArray
from std_srvs.srv import SetBool


@dataclass
class VideoSaverConfig:
    """Configuration for video and audio recording."""

    output_directory: str = "/root/m_ws/data"
    video_fps: int = 30
    audio_rate: int = 16000
    video_codec: str = "XVID"  # XVID, MJPG, H264, etc.
    audio_bitrate: int = 128  # kbps for final MP4
    video_bitrate: int = 2000  # kbps for final MP4


class VideoSaver(Node):
    """Node for recording video and audio streams with synchronized direct writes.

    Architecture:
    - image_callback writes frames directly to VideoWriter
    - audio_callback writes frames directly to WAV file
    - Thread-safe via _write_lock
    - Post-recording: ffmpeg muxes video+audio into MP4

    Statistics:
    - Tracks frame drops and audio underruns
    - Logs results at recording stop
    """

    def __init__(self) -> None:
        super().__init__("video_saver")

        # Declare and load configuration
        defaults = VideoSaverConfig()
        for field in fields(VideoSaverConfig):
            self.declare_parameter(field.name, getattr(defaults, field.name))

        self._config = VideoSaverConfig(
            **{
                field.name: self.get_parameter(field.name).value
                for field in fields(VideoSaverConfig)
            }
        )

        # Create output directory
        Path(self._config.output_directory).mkdir(parents=True, exist_ok=True)

        # Services
        self.start_service = self.create_service(
            SetBool, "start_recording", self.start_recording_callback
        )
        self.stop_service = self.create_service(
            SetBool, "stop_recording", self.stop_recording_callback
        )

        # Subscribers
        self.image_sub = self.create_subscription(
            Image, "camera/image_raw", self.image_callback, 10
        )
        self.audio_sub = self.create_subscription(
            Float32MultiArray, "mic_audio", self.audio_callback, 30
        )

        # CV Bridge
        self.bridge = CvBridge()

        # Recording state
        self.recording = False
        self._write_lock = threading.Lock()  # Synchronizes file writes

        # Video writer (created on first frame)
        self._video_writer: Optional[cv2.VideoWriter] = None
        self._video_writer_ready = False

        # Audio file handle (created on recording start)
        self._audio_file: Optional[wave.Wave_write] = None

        # Recording file paths
        self.video_filename = ""
        self.audio_filename = ""
        self.final_filename = ""

        # Recording statistics
        self._frames_written = 0
        self._audio_samples_written = 0
        self._frame_drops = 0
        self._audio_errors = 0

        self.get_logger().info("Video saver node initialized")

    def start_recording_callback(
        self, request: SetBool.Request, response: SetBool.Response
    ) -> SetBool.Response:
        """Start recording via SetBool service."""
        if request.data and not self.recording:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self.video_filename = os.path.join(
                self._config.output_directory, f"temp_video_{timestamp}.avi"
            )
            self.audio_filename = os.path.join(
                self._config.output_directory, f"temp_audio_{timestamp}.wav"
            )
            self.final_filename = os.path.join(
                self._config.output_directory, f"recording_{timestamp}.mp4"
            )

            # Reset statistics
            self._frames_written = 0
            self._audio_samples_written = 0
            self._frame_drops = 0
            self._audio_errors = 0
            self._video_writer = None
            self._video_writer_ready = False

            # Open audio file for streaming writes
            try:
                self._audio_file = wave.open(self.audio_filename, "wb")
                self._audio_file.setnchannels(1)  # Mono
                self._audio_file.setsampwidth(2)  # 16-bit
                self._audio_file.setframerate(self._config.audio_rate)
            except Exception as exc:
                response.success = False
                response.message = f"Failed to open audio file: {exc}"
                self.get_logger().error(f"Failed to open audio file: {exc}")
                return response

            self.recording = True
            response.success = True
            response.message = f"Recording started: {timestamp}"
            self.get_logger().info(f"Recording started to {self.final_filename}")

        elif request.data and self.recording:
            response.success = False
            response.message = "Already recording"
        else:
            response.success = False
            response.message = "Not currently recording"

        return response

    def stop_recording_callback(
        self, request: SetBool.Request, response: SetBool.Response
    ) -> SetBool.Response:
        """Stop recording via SetBool service."""
        if not self.recording:
            response.success = False
            response.message = "Not currently recording"
            return response

        self.recording = False

        # Close writers
        try:
            with self._write_lock:
                if self._video_writer is not None:
                    self._video_writer.release()
                    self._video_writer = None
                    self.get_logger().info("Video writer closed")

                if self._audio_file is not None:
                    self._audio_file.close()
                    self._audio_file = None
                    self.get_logger().info("Audio file closed")
        except Exception as exc:
            self.get_logger().error(f"Error closing writers: {exc}")

        # Log recording statistics
        self.get_logger().info(
            f"Recording stopped. Frames: {self._frames_written}, Audio samples: {self._audio_samples_written}, Frame drops: {self._frame_drops}, Audio errors: {self._audio_errors}"
        )

        # Combine video and audio
        try:
            self._combine_audio_video()
            response.success = True
            response.message = f"Recording saved to {self.final_filename}"
            self.get_logger().info(f"Recording successfully muxed to {self.final_filename}")
        except Exception as exc:
            response.success = False
            response.message = f"Failed to mux recording: {exc}"
            self.get_logger().error(f"Failed to mux recording: {exc}")

        return response

    def image_callback(self, msg: Image) -> None:
        """Write video frames directly to VideoWriter (thread-safe)."""
        if not self.recording:
            return

        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except Exception as exc:
            self.get_logger().error(f"Error converting image: {exc}")
            return

        with self._write_lock:
            try:
                # Lazy-initialize video writer on first frame
                if self._video_writer is None:
                    height, width = cv_image.shape[:2]
                    fourcc = cv2.VideoWriter_fourcc(*self._config.video_codec)
                    self._video_writer = cv2.VideoWriter(
                        self.video_filename,
                        fourcc,
                        self._config.video_fps,
                        (width, height),
                    )
                    if not self._video_writer.isOpened():
                        self.get_logger().error("Failed to open VideoWriter")
                        self._video_writer = None
                        return
                    self._video_writer_ready = True

                if self._video_writer_ready:
                    self._video_writer.write(cv_image)
                    self._frames_written += 1
            except Exception as exc:
                self.get_logger().error(f"Error writing video frame: {exc}")
                self._frame_drops += 1

    def audio_callback(self, msg: Float32MultiArray) -> None:
        """Stream audio frames directly to WAV file (thread-safe)."""
        if not self.recording or self._audio_file is None:
            return

        try:
            audio_data = np.array(msg.data, dtype=np.float32)

            # Clamp and convert float32 to int16
            audio_data = np.clip(audio_data, -1.0, 1.0)
            audio_int16 = (audio_data * 32767).astype(np.int16)

            with self._write_lock:
                self._audio_file.writeframes(audio_int16.tobytes())
                self._audio_samples_written += len(audio_int16)
        except Exception as exc:
            self.get_logger().error(f"Error writing audio: {exc}")
            self._audio_errors += 1

    def _combine_audio_video(self) -> None:
        """Mux video and audio into final MP4 file via ffmpeg.

        Handles three cases:
        1. Both video and audio exist → mux to MP4
        2. Video only → copy to MP4
        3. Neither exist → error

        On success, removes temporary files. On error, preserves them for debugging.
        """
        # Verify files exist
        if not os.path.exists(self.video_filename):
            raise FileNotFoundError(f"Video file not found: {self.video_filename}")

        audio_exists = os.path.exists(self.audio_filename) and os.path.getsize(
            self.audio_filename
        ) > 44  # WAV header is 44 bytes minimum

        try:
            if audio_exists:
                # Both video and audio: encode to MP4 with specified bitrates
                subprocess.run(
                    [
                        "ffmpeg",
                        "-i",
                        self.video_filename,
                        "-i",
                        self.audio_filename,
                        "-c:v",
                        "libx264",
                        "-b:v",
                        f"{self._config.video_bitrate}k",
                        "-c:a",
                        "aac",
                        "-b:a",
                        f"{self._config.audio_bitrate}k",
                        "-shortest",  # End at shortest stream
                        self.final_filename,
                        "-y",  # Overwrite output
                    ],
                    check=True,
                    capture_output=True,
                    timeout=300.0,  # 5 minute timeout
                )
                self.get_logger().info(f"Muxed video+audio to {self.final_filename}")

                # Clean up temp files on success
                os.remove(self.video_filename)
                os.remove(self.audio_filename)
            else:
                # Video only: copy to MP4 container
                subprocess.run(
                    [
                        "ffmpeg",
                        "-i",
                        self.video_filename,
                        "-c",
                        "copy",
                        self.final_filename,
                        "-y",
                    ],
                    check=True,
                    capture_output=True,
                    timeout=60.0,
                )
                self.get_logger().info(f"Copied video-only to {self.final_filename}")
                os.remove(self.video_filename)

                # Remove empty audio file if it exists
                if os.path.exists(self.audio_filename):
                    os.remove(self.audio_filename)

        except subprocess.CalledProcessError as exc:
            raise RuntimeError(
                f"ffmpeg encoding failed (exit code {exc.returncode}): {exc.stderr}"
            ) from exc
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError("ffmpeg encoding timed out after 5 minutes") from exc

    def destroy_node(self) -> None:
        """Clean up resources on node shutdown."""
        self.recording = False

        # Force-close any open files
        try:
            with self._write_lock:
                if self._video_writer is not None:
                    self._video_writer.release()
                    self._video_writer = None

                if self._audio_file is not None:
                    self._audio_file.close()
                    self._audio_file = None
        except Exception as exc:
            self.get_logger().error("Error during shutdown cleanup: %s", exc)

        super().destroy_node()



def main(args: Optional[list[str]] = None) -> None:  # pragma: no cover
    """Main entry point for video saver node."""
    rclpy.init(args=args)
    node = VideoSaver()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    finally:
        executor.remove_node(node)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":  # pragma: no cover
    main()
