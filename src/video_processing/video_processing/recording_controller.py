#!/usr/bin/env python3
"""CLI controller for video recording via ROS 2 services."""

from __future__ import annotations

import sys
from typing import Optional

import rclpy
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from std_srvs.srv import SetBool


class RecordingController(Node):
    """Client node for controlling video recording via SetBool services."""

    def __init__(self) -> None:
        super().__init__("recording_controller")
        self.start_client = self.create_client(SetBool, "start_recording")
        self.stop_client = self.create_client(SetBool, "stop_recording")

    def start_recording(self) -> Optional[bool]:
        """Request recording to start."""
        while not self.start_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Start recording service not available, waiting...")

        request = SetBool.Request()
        request.data = True
        future = self.start_client.call_async(request)
        return future.result(timeout_sec=5.0).success

    def stop_recording(self) -> Optional[bool]:
        """Request recording to stop."""
        while not self.stop_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Stop recording service not available, waiting...")

        request = SetBool.Request()
        request.data = False
        future = self.stop_client.call_async(request)
        return future.result(timeout_sec=5.0).success


def main(args: Optional[list[str]] = None) -> None:  # pragma: no cover
    """CLI entry point for recording control."""
    rclpy.init(args=args)
    controller = RecordingController()

    if len(sys.argv) < 2:
        print("Usage: python3 recording_controller.py [start|stop]")
        controller.destroy_node()
        rclpy.shutdown()
        return

    command = sys.argv[1].lower()

    try:
        if command == "start":
            controller.get_logger().info("Requesting recording start...")
            success = controller.start_recording()
            print(f"Recording started: {success}")
        elif command == "stop":
            controller.get_logger().info("Requesting recording stop...")
            success = controller.stop_recording()
            print(f"Recording stopped: {success}")
        else:
            print(f"Invalid command '{command}'. Use 'start' or 'stop'")
    except Exception as exc:  # pragma: no cover
        controller.get_logger().error("Error: %s", exc)
    finally:
        controller.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":  # pragma: no cover
    main()
