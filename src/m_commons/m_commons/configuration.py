"""Configuration helpers shared across packages."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence

from rclpy.node import Node


class ConfigurationError(RuntimeError):
    """Raised when configuration parameters are invalid."""


def _expand_paths(values: Sequence[str]) -> List[Path]:
    paths: List[Path] = []
    for raw in values:
        if not raw:
            continue
        expanded = Path(os.path.expanduser(raw)).resolve()
        paths.append(expanded)
    return paths


@dataclass(frozen=True)
class StoryManagerConfig:
    """Configuration for managing story assets."""

    story_search_paths: List[Path]
    log_directory: Path
    default_story: str
    session_id: str

    @classmethod
    def from_node(cls, node: Node) -> "StoryManagerConfig":
        """Build configuration from ROS parameters and environment variables."""

        default_story_dir = Path("/root/m_ws/src/story_teller/stories")
        default_log_dir = Path(os.getenv("ROBOT_LOG_DIR", Path.home() / ".ella" / "logs"))

        search_paths_param = node.declare_parameter(
            "story_search_paths",
            [str(default_story_dir)],
        )
        log_dir_param = node.declare_parameter("log_directory", str(default_log_dir))
        default_story_param = node.declare_parameter("default_story", "chunked.json")
        session_param = node.declare_parameter("session_id", os.getenv("SESSION_ID", "session_unknown"))

        search_paths = _expand_paths(search_paths_param.value)
        if not search_paths:
            raise ConfigurationError("No story search paths configured")

        log_directory = Path(os.path.expanduser(log_dir_param.value)).resolve()
        log_directory.mkdir(parents=True, exist_ok=True)

        return cls(
            story_search_paths=search_paths,
            log_directory=log_directory,
            default_story=default_story_param.value,
            session_id=session_param.value,
        )

    def resolve_story_path(self, filename: str) -> Path:
        """Resolve *filename* against the configured search paths."""

        candidate = Path(os.path.expanduser(filename))
        if candidate.is_absolute() and candidate.exists():
            return candidate

        for base in self.story_search_paths:
            candidate = (base / filename).resolve()
            if candidate.exists():
                return candidate
        raise ConfigurationError(f"Story file '{filename}' not found in search paths {self.story_search_paths!r}")
