#!/usr/bin/env python3
"""ROS 2 Faster Whisper Streaming ASR Node.

Provides speech recognition using Faster Whisper (tiny model) with VAD-based buffering.
Buffers audio during speech and transcribes when VAD indicates speech has ended.
Compatible interface with google_streaming_asr for plug-and-play replacement.
"""
from collections import deque
import os

import numpy as np
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, Float32MultiArray, String

from faster_whisper import WhisperModel


class WhisperStreamingASR(Node):
    """ASR node using Faster Whisper with VAD-based buffering."""

    def __init__(self):
        super().__init__('whisper_streaming_asr')

        # Subscribers
        self.sub_audio = self.create_subscription(
            Float32MultiArray, 'mic_audio', self.audio_callback, 10)
        self.sub_vad = self.create_subscription(
            Bool, 'vad_result', self.vad_callback, 10)
        self.sub_speaking = self.create_subscription(
            Bool, 'robot_speaking', self._on_robot_speaking, 10)

        # Publishers (matching google_asr interface)
        self.pub_final = self.create_publisher(String, 'asr_text', 10)
        # Note: No partial results as Faster Whisper doesn't support true streaming
        # but we keep the same topic structure for compatibility

        self.robot_speaking = False
        self.sample_rate = 16000

        # Audio buffering
        self.audio_buffer = deque()
        self.is_speech_active = False
        self.pre_buffer = deque(maxlen=40000)  # Buffer ~2 seconds before speech

        # Load Faster Whisper model
        self.get_logger().info('Loading Faster Whisper tiny model...')
        
        # Check if model is in local models directory
        models_dir = '/root/m_ws/src/audio_processing/models/whisper-tiny'
        
        if os.path.exists(models_dir):
            self.get_logger().info(f'Loading model from: {models_dir}')
            model_path = models_dir
        else:
            self.get_logger().info('Loading model: tiny (will download if needed)')
            model_path = "tiny"

        self.model = WhisperModel(
            model_path, 
            device="cpu", 
            compute_type="int8"
        )
        self.get_logger().info('Faster Whisper ASR node ready.')

    def _on_robot_speaking(self, msg: Bool):
        """Update robot speaking status."""
        self.robot_speaking = msg.data
        if self.robot_speaking:
            # Clear buffers when robot starts speaking
            self.audio_buffer.clear()
            self.is_speech_active = False
            self.get_logger().info('Robot speaking - clearing buffers')

    def vad_callback(self, msg: Bool):
        """Handle VAD state changes to start/stop buffering and trigger transcription."""
        if msg.data and not self.is_speech_active and not self.robot_speaking:
            # Speech started - begin buffering
            self.get_logger().info('[VAD] Speech started - buffering audio')
            self.is_speech_active = True
            
            # Pre-fill buffer with recent audio
            self.audio_buffer.clear()
            self.audio_buffer.extend(self.pre_buffer)
            
        elif not msg.data and self.is_speech_active:
            # Speech ended - transcribe buffered audio
            self.get_logger().info('[VAD] Speech ended - transcribing')
            self.is_speech_active = False
            self._transcribe_buffer()

    def audio_callback(self, msg: Float32MultiArray):
        """Process incoming audio and buffer during speech."""
        audio_np = np.array(msg.data, dtype=np.float32)
        
        # Always maintain pre-buffer
        self.pre_buffer.extend(audio_np)
        
        # Buffer audio during active speech
        if self.is_speech_active:
            self.audio_buffer.extend(audio_np)

    def _transcribe_buffer(self):
        """Transcribe the buffered audio using Faster Whisper."""
        if len(self.audio_buffer) == 0:
            self.get_logger().warn('No audio in buffer to transcribe')
            return

        try:
            # Convert buffer to numpy array
            audio_np = np.array(list(self.audio_buffer), dtype=np.float32)
            
            # Ensure audio is not empty and has reasonable length
            if len(audio_np) < self.sample_rate * 0.1:  # At least 100ms
                self.get_logger().warn('Audio too short to transcribe')
                self.audio_buffer.clear()
                return

            self.get_logger().info(
                f'Transcribing {len(audio_np)/self.sample_rate:.2f}s of audio')

            # Transcribe using Faster Whisper
            segments, info = self.model.transcribe(
                audio_np,
                beam_size=2,
                language="en",
                vad_filter=False,  # We already have VAD
                condition_on_previous_text=False
            )

            # Collect all segments into final transcript
            transcript_parts = []
            for segment in segments:
                transcript_parts.append(segment.text.strip())

            transcript = " ".join(transcript_parts).strip()

            if transcript:
                # Publish final result
                msg = String()
                msg.data = transcript
                self.pub_final.publish(msg)
                self.get_logger().info(f'[ASR FINAL] {transcript}')
            else:
                self.get_logger().info('[ASR] No speech detected in audio')

        except Exception as e:
            self.get_logger().error(f'Transcription error: {str(e)}')
        finally:
            # Clear buffer after transcription
            self.audio_buffer.clear()


def main(args=None):
    """Main entry point."""
    rclpy.init(args=args)
    node = WhisperStreamingASR()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutdown request (Ctrl-C).')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
