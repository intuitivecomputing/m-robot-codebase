#!/usr/bin/env python3
"""Conversation logger node for recording user and robot speech to JSONL."""

from __future__ import annotations

import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_srvs.srv import SetBool


class ConversationLogger(Node):
    """Logs user and robot utterances to JSONL files."""

    def __init__(self) -> None:
        super().__init__("conversation_logger")

        self.declare_parameter("output_directory", "/root/m_ws/data/conversations")
        self.declare_parameter("auto_start", True)

        self._output_dir = Path(self.get_parameter("output_directory").value)
        self._auto_start = self.get_parameter("auto_start").value
        self._output_dir.mkdir(parents=True, exist_ok=True)

        self._logging = False
        self._session_id: Optional[str] = None
        self._file_handle = None
        self._write_lock = threading.Lock()
        self._entry_count = 0

        self.create_service(SetBool, "start_logging", self._start_logging_cb)
        self.create_service(SetBool, "stop_logging", self._stop_logging_cb)

        self.create_subscription(String, "asr_text", self._on_user_speech, 10)
        self.create_subscription(String, "robot_utterance", self._on_robot_speech, 10)

        if self._auto_start:
            self._start_session()

        self.get_logger().info(f"Conversation logger ready. Output: {self._output_dir}")

    def _start_session(self) -> str:
        self._session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file = self._output_dir / f"conversation_{self._session_id}.jsonl"
        self._file_handle = open(log_file, "w", encoding="utf-8")
        self._logging = True
        self._entry_count = 0
        self.get_logger().info(f"Started session: {self._session_id}")
        return self._session_id

    def _stop_session(self) -> None:
        if not self._logging:
            return
        with self._write_lock:
            if self._file_handle:
                self._file_handle.close()
                self._file_handle = None
        self.get_logger().info(f"Stopped session {self._session_id}. Entries: {self._entry_count}")
        self._logging = False

    def _write_entry(self, speaker: str, text: str) -> None:
        if not self._logging or not self._file_handle:
            return
        entry = {
            "ts": datetime.now().isoformat(),
            "speaker": speaker,
            "text": text,
        }
        with self._write_lock:
            self._file_handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
            self._file_handle.flush()
            self._entry_count += 1

    def _start_logging_cb(self, request: SetBool.Request, response: SetBool.Response) -> SetBool.Response:
        if request.data and not self._logging:
            self._start_session()
            response.success = True
            response.message = f"Started: {self._session_id}"
        else:
            response.success = False
            response.message = "Already logging" if self._logging else "Use data=True to start"
        return response

    def _stop_logging_cb(self, request: SetBool.Request, response: SetBool.Response) -> SetBool.Response:
        if self._logging:
            self._stop_session()
            response.success = True
            response.message = "Stopped"
        else:
            response.success = False
            response.message = "Not logging"
        return response

    def _on_user_speech(self, msg: String) -> None:
        if msg.data.strip():
            self._write_entry("user", msg.data)

    def _on_robot_speech(self, msg: String) -> None:
        if msg.data.strip():
            self._write_entry("robot", msg.data)

    def destroy_node(self) -> None:
        self._stop_session()
        super().destroy_node()


def main(args=None) -> None:
    rclpy.init(args=args)
    node = ConversationLogger()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
