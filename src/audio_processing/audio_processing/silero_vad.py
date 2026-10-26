#!/usr/bin/env python3
"""ROS 2 Silero VAD Node.

Voice Activity Detection using Silero VAD model.
Subscribes to 'mic_audio' and publishes VAD results to 'vad_result'.
"""
import numpy as np
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, Float32MultiArray

from silero_vad import get_speech_timestamps, load_silero_vad


class SileroVADNode(Node):
    """Voice Activity Detection node using Silero VAD."""

    def __init__(self):
        super().__init__('silero_vad')

        self.subscription = self.create_subscription(
            Float32MultiArray,
            'mic_audio',
            self.audio_callback,
            10
        )
        self.publisher_ = self.create_publisher(Bool, 'vad_result', 10)

        self.model = load_silero_vad()
        self.sample_rate = 16000
        self.min_samples = self.sample_rate  # ~1 second chunks

        self.audio_buffer = []
        self.last_speech_state = None  # Track previous speech state

        self.get_logger().info('Silero VAD node is ready.')

    def audio_callback(self, msg: Float32MultiArray):
        """Process audio chunks and detect speech."""
        self.audio_buffer.extend(msg.data)

        if len(self.audio_buffer) >= self.min_samples:
            audio = np.array(
                self.audio_buffer[:self.min_samples], dtype=np.float32)
            self.audio_buffer = self.audio_buffer[self.min_samples:]

            speech_ts = get_speech_timestamps(
                audio, self.model, sampling_rate=self.sample_rate,
                return_seconds=False)
            speech_detected = len(speech_ts) > 0

            if speech_detected != self.last_speech_state:
                self.get_logger().info(f"Speech detected: {speech_detected}")
                self.last_speech_state = speech_detected

            self.publisher_.publish(Bool(data=speech_detected))


def main(args=None):
    """Main entry point."""
    rclpy.init(args=args)
    node = SileroVADNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutdown request (Ctrl-C).')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()