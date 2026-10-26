"""Coaching response generation using LLM backend (moved to positivity_pysch_coach)."""

from __future__ import annotations

import json
from typing import Optional

from positivity_pysch_coach.conversation_models import ConversationMemory, CoachReply
from .groq_llm_provider import Groq_LLMProvider


class CoachResponseGenerator:
    """Generate coaching responses using LLM API."""

    def __init__(self, *, node=None, model: str = "openai/gpt-oss-120b", temperature: float = 0.7, day: int = 1) -> None:
        self._node = node
        self._llm = Groq_LLMProvider(model=model, temperature=temperature)
        self._day = max(1, min(5, day))  # Clamp day between 1 and 5
        self._session_prompt = self._load_session_prompt(self._day)

    def _load_session_prompt(self, day: int) -> str:
        session_file_path = f"/root/m_ws/src/positivity_pysch_coach/positivity_pysch_coach/interaction_prompts/Session{day}.txt"
        with open(session_file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()

    def generate(self, memory: ConversationMemory, latest_user_text: Optional[str]) -> CoachReply:
        # Use the most recent turns for context so the LLM sees the latest
        # exchanges instead of only the very start of the session.
        conversation_context = memory.get_recent_context(max_turns=6)
        robot_turn_count = memory.robot_turns()

        if self._node:
            self._node.get_logger().info(f"[COACH_GEN] ========== LLM INPUT ==========")
            self._node.get_logger().info(f"[COACH_GEN] User utterance passed to LLM: '{latest_user_text}'")
            self._node.get_logger().info(f"[COACH_GEN] Robot turn count: {robot_turn_count}")
            # Log the tail of the conversational context (most recent content)
            self._node.get_logger().info(
                f"[COACH_GEN] Conversation context (recent): {conversation_context if conversation_context else '(empty)'}"
            )
            self._node.get_logger().info(f"[COACH_GEN] ================================")

        system_prompt = self._session_prompt

        user_message = self._build_user_message(
            conversation_context=conversation_context,
            latest_user_text=latest_user_text,
            turn_number=robot_turn_count,
        )
        
        if self._node:
            self._node.get_logger().info(f"[COACH_GEN] Full user message: {user_message[:300]}...")

        completion_text = self._llm.complete(
            system_prompt=system_prompt,
            user_message=user_message,
            max_tokens=1000,
            reasoning_effort="low",
        )

        if self._node:
            self._node.get_logger().info(f"[COACH_GEN] Raw LLM completion: {completion_text}")

        end_conversation = "[END_CONVERSATION]" in completion_text
        clean_response = completion_text.replace("[END_CONVERSATION]", "").strip()

        if self._node:
            self._node.get_logger().info(f"[COACH_GEN] Clean response after removing [END_CONVERSATION]: {clean_response}")

        # Strip markdown code blocks if present (e.g., ```json ... ```)
        if clean_response.startswith("```"):
            # Remove opening markdown code fence
            clean_response = clean_response.split("\n", 1)[1] if "\n" in clean_response else clean_response
        if clean_response.endswith("```"):
            # Remove closing markdown code fence
            clean_response = clean_response.rsplit("\n", 1)[0] if "\n" in clean_response else clean_response
        clean_response = clean_response.strip()

        try:
            utterances = json.loads(clean_response)
            if not isinstance(utterances, list):
                raise ValueError("Response must be a JSON array")
            
            # Validate structure: each item should have utterance, expression, gesture
            for item in utterances:
                if not isinstance(item, dict):
                    raise ValueError("Each item must be a dictionary")
                if "utterance" not in item or "expression" not in item or "gesture" not in item:
                    raise ValueError("Each item must have 'utterance', 'expression', and 'gesture' fields")
            
            if self._node:
                self._node.get_logger().info(f"[COACH_GEN] Successfully parsed {len(utterances)} utterances")
        except (json.JSONDecodeError, ValueError) as e:
            if self._node:
                self._node.get_logger().warning(f"[COACH_GEN] Failed to parse JSON response: {e}")
                self._node.get_logger().warning(f"[COACH_GEN] Raw response was: {repr(clean_response)}")
            # Fallback to simple format
            utterances = [{"utterance": clean_response or "Hello!", "expression": "neutral:low", "gesture": "base_shift:start"}]
        
        return CoachReply(
            utterances=utterances,
            end_conversation=end_conversation,
        )

    def set_day(self, day: int) -> None:
        self._day = max(1, min(5, day))
        self._session_prompt = self._load_session_prompt(self._day)
        if self._node:
            self._node.get_logger().info(f"[COACH_GEN] Coach session updated to day {self._day}")

    def get_day(self) -> int:
        return self._day

    def _build_user_message(
        self, conversation_context: str, latest_user_text: Optional[str], turn_number: int
    ) -> str:
        if turn_number == 0:
            return "Begin the coaching session."

        msg = (
            "Conversation so far:\n"
            + (conversation_context if conversation_context else "(No prior exchanges)")
            + "\n\n"
        )

        if latest_user_text:
            msg += f"The user just said: {latest_user_text}\n"
        else:
            msg += "The user has not yet responded in this turn.\n"

        msg += "\nProvide your next response according to the session format:"

        return msg
