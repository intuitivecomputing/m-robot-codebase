#!/usr/bin/env python3
"""ROS 2 Audio Saver Node.

Saves audio segments to WAV files based on VAD detection.
Subscribes to mic_audio and vad_result topics.
"""
import time
import wave
from pathlib import Path

import numpy as np
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, Float32MultiArray


class AudioSaverNode(Node):
    """Saves audio segments to WAV files when speech is detected."""

    def __init__(self):
        super().__init__('audio_saver_node')

        self.sub_audio = self.create_subscription(
            Float32MultiArray, 'mic_audio', self.audio_callback, 10)
        self.sub_vad = self.create_subscription(
            Bool, 'vad_result', self.vad_callback, 10)

        self.sample_rate = 16000
        self.buffer = []
        self.recording = False
        self.output_dir = Path('/root/audio_logs')
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.get_logger().info('AudioSaverNode ready — will save .wav files for each VAD segment.')

    def vad_callback(self, msg: Bool):
        """Handle VAD state changes to start/stop recording."""
        if msg.data and not self.recording:
            self.get_logger().info('[VAD] Start recording')
            self.recording = True
            self.buffer.clear()
        elif not msg.data and self.recording:
            self.get_logger().info('[VAD] Stop recording and save')
            self.recording = False
            self.save_audio()

    def audio_callback(self, msg: Float32MultiArray):
        """Accumulate audio data while recording."""
        if self.recording:
            self.buffer.extend(msg.data)

    def save_audio(self):
        """Save buffered audio to a timestamped WAV file."""
        if not self.buffer:
            self.get_logger().warn('Buffer was empty — skipping save')
            return

        audio_np = np.array(self.buffer, dtype=np.float32)
        audio_int16 = np.int16(audio_np * 32767)

        timestamp = int(time.time())
        filename = self.output_dir / f"vad_audio_{timestamp}.wav"

        with wave.open(str(filename), 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_int16.tobytes())

        self.get_logger().info(f'Saved audio to {filename}')

def main(args=None):
    """Main entry point."""
    rclpy.init(args=args)
    node = AudioSaverNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutdown request (Ctrl-C).')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()