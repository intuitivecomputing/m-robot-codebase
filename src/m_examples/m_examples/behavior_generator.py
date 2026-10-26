"""Behavior generation using Groq LLM for robot expressions and movements."""

from __future__ import annotations

import json
import logging
from typing import List, Dict, Any

from .groq_llm_provider import Groq_LLMProvider


logger = logging.getLogger(__name__)


class BehaviorGenerator:
    """Generate robot behaviors (expressions and movements) using Groq LLM."""

    def __init__(self) -> None:
        """Initialize behavior generator with Groq client."""
        self._llm = Groq_LLMProvider(model="openai/gpt-oss-20b", temperature=0.7)
        self._body_gen_prompt = self._load_body_gen_prompt()

    def _load_body_gen_prompt(self) -> str:
        """Load the BodyGenPrompt.txt file."""
        prompt_path = "/root/m_ws/src/m_examples/m_examples/prompts/BodyGenPrompt.txt"
        
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read().strip()

    def generate_behaviors(self, segments: List[str]) -> List[Dict[str, Any]]:
        """Generate behaviors for a list of text segments.
        
        Args:
            segments: List of text segments to generate behaviors for
            
        Returns:
            List of behavior dictionaries with segmentID, expression, and primitive
        """
        if not segments:
            return []

        # Format segments as JSON array for the prompt
        segments_json = json.dumps(segments)
        
        # Use the BodyGenPrompt as system prompt and segments as user input
        user_message = f"Input: {segments_json}"
        
        try:
            # Call Groq with reasoning effort
            response_text = self._llm.complete(
                system_prompt=self._body_gen_prompt,
                user_message=user_message,
                max_tokens=2000,
                reasoning_effort="low",
            )
            
            logger.info(f"LLM raw response: {response_text[:500]}...")  # Log first 500 chars
            
            # Parse the JSON response
            behaviors = json.loads(response_text.strip())
            logger.info(f"Parsed {len(behaviors)} behaviors successfully")
            
            # Validate the response format
            if not isinstance(behaviors, list):
                raise ValueError("Response must be a JSON array")
                
            for behavior in behaviors:
                if not isinstance(behavior, dict):
                    raise ValueError("Each behavior must be a dictionary")
                required_keys = ["segmentID", "expression", "primitive"]
                for key in required_keys:
                    if key not in behavior:
                        raise ValueError(f"Missing required key: {key}")
            
            return behaviors
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse behavior response: {e}")
            logger.error(f"Response text was: {response_text if 'response_text' in locals() else 'N/A'}")
            # Return neutral behaviors as fallback
            return [
                {
                    "segmentID": i,
                    "expression": "neutral",
                    "primitive": None
                }
                for i in range(len(segments))
            ]
        except Exception as e:
            logger.error(f"Behavior generation failed: {e}")
            return [
                {
                    "segmentID": i,
                    "expression": "neutral",
                    "primitive": None
                }
                for i in range(len(segments))
            ]
