#!/usr/bin/env python3
"""ROS 2 OpenAI TTS Service."""
import base64
import os

import rclpy
from rclpy.node import Node
import requests

from m_interfaces.srv import TextToSpeech


class OpenAITTSService(Node):
    """
    Exposes a ROS 2 service that turns text → Base-64 MP3 using OpenAI TTS API.
    """

    def __init__(self):
        super().__init__('openai_tts_service')

        # Create the service
        self.srv = self.create_service(
            TextToSpeech,        # service type
            'tts_synthesize',    # service name (same as google_tts)
            self.handle_request  # callback
        )

        # Get OpenAI API key from environment variable
        self.api_key = os.environ.get('OPENAI_API_KEY')
        if not self.api_key:
            self.get_logger().error(
                'OPENAI_API_KEY environment variable not set!')


        
        self.get_logger().info('OpenAI TTS service ready (returns Base-64 MP3)')

    # ---------- Service callback ------------------------------------------------
    def handle_request(self, request, response):
        """Handle TTS synthesis requests."""
        text = request.text.strip()
        self.get_logger().info(f"⮕  OpenAI TTS request: '{text}'")

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

    # ---------- OpenAI API helper --------------------------------------------
    def _synthesize(self, text: str) -> bytes:
        """Call OpenAI API and return raw MP3 bytes."""
        url = "https://api.openai.com/v1/audio/speech"
        data = {
            "input": text,
            "model": "gpt-4o-mini-tts",
            "voice": "sage",
            "speed": 0.9,
            "instructions": (
                "You are Ella, a friendly and magical storytelling robot who loves sharing adventures with pre-school aged children. "
                "Your voice is clear, warm, and engaging, with a pitch that feels comforting and fun. Speak at a gentle, steady pace so young listeners can follow along easily. "
                "Make sure every word is clearly pronounced, with expressive tone and a touch of wonder — as if you’re inviting the listener into a magical world. "
                "Pause at key plot points and story sections so that the children have time to take in the content."
            )
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        response = requests.post(url, json=data, headers=headers)
        if response.status_code != 200:
            raise RuntimeError(
                f"OpenAI API error: {response.status_code} {response.text}")
        return response.content  # MP3 bytes


def main(args=None):
    """Main entry point."""
    rclpy.init(args=args)
    node = OpenAITTSService()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutdown request (Ctrl-C).')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
