"""Camera streamer node using OpenCV video capture."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Optional

import cv2
import numpy as np
import rclpy
from cv_bridge import CvBridge
from rclpy.client import Client
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from sensor_msgs.msg import Image
from m_interfaces.srv import ControlLED


@dataclass
class CameraConfig:
    """Configuration for camera capture and streaming."""

    device_path: str = "/dev/video10"
    width: int = 640
    height: int = 480
    fps: int = 30
    fourcc: str = "YUYV"


class CameraStreamer(Node):
    """Stream camera frames via ROS 2 Image topic."""

    def __init__(self) -> None:
        super().__init__("camera_streamer")

        # Declare parameters from dataclass fields
        defaults = CameraConfig()
        for field in fields(CameraConfig):
            default_value = getattr(defaults, field.name)
            self.declare_parameter(field.name, default_value)

        self._config = CameraConfig(
            **{
                field.name: self.get_parameter(field.name).value
                for field in fields(CameraConfig)
            }
        )

        self._bridge = CvBridge()
        self._cap: Optional[cv2.VideoCapture] = None
        self._led_client: Optional[Client] = self.create_client(
            ControlLED, 'control_led'
        )

        # Initialize camera
        try:
            self._cap = cv2.VideoCapture(self._config.device_path, cv2.CAP_V4L2)
            if not self._cap.isOpened():
                raise RuntimeError(f"Failed to open camera at {self._config.device_path}")

            # Set resolution
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._config.width)
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._config.height)

            # Set frame format (FOURCC)
            fourcc_int = cv2.VideoWriter_fourcc(*self._config.fourcc)
            self._cap.set(cv2.CAP_PROP_FOURCC, fourcc_int)

            # Set FPS
            self._cap.set(cv2.CAP_PROP_FPS, self._config.fps)

            self.get_logger().info(
                f"Camera initialized (device={self._config.device_path}, {self._config.width}x{self._config.height}@{self._config.fps}Hz, format={self._config.fourcc})"
            )
        except Exception as exc:  # pragma: no cover
            self.get_logger().error(f"Failed to initialize camera: {exc}")
            raise

        self._publisher = self.create_publisher(Image, "camera/image_raw", 10)

        # Create timer for frame capture loop
        frame_period = 1.0 / max(self._config.fps, 1)
        self._timer = self.create_timer(frame_period, self._capture_and_publish)

        # Turn on LED when camera streamer starts
        self._turn_led_on()

    def _capture_and_publish(self) -> None:
        """Capture frame from camera and publish as Image message."""
        if self._cap is None:
            self.get_logger().error("Camera not initialized")
            return

        ok, frame = self._cap.read()
        if not ok:
            self.get_logger().error("Failed to capture frame")
            return

        try:
            msg = self._bridge.cv2_to_imgmsg(frame, encoding="bgr8")
            self._publisher.publish(msg)
        except Exception as exc:  # pragma: no cover
            self.get_logger().error(f"Failed to publish frame: {exc}")

    def destroy_node(self) -> bool:
        """Clean up camera resources."""
        if self._cap is not None:
            self._cap.release()
        # Turn off LED when shutting down
        self._turn_led_off()
        return super().destroy_node()

    def _turn_led_on(self) -> None:
        """Turn LED on via service call."""
        if not self._led_client.wait_for_service(timeout_sec=2.0):
            self.get_logger().warn(
                'LED control service not available - continuing without LED'
            )
            return

        request = ControlLED.Request()
        request.enabled = True
        future = self._led_client.call_async(request)
        future.add_done_callback(self._led_response_callback)

    def _turn_led_off(self) -> None:
        """Turn LED off via service call."""
        if not self._led_client.wait_for_service(timeout_sec=1.0):
            return

        request = ControlLED.Request()
        request.enabled = False
        self._led_client.call_async(request)

    def _led_response_callback(self, future) -> None:
        """Handle LED control response."""
        try:
            response = future.result()
            if response.success:
                self.get_logger().info('LED turned on successfully')
            else:
                self.get_logger().warn(f'LED control failed: {response.message}')
        except Exception as e:
            self.get_logger().warn(f'Failed to turn on LED: {e}')


def main(args: Optional[list[str]] = None) -> None:  # pragma: no cover - thin wrapper
    rclpy.init(args=args)
    node = CameraStreamer()
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
