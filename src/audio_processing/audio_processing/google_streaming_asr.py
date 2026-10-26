#!/usr/bin/env python3
"""ROS 2 Google Streaming ASR Node.

Provides real-time speech recognition using Google Cloud Speech-to-Text API
with support for interim and final results.
"""
import queue
import threading
from collections import deque

import numpy as np
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, Float32MultiArray, String

from google.cloud import speech


class GoogleStreamingASR(Node):
    """Real-time ASR using Google Cloud Speech-to-Text streaming API."""

    def __init__(self):
        super().__init__('google_asr_streaming')

        self.sub_audio = self.create_subscription(
            Float32MultiArray, 'mic_audio', self.audio_callback, 10)
        self.sub_vad = self.create_subscription(
            Bool, 'vad_result', self.vad_callback, 10)
        self.pub_final = self.create_publisher(String, 'asr_text', 10)
        self.pub_partial = self.create_publisher(String, 'asr_partial', 10)
        self.sub_speaking = self.create_subscription(
            Bool, 'robot_speaking', self._on_robot_speaking, 10)
    
        self.robot_speaking = False

        self.sample_rate = 16000
        self.audio_queue = queue.Queue()
        self.streaming = False
        self.stop_stream = threading.Event()
        self.stream_thread = None

        self.client = speech.SpeechClient()
        self.config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=self.sample_rate,
            language_code="en-US",
            enable_automatic_punctuation=True
        )
        self.streaming_config = speech.StreamingRecognitionConfig(
            config=self.config,
            interim_results=True,
            single_utterance=False
        )

        self.pre_buffer = deque(maxlen=40000)  # Buffer ~2 seconds of audio

        self.get_logger().info('Google Streaming ASR node ready.')

    def _on_robot_speaking(self, msg: Bool):
        """Update robot speaking status."""
        self.robot_speaking = msg.data
        
        # When robot starts speaking, clear pre-buffer to avoid capturing robot audio tail
        if self.robot_speaking:
            self.pre_buffer.clear()
        
        self.get_logger().info(f'Robot speaking status: {self.robot_speaking}')

    def vad_callback(self, msg: Bool):
        """Handle VAD state changes to start/stop streaming."""
        if msg.data and not self.streaming and not self.robot_speaking:
            # Wait for any previous stream to fully close
            if self.stream_thread and self.stream_thread.is_alive():
                self.get_logger().info('[VAD] Waiting for previous stream to close...')
                self.stop_stream.set()
                self.stream_thread.join(timeout=1.0)
            
            self.get_logger().info('[VAD] Voice started — opening stream')
            self.streaming = True
            self.stop_stream.clear()

            # Pre-fill audio queue with buffered audio
            with self.audio_queue.mutex:
                self.audio_queue.queue.clear()

            buffered_audio = list(self.pre_buffer)
            chunk_size = 320  # 20ms at 16kHz

            for i in range(0, len(buffered_audio), chunk_size):
                chunk = bytes(buffered_audio[i:i+chunk_size])
                self.audio_queue.put(chunk)

            self.stream_thread = threading.Thread(
                target=self.stream_audio_to_google, daemon=True)
            self.stream_thread.start()
        elif not msg.data and self.streaming:
            self.get_logger().info('[VAD] Voice ended — closing stream')
            self.streaming = False
            self.stop_stream.set()

    def audio_callback(self, msg: Float32MultiArray):
        """Process incoming audio and buffer for streaming."""
        audio_np = np.array(msg.data, dtype=np.float32)
        audio_int16 = np.int16(audio_np * 32767)
        audio_bytes = audio_int16.tobytes()

        # Only buffer audio if robot is not speaking (prevents capturing robot's tail audio)
        if not self.robot_speaking:
            self.pre_buffer.extend(audio_bytes)  # Fill the rolling buffer only during user turn

        if self.streaming and not self.robot_speaking:
            self.audio_queue.put(audio_bytes)

    def stream_audio_to_google(self):
        """Stream audio chunks to Google Cloud Speech API."""
        def request_generator():
            while not self.stop_stream.is_set():
                try:
                    chunk = self.audio_queue.get(timeout=0.1)
                    yield speech.StreamingRecognizeRequest(audio_content=chunk)
                except queue.Empty:
                    continue

        try:
            responses = self.client.streaming_recognize(
                self.streaming_config, request_generator())
            for response in responses:
                for result in response.results:
                    transcript = result.alternatives[0].transcript
                    msg = String()
                    msg.data = transcript
                    if result.is_final:
                        self.pub_final.publish(msg)
                        self.get_logger().info(f"[ASR FINAL] {transcript}")
                    else:
                        self.pub_partial.publish(msg)
        except Exception as e:
            self.get_logger().error(f"[Google ASR Streaming Error] {str(e)}")


def main(args=None):
    """Main entry point."""
    rclpy.init(args=args)
    node = GoogleStreamingASR()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutdown request (Ctrl-C).')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()