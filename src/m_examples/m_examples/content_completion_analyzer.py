"""Content-based turn completion analysis using OpenAI (moved to positivity_pysch_coach)."""

from __future__ import annotations

import os
from typing import Optional

import openai
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, String


class ContentCompletionAnalyzer(Node):
    def __init__(self) -> None:
        super().__init__("content_completion_analyzer")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            self.get_logger().error("OPENAI_API_KEY not set")
            raise RuntimeError("OPENAI_API_KEY environment variable required")
        openai.api_key = api_key
        self._system_prompt = (
            "Determine if the user completed their thought. Output ONLY 'yes' or 'no'.\n\n"
            "Output 'yes' for complete thoughts (ignore fillers like 'uh', 'um'):\n"
            "- 'What's going to happen?' (complete question)\n"
            "- 'I'm not sure. I'm trying to see.' (complete statement)\n"
            "- 'Let's see if that happens.' (complete thought)\n"
            "- 'But yeah, let's see if that happens.' (complete despite 'uh')\n"
            "- Any sentence with clear meaning and conclusion\n\n"
            "Output 'no' ONLY for obvious incomplete fragments:\n"
            "- 'I think that...' (trailing off)\n"
            "- 'Well, um...' (just hesitation)\n"
            "- 'The thing is' (clearly unfinished)\n\n"
            "IGNORE fillers (uh, um, like). Focus on whether the meaning is complete.\n"
            "When unsure, default to 'yes'.\n"
        )
        self.create_subscription(String, "asr_partial", self._on_partial_text, 10)
        self.create_subscription(String, "asr_text", self._on_final_text, 10)
        self._completion_pub = self.create_publisher(Bool, "content_complete", 10)
        self._current_text = ""
        self._analyzing = False
        self.get_logger().info("Content completion analyzer ready - subscribed to asr_partial and asr_text")

    def _on_partial_text(self, msg: String) -> None:
        self._current_text = msg.data.strip()

    def _on_final_text(self, msg: String) -> None:
        self._current_text = msg.data.strip()
        if self._current_text and not self._analyzing:
            self._analyze_completion()

    def _analyze_completion(self) -> None:
        if not self._current_text or self._analyzing:
            return
        self._analyzing = True
        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self._system_prompt},
                    {"role": "user", "content": f'User speech: "{self._current_text}"'}
                ],
                temperature=0.3,
                max_tokens=10,
                timeout=5.0
            )
            result = response.choices[0].message.content.strip().lower()
            is_complete = result == "yes"
            msg = Bool(); msg.data = is_complete
            self._completion_pub.publish(msg)
            self.get_logger().info(f"[CONTENT_ANALYZER] Result: '{self._current_text}' -> {is_complete} (raw: '{result}')")
        except Exception as exc:
            self.get_logger().error(f"[CONTENT_ANALYZER] Analysis failed: {exc}")
        finally:
            self._analyzing = False

def main(args: Optional[list] = None) -> None:
    rclpy.init(args=args)
    node = ContentCompletionAnalyzer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutdown requested")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()
