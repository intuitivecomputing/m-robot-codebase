"""Session tracking for multi-day positivity coaching intervention."""

from __future__ import annotations

import json
from datetime import datetime, date
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo


class SessionTracker:
    """Track and manage session state across deployment days."""

    DEFAULT_CONFIG = {
        "start_date": None,
        "timezone": "America/New_York",
        "max_sessions": 5,
    }

    def __init__(self, config_path: str) -> None:
        self._config_path = Path(config_path)
        self._config = self._load_config()

    def _load_config(self) -> dict:
        if self._config_path.exists():
            with open(self._config_path, "r") as f:
                return {**self.DEFAULT_CONFIG, **json.load(f)}
        return self.DEFAULT_CONFIG.copy()

    def _save_config(self) -> None:
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._config_path, "w") as f:
            json.dump(self._config, f, indent=2)

    def _get_today(self) -> date:
        tz = ZoneInfo(self._config["timezone"])
        return datetime.now(tz).date()

    def _get_start_date(self) -> Optional[date]:
        if self._config["start_date"]:
            return date.fromisoformat(self._config["start_date"])
        return None

    def get_session_number(self) -> int:
        """Return current session number (1-5) based on days since start."""
        start = self._get_start_date()
        if start is None:
            # Auto-initialize start_date on first run
            self._config["start_date"] = self._get_today().isoformat()
            self._save_config()
            return 1

        days_elapsed = (self._get_today() - start).days
        session = days_elapsed + 1  # Day 0 -> Session 1
        return max(1, min(session, self._config["max_sessions"]))

    def get_prompt_path(self, base_path: str) -> str:
        """Return full path to the session prompt file."""
        session_num = self.get_session_number()
        return f"{base_path}/Session{session_num}.txt"

    def get_session_info(self) -> dict:
        """Return session metadata for logging/debugging."""
        return {
            "session_number": self.get_session_number(),
            "start_date": self._config["start_date"],
            "timezone": self._config["timezone"],
            "today": self._get_today().isoformat(),
        }
