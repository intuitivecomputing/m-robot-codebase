#!/usr/bin/env python3
"""ROS 2 Faster Whisper ASR Service.

Provides speech-to-text transcription with word-level timestamps
using the Faster Whisper model.
"""
import base64
import io

import numpy as np
import rclpy
from rclpy.node import Node
import soundfile as sf

from faster_whisper import WhisperModel
from m_interfaces.srv import TranscribeAudio


class FasterWhisperASRService(Node):
    """Service node for ASR using Faster Whisper."""

    def __init__(self):
        super().__init__('faster_whisper_asr_service')

        self.srv = self.create_service(
            TranscribeAudio, 'faster_whisper_transcribe', self.transcribe_callback)

        self.get_logger().info('Faster Whisper ASR service LOADING...')
        self.model = WhisperModel("tiny", device="cpu", compute_type="int8")
        self.get_logger().info('Faster Whisper ASR service loaded.')

    def transcribe_callback(self, request, response):
        """Handle transcription requests with word-level timestamps."""
        try:
            # Decode base64 audio data
            base64_audio = request.base64_audio.split(";base64,")[-1]
            audio_data = base64.b64decode(base64_audio)

            # Load audio data into a NumPy array
            audio_buffer = io.BytesIO(audio_data)
            audio, sample_rate = sf.read(audio_buffer)

            # Transcribe using Faster Whisper
            segments, info = self.model.transcribe(
                audio, beam_size=2, language="en", word_timestamps=True)

            # Process segments to create timestamped transcript
            transcript_parts = []
            for segment in segments:
                if hasattr(segment, 'words') and segment.words:
                    for word in segment.words:
                        timestamp = round(word.start, 2)
                        word_text = word.word.strip()
                        transcript_parts.append(f"<{timestamp:.2f}> {word_text}")
                else:
                    # Fallback if word timestamps are not available
                    timestamp = round(segment.start, 2)
                    text = segment.text.strip()
                    transcript_parts.append(f"<{timestamp:.2f}> {text}")

            response.transcript = " ".join(transcript_parts)
            self.get_logger().info(f'[ASR] Transcribed: {response.transcript}')
            return response
        except Exception as e:
            self.get_logger().error(f"Transcription error: {e}")
            response.transcript = ""
            return response


def main(args=None):
    """Main entry point."""
    rclpy.init(args=args)
    node = FasterWhisperASRService()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutdown request (Ctrl-C).')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()