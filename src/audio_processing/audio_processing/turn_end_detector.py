#!/usr/bin/env python3
"""ROS 2 Turn End Detector Node.

Buffers audio and uses VAD to detect speech segments, then predicts
whether the turn is complete using the smart-turn model.
Publishes turn completion events.
"""
import os
from collections import deque
import numpy as np
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, Float32MultiArray, String
import ament_index_python

from audio_processing.turn_predictor import TurnPredictor


class TurnEndDetectorNode(Node):
    """Detects turn completion based on VAD and audio analysis."""

    def __init__(self):
        super().__init__('turn_end_detector')

        # Parameters
        self.declare_parameter('vad_threshold', 0.5)
        self.declare_parameter('pre_speech_ms', 200)
        self.declare_parameter('stop_ms', 100)
        self.declare_parameter('max_duration_sec', 8)
        
        self.sample_rate = 16000
        self.chunk_size = 512  # matches silero VAD chunk size
        
        # Calculate chunk counts
        chunk_ms = (self.chunk_size / self.sample_rate) * 1000.0
        self.pre_chunks = int(np.ceil(self.get_parameter('pre_speech_ms').value / chunk_ms))
        self.stop_chunks = int(np.ceil(self.get_parameter('stop_ms').value / chunk_ms))
        self.max_chunks = int(np.ceil(
            self.get_parameter('max_duration_sec').value / (self.chunk_size / self.sample_rate)
        ))
        
        # Audio buffering
        self.pre_buffer = deque(maxlen=self.pre_chunks)
        self.segment_buffer = []
        self.speech_active = False
        self.trailing_silence = 0
        self.chunks_since_trigger = 0
        
        # Audio chunk buffer (accumulate until we have chunk_size samples)
        self.audio_chunk_buffer = []
        
        # Load turn predictor
        model_path = '/root/m_ws/src/audio_processing/models/smart-turn-v3.0.onnx'
        self.predictor = TurnPredictor(model_path)
        
        # Subscribers
        self.audio_sub = self.create_subscription(
            Float32MultiArray,
            'mic_audio',
            self.audio_callback,
            10
        )
        self.vad_sub = self.create_subscription(
            Bool,
            'vad_result',
            self.vad_callback,
            10
        )
        self.speaking_sub = self.create_subscription(
            Bool,
            'robot_speaking',
            self.robot_speaking_callback,
            10
        )
        
        # Publisher for turn completion results
        self.turn_pub = self.create_publisher(String, 'turn_completion', 10)
        
        self.current_vad_state = False
        self.robot_speaking = False
        self.get_logger().info('Turn End Detector node ready.')

    def audio_callback(self, msg: Float32MultiArray):
        """Buffer incoming audio chunks."""
        if not self.robot_speaking:
            self.audio_chunk_buffer.extend(list(msg.data))

    def robot_speaking_callback(self, msg: Bool):
        """Handle robot speaking state changes."""
        was_speaking = self.robot_speaking
        self.robot_speaking = msg.data
        
        # If robot just finished speaking, reset state to start fresh for user turn
        if was_speaking and not self.robot_speaking:
            # Clear any audio captured during robot speech transition
            self.audio_chunk_buffer.clear()
            self.segment_buffer.clear()
            self.speech_active = False
            self.trailing_silence = 0
            self.chunks_since_trigger = 0
            self.pre_buffer.clear()
            self.get_logger().info('Robot finished speaking - cleared buffers for new user turn')

    def vad_callback(self, msg: Bool):
        """Process VAD state changes and detect turn boundaries."""
        if self.robot_speaking:
            # Don't process VAD while robot is speaking
            return
            
        self.current_vad_state = msg.data
        
        # Process audio in chunk_size increments
        while len(self.audio_chunk_buffer) >= self.chunk_size:
            chunk = np.array(self.audio_chunk_buffer[:self.chunk_size], dtype=np.float32)
            self.audio_chunk_buffer = self.audio_chunk_buffer[self.chunk_size:]
            self._process_chunk(chunk)

    def _process_chunk(self, chunk: np.ndarray):
        """Process one audio chunk with VAD state."""
        is_speech = self.current_vad_state
        
        if not self.speech_active:
            # Warmup: accumulate pre-speech buffer
            self.pre_buffer.append(chunk)
            if is_speech:
                # Speech detected - start segment
                self.segment_buffer = list(self.pre_buffer)
                self.segment_buffer.append(chunk)
                self.speech_active = True
                self.trailing_silence = 0
                self.chunks_since_trigger = 1
                self.get_logger().info('Speech segment started')
        else:
            # Already capturing a segment
            self.segment_buffer.append(chunk)
            self.chunks_since_trigger += 1
            
            if is_speech:
                self.trailing_silence = 0
            else:
                self.trailing_silence += 1
            
            # Check end conditions
            if self.trailing_silence >= self.stop_chunks or \
               self.chunks_since_trigger >= self.max_chunks:
                self._process_segment()

    def _process_segment(self):
        """Process completed speech segment with turn predictor."""
        if not self.segment_buffer:
            return
        
        segment_audio = np.concatenate(self.segment_buffer, dtype=np.float32)
        dur_sec = segment_audio.size / self.sample_rate
        
        self.get_logger().info(f'Processing segment ({dur_sec:.2f}s)...')
        
        result = self.predictor.predict(segment_audio)
        
        prediction = "complete" if result["prediction"] == 1 else "incomplete"
        probability = result["probability"]
        
        self.get_logger().info(
            f'Turn prediction: {prediction} (prob={probability:.4f})'
        )
        
        # Publish result
        msg = String()
        msg.data = f'{prediction},{probability:.4f}'
        self.turn_pub.publish(msg)
        
        # Reset for next segment
        self.segment_buffer.clear()
        self.speech_active = False
        self.trailing_silence = 0
        self.chunks_since_trigger = 0
        self.pre_buffer.clear()


def main(args=None):
    """Main entry point."""
    rclpy.init(args=args)
    node = TurnEndDetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutdown request.')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
