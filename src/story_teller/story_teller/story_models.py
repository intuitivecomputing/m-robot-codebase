"""Typed representations of stories consumed by story delivery (migrated to story_teller)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence


@dataclass(frozen=True)
class AnimationCue:
    program_json: str
    delay: float


@dataclass(frozen=True)
class BodyTimeline:
    timeline_json: str
    delay: float


@dataclass(frozen=True)
class NarrativeChunk:
    content: str
    audio_b64: str | None
    face_programs: List[AnimationCue] = field(default_factory=list)
    body_programs: List[BodyTimeline] = field(default_factory=list)


@dataclass(frozen=True)
class InteractionChunk:
    question: str
    target_vocab: str | None


StoryChunk = NarrativeChunk | InteractionChunk


@dataclass(frozen=True)
class StoryDocument:
    title: str
    chunks: List[StoryChunk]

    @staticmethod
    def _parse_face_programs(raw_items: Sequence[Sequence[object]]) -> List[AnimationCue]:
        programs: List[AnimationCue] = []
        for entry in raw_items:
            if len(entry) != 2:
                continue
            program, delay = entry
            try:
                delay_value = float(delay)
            except (TypeError, ValueError):
                delay_value = 0.0
            programs.append(AnimationCue(str(program), delay_value))
        return programs

    @staticmethod
    def _parse_body_programs(raw_items: Sequence[Sequence[object]]) -> List[BodyTimeline]:
        programs: List[BodyTimeline] = []
        for entry in raw_items:
            if len(entry) != 2:
                continue
            program, delay = entry
            try:
                delay_value = float(delay)
            except (TypeError, ValueError):
                delay_value = 0.0
            programs.append(BodyTimeline(str(program), delay_value))
        return programs

    @classmethod
    def from_dict(cls, payload: Dict[str, object]) -> "StoryDocument":
        title = str(payload.get("story", ""))
        raw_chunks = payload.get("chunks", [])
        chunks: List[StoryChunk] = []

        for raw_chunk in raw_chunks:
            if not isinstance(raw_chunk, dict):
                continue
            chunk_type = raw_chunk.get("type")
            if chunk_type == "narrative":
                chunks.append(
                    NarrativeChunk(
                        content=str(raw_chunk.get("content", "")),
                        audio_b64=str(raw_chunk.get("audio")) if raw_chunk.get("audio") else None,
                        face_programs=cls._parse_face_programs(raw_chunk.get("face_programs", []) or []),
                        body_programs=cls._parse_body_programs(raw_chunk.get("body_programs", []) or []),
                    )
                )
            elif chunk_type == "interaction":
                content = raw_chunk.get("content", {})
                question = ""
                vocab: str | None = None
                if isinstance(content, dict):
                    question = str(content.get("question", ""))
                    vocab_value = content.get("vocab")
                    vocab = str(vocab_value) if vocab_value else None
                chunks.append(InteractionChunk(question=question, target_vocab=vocab))
        return cls(title=title, chunks=chunks)
