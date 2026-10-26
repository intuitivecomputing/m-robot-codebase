#!/usr/bin/env python3
"""ROS 2 Microphone Streamer Node.

Streams microphone audio to a ROS 2 topic using sounddevice.
Publishes Float32MultiArray messages on 'mic_audio' topic.
"""
from typing import Optional

import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.client import Client
import sounddevice as sd

from std_msgs.msg import Float32MultiArray
from m_interfaces.srv import ControlLED


class MicStreamer(Node):
    """Streams live microphone audio to ROS 2 topic."""

    def __init__(self):
        super().__init__('mic_streamer')
        self.publisher_ = self.create_publisher(
            Float32MultiArray, 'mic_audio', 30)
        self.rate = 16000  # 16 kHz
        self.chunk = 1024  # Samples per frame

        # Create LED control client
        self.led_client: Optional[Client] = self.create_client(
            ControlLED, 'control_led'
        )

        self.get_logger().info('Starting microphone stream...')
        self.stream = sd.InputStream(
            samplerate=self.rate,
            channels=2,
            blocksize=self.chunk,
            callback=self.audio_callback
        )
        self.stream.start()

        # Turn on LED when mic streamer starts
        self._turn_led_on()

    def _turn_led_on(self) -> None:
        """Turn LED on via service call."""
        if not self.led_client.wait_for_service(timeout_sec=2.0):
            self.get_logger().warn(
                'LED control service not available - continuing without LED'
            )
            return

        request = ControlLED.Request()
        request.enabled = True
        future = self.led_client.call_async(request)
        future.add_done_callback(self._led_response_callback)

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

    def audio_callback(self, indata, frames, time, status):
        """Process and publish audio chunks."""
        if status:
            self.get_logger().warn(f"Stream status: {status}")
        audio_msg = Float32MultiArray()
        audio_msg.data = indata[:, 0].tolist()
        self.publisher_.publish(audio_msg)

    def destroy_node(self):
        """Clean up audio stream on shutdown."""
        self.stream.stop()
        self.stream.close()
        # Turn off LED when shutting down
        self._turn_led_off()
        super().destroy_node()

    def _turn_led_off(self) -> None:
        """Turn LED off via service call."""
        if not self.led_client.wait_for_service(timeout_sec=1.0):
            return

        request = ControlLED.Request()
        request.enabled = False
        future = self.led_client.call_async(request)


def main(args=None):
    """Main entry point."""
    rclpy.init(args=args)
    node = MicStreamer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutdown request (Ctrl-C).')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()