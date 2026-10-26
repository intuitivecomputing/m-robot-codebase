"""Core data models for conversation management (migrated to positivity_pysch_coach)."""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import List, Optional

# Story models now live in story_teller
from story_teller.story_models import AnimationCue, BodyTimeline


@dataclass(frozen=True)
class Turn:
    """Single conversational turn."""

    speaker: str
    text: str


class ConversationMemory:
    """Thread-safe turn history for grounding responses."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._turns: List[Turn] = []

    def add_turn(self, speaker: str, text: str) -> None:
        cleaned = text.strip()
        if not cleaned:
            return
        with self._lock:
            self._turns.append(Turn(speaker=speaker, text=cleaned))

    def last_user_text(self) -> Optional[str]:
        with self._lock:
            for turn in reversed(self._turns):
                if turn.speaker == "user":
                    return turn.text
        return None

    def robot_turns(self) -> int:
        with self._lock:
            return sum(1 for turn in self._turns if turn.speaker == "robot")

    def snapshot(self) -> List[Turn]:
        with self._lock:
            return list(self._turns)

    def get_full_context(self) -> str:
        with self._lock:
            if not self._turns:
                return ""
            return "\n".join([f"{turn.speaker.capitalize()}: {turn.text}" for turn in self._turns])

    def get_recent_context(self, max_turns: int = 6) -> str:
        """Return the most recent `max_turns` turns as a single context string.

        Default returns the last 6 turns (roughly last few exchanges). This is
        useful for LLM prompts where recent context matters more than the very
        beginning of the session.
        """
        with self._lock:
            if not self._turns:
                return ""
            recent = self._turns[-max_turns:]
            return "\n".join([f"{turn.speaker.capitalize()}: {turn.text}" for turn in recent])


@dataclass
class CoachReply:
    """Response payload generated for the next robot turn."""

    utterances: List[dict] = field(default_factory=list)
    end_conversation: bool = False
    
    @property
    def text(self) -> str:
        """Get full text by concatenating all utterances."""
        return " ".join([u.get("utterance", "") for u in self.utterances])
    
    @property
    def segments(self) -> List[str]:
        """Get list of text segments for backward compatibility."""
        return [u.get("utterance", "") for u in self.utterances]
