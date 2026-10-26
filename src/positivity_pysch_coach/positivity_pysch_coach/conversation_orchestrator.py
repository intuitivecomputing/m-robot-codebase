"""Realtime conversation orchestrator moved to `positivity_pysch_coach`.

Adapted from `behavior_control.conversation_orchestrator`, updated imports to
use `m_commons` and `positivity_pysch_coach` modules.
"""

from __future__ import annotations

from enum import Enum, auto
from typing import List, Optional

import rclpy
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.task import Future
from std_msgs.msg import Bool, String

from positivity_pysch_coach.conversation_models import ConversationMemory, CoachReply
from positivity_pysch_coach.coach_response_generator import CoachResponseGenerator
from positivity_pysch_coach.response_delivery import ResponseDelivery
from positivity_pysch_coach.turn_manager import TurnManagerConfig, TurnManager
from positivity_pysch_coach.session_tracker import SessionTracker


class ConversationState(Enum):
    STARTING = auto()
    ROBOT_PROCESSING = auto()
    ROBOT_SPEAKING = auto()
    WAITING_USER = auto()
    FINISHED = auto()


class ConversationOrchestrator(Node):
    CONFIG_PATH = "/root/m_ws/src/positivity_pysch_coach/config/session_config.json"

    def __init__(self) -> None:
        super().__init__("conversation_orchestrator")

        self.declare_parameter("initial_wait_ms", 5000.0)
        self.declare_parameter("vad_silence_timeout_ms", 1500.0)

        config = TurnManagerConfig(
            initial_wait_ms=self.get_parameter("initial_wait_ms").value,
            vad_silence_timeout_ms=self.get_parameter("vad_silence_timeout_ms").value,
        )

        self._session_tracker = SessionTracker(self.CONFIG_PATH)
        session_info = self._session_tracker.get_session_info()
        self.get_logger().info(f"Session tracker initialized: {session_info}")

        self._memory = ConversationMemory()
        self._delivery = ResponseDelivery(self)
        self._manager = TurnManager(self, config)

        try:
            self._llm = CoachResponseGenerator(
                node=self,
                model="openai/gpt-oss-120b",
                day=session_info["session_number"],
            )
            self.get_logger().info(
                f"LLM provider initialized (openai/gpt-oss-120b) - Session {session_info['session_number']}"
            )
        except RuntimeError as exc:
            self.get_logger().error(f"Failed to initialize LLM: {exc}")
            raise

        self._state = ConversationState.STARTING
        self._latest_user_text: str = ""
        self._pending_user_text: Optional[str] = None
        self._conversation_should_end = False
        self._asr_wait_timer = None
        self._turn_update_timer = None
        self._user_turn_finalized = False  # Flag to prevent re-finalization

        self.create_subscription(String, "asr_text", self._on_asr_final, 10)
        self._robot_speaking_pub = self.create_publisher(Bool, "robot_speaking", 10)
        self._start_timer = self.create_timer(0.5, self._begin_conversation)

    def _begin_conversation(self) -> None:
        if self._state != ConversationState.STARTING:
            return
        self._start_timer.cancel()
        self._start_robot_turn(initial=True)

    def _start_robot_turn(self, *, initial: bool = False, user_text: str = None) -> None:
        self._state = ConversationState.ROBOT_PROCESSING
        
        # Use provided user_text, or get from _latest_user_text if not provided
        if user_text is None:
            user_text = self._latest_user_text if (not initial and self._latest_user_text) else None
            # Clear _latest_user_text to prevent reuse
            self._latest_user_text = ""
        
        # Add accumulated user text to memory before generating response
        if user_text:
            self._memory.add_turn("user", user_text)
        
        reply = self._llm.generate(self._memory, user_text)
        # Behavior generation omitted here — assumed to be handled elsewhere
        self._memory.add_turn("robot", reply.text)
        
        self._state = ConversationState.ROBOT_SPEAKING
        self._robot_speaking_pub.publish(Bool(data=True))

        speak_future = self._delivery.speak(reply)
        speak_future.add_done_callback(lambda fut: self._on_robot_spoken(fut, reply))

    def _on_robot_spoken(self, future: Future, reply: CoachReply) -> None:
        try:
            future.result()
        except Exception as exc:
            self.get_logger().error(f"Robot speech failed: {exc}")
            self._state = ConversationState.FINISHED
            self._robot_speaking_pub.publish(Bool(data=False))
            return

        if reply.end_conversation:
            self._conversation_should_end = True

        if self._conversation_should_end:
            self._state = ConversationState.FINISHED
            self._robot_speaking_pub.publish(Bool(data=False))
            self.get_logger().info("Conversation concluded")
            return

        self._prepare_user_turn()

    def _prepare_user_turn(self) -> None:
        self._robot_speaking_pub.publish(Bool(data=False))
        
        # Reset finalization flag for the next user turn
        self._user_turn_finalized = False
        
        # Transfer pending text (captured while robot was speaking) to the start
        # of this user turn, then clear pending
        if self._pending_user_text:
            self.get_logger().info(f"[PREPARE_TURN] Carrying forward buffered text: '{self._pending_user_text}'")
            self._latest_user_text = self._pending_user_text
            self._pending_user_text = None
        else:
            self._latest_user_text = ""
        
        self._state = ConversationState.WAITING_USER
        now = self.get_clock().now().nanoseconds / 1e9
        self._manager.start(
            now, 
            on_complete_callback=self._on_user_turn_complete,
            has_asr_text_callback=lambda: bool(self._latest_user_text)
        )
        # Start periodic update timer for turn manager
        if self._turn_update_timer:
            self._turn_update_timer.cancel()
        self._turn_update_timer = self.create_timer(0.05, self._update_turn_manager)

    def _on_asr_final(self, msg: String) -> None:
        text = msg.data.strip()
        if not text:
            return
        
        if self._state == ConversationState.WAITING_USER:
            # Concatenate ASR finals with space separator during user's turn
            if self._latest_user_text:
                self._latest_user_text += " " + text
            else:
                self._latest_user_text = text
            if self._asr_wait_timer:
                self._asr_wait_timer.cancel()
                self._asr_wait_timer = None
                self._finalize_turn()
        elif self._state == ConversationState.ROBOT_PROCESSING:
            # Robot is thinking - buffer ASR for next user turn
            self.get_logger().info(f"[ASR] Buffering ASR during ROBOT_PROCESSING: '{text}'")
            if self._pending_user_text:
                self._pending_user_text += " " + text
            else:
                self._pending_user_text = text
        elif self._state == ConversationState.ROBOT_SPEAKING:
            # Robot is speaking - save for next turn
            self.get_logger().info(f"[ASR] User speaking during robot turn: '{text}'")
            if self._pending_user_text:
                self._pending_user_text += " " + text
            else:
                self._pending_user_text = text
        elif self._state == ConversationState.STARTING:
            # Robot hasn't started yet - ignore ASR (ambient noise)
            self.get_logger().info(f"[ASR] Ignoring ASR during STARTING: '{text}'")

    def _update_turn_manager(self) -> None:
        """Periodically update turn manager to check for completion."""
        if self._state != ConversationState.WAITING_USER:
            if self._turn_update_timer:
                self._turn_update_timer.cancel()
                self._turn_update_timer = None
            return
        
        now = self.get_clock().now().nanoseconds / 1e9
        turn_complete = self._manager.update(now)
        
        if turn_complete:
            if self._turn_update_timer:
                self._turn_update_timer.cancel()
                self._turn_update_timer = None
            self._manager.stop()
            self._on_user_turn_complete_internal()

    def _on_user_turn_complete_internal(self) -> None:
        """Internal handler when turn manager signals completion."""
        if self._state != ConversationState.WAITING_USER:
            return
        
        # Prevent re-finalization of the same turn
        if self._user_turn_finalized:
            self.get_logger().info("[FINALIZE] User turn already finalized, ignoring duplicate completion")
            return
        
        self._user_turn_finalized = True
        
        # Cancel any existing ASR wait timer
        if self._asr_wait_timer:
            self._asr_wait_timer.cancel()
            self._asr_wait_timer = None
        
        # Finalize immediately with whatever text we have (including pending)
        self._finalize_turn()

    def _on_user_turn_complete(self) -> None:
        """Called when turn manager signals completion (via callback)."""
        self._on_user_turn_complete_internal()

    def _finalize_turn(self) -> None:
        # Save the user text before clearing
        user_text = self._latest_user_text
        # Clear _latest_user_text NOW to prevent reuse
        self._latest_user_text = ""
        
        if not user_text or not user_text.strip():
            self.get_logger().info("[FINALIZE] No user text detected - robot will prompt user")
            # Robot takes turn to prompt/encourage user
            self._start_robot_turn(user_text=None)
        else:
            self.get_logger().info(f"[FINALIZE] User text detected: '{user_text}'")
            self._start_robot_turn(user_text=user_text)

    def destroy_node(self) -> bool:
        return super().destroy_node()


def main(args: Optional[List[str]] = None) -> None:
    rclpy.init(args=args)
    node = ConversationOrchestrator()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    finally:
        executor.remove_node(node)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
