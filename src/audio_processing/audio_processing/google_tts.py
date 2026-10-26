#!/usr/bin/env python3
"""ROS 2 Google TTS Service.

Exposes a ROS 2 service that converts text to Base64-encoded MP3
using Google Cloud Text-to-Speech API.
"""
import base64

import rclpy
from rclpy.node import Node

from google.cloud import texttospeech
from m_interfaces.srv import TextToSpeech


class GoogleTTSService(Node):
    """
    Exposes a ROS 2 service that turns text → Base-64 MP3 using Google Cloud TTS.
    """

    def __init__(self):
        super().__init__('google_tts_service')

        # Create the service
        self.srv = self.create_service(
            TextToSpeech,        # service type
            'tts_synthesize',    # service name
            self.handle_request  # callback
        )

        # Initialise Google Cloud TTS client once
        self.tts_client = texttospeech.TextToSpeechClient()
        self.get_logger().info('Google TTS service ready (returns Base-64 MP3)')

    # ---------- Service callback ------------------------------------------------
    def handle_request(self, request, response):
        """Handle TTS synthesis requests."""
        text = request.text.strip()
        self.get_logger().info(f"⮕  TTS request: '{text}'")

        try:
            audio_bytes = self._synthesize(text)
            # Encode to Base-64 for transport
            response.audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            response.success = True
            response.error_message = ''
            self.get_logger().info('✓  Synthesis complete, returning Base-64')
        except Exception as e:
            resp_msg = f'TTS synthesis failed: {e}'
            self.get_logger().error(resp_msg)
            response.audio_base64 = ''
            response.success = False
            response.error_message = resp_msg

        return response

    # ---------- Google Cloud helper --------------------------------------------
    def _synthesize(self, text: str) -> bytes:
        """Call Google Cloud and return raw MP3 bytes."""
        synthesis_input = texttospeech.SynthesisInput(text=text)

        voice = texttospeech.VoiceSelectionParams(
            language_code='en-US',
            name='en-US-Chirp3-HD-Zephyr'
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=0.75
        )

        reply = self.tts_client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        return reply.audio_content


def main(args=None):
    """Main entry point."""
    rclpy.init(args=args)
    node = GoogleTTSService()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutdown request (Ctrl-C).')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()