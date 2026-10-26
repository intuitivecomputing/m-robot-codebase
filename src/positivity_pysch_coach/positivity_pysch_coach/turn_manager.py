"""Turn management module using VAD and audio_processing/turn_end_detector.

Handles user turn timing:
1. When user's turn starts: wait 5 seconds for speech detection
2. If no speech detected in 5s: robot re-takes the turn
3. If speech detected: wait until VAD returns False
4. When VAD silence begins: start 1.5 second timer
5. If audio_processing/turn_end_detector says turn is complete: terminate immediately
6. If turn_end_detector says turn is incomplete: wait full 1.5 seconds before robot takes turn
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Callable

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, String


class UserTurnState(Enum):
    """States during user turn management."""
    WAITING_FOR_SPEECH = auto()  # Initial 5s wait for any speech
    SPEECH_ACTIVE = auto()        # User is speaking
    VAD_SILENCE = auto()          # VAD detected silence, waiting for turn decision
    GRACE_PERIOD = auto()         # 250ms grace period after turn_end_detector says complete
    TURN_COMPLETE = auto()        # Turn ended


@dataclass
class TurnManagerConfig:
    """Configuration for turn management."""
    initial_wait_ms: float = 5000.0           # Wait 5s for speech to start
    vad_silence_timeout_ms: float = 1250.0    # Wait 1.5s after VAD silence
    turn_end_poll_interval_ms: float = 50.0   # Poll interval for checking turn end detector
    grace_period_ms: float = 500.0            # Grace period after turn_end_detector says complete


class TurnManager:
    """Manages user turn timing based on VAD and turn end detection."""

    def __init__(self, node: Node, config: Optional[TurnManagerConfig] = None) -> None:
        self._node = node
        self._config = config or TurnManagerConfig()
        self._active = False
        self._state = UserTurnState.WAITING_FOR_SPEECH
        self._start_time = 0.0
        self._last_vad_true_time = 0.0
        self._vad_silence_start_time = 0.0
        self._grace_period_start_time = 0.0
        self._last_turn_decision = None
        self._turn_end_detector_result = None
        self._has_asr_text_callback: Optional[Callable] = None
        self._on_turn_complete_callback: Optional[Callable] = None

        # Subscribe to VAD and turn end detector results
        self._node.create_subscription(Bool, "vad_result", self._on_vad, 10)
        self._node.create_subscription(String, "turn_completion", self._on_turn_completion, 10)

    def start(self, timestamp: float, on_complete_callback: Optional[Callable] = None, has_asr_text_callback: Optional[Callable] = None) -> None:
        """Start a new user turn.
        
        Args:
            timestamp: Current time in seconds
            on_complete_callback: Function to call when turn is complete
            has_asr_text_callback: Function to call to check if ASR text exists
        """
        self._active = True
        self._state = UserTurnState.WAITING_FOR_SPEECH
        self._start_time = timestamp
        self._last_vad_true_time = 0.0
        self._vad_silence_start_time = 0.0
        self._grace_period_start_time = 0.0
        self._last_turn_decision = None
        self._turn_end_detector_result = None
        self._has_asr_text_callback = has_asr_text_callback
        self._on_turn_complete_callback = on_complete_callback
        self._node.get_logger().info("[TURN_MANAGER] Started new user turn - waiting for speech (5s)")

    def stop(self) -> None:
        """Stop turn management."""
        self._active = False

    def update(self, timestamp: float) -> bool:
        """Update turn state and check if turn is complete.
        
        Args:
            timestamp: Current time in seconds
            
        Returns:
            True if user turn is complete, False otherwise
        """
        if not self._active:
            return False

        elapsed = timestamp - self._start_time
        elapsed_ms = elapsed * 1000.0

        if self._state == UserTurnState.WAITING_FOR_SPEECH:
            # Check if we've exceeded the initial wait
            if elapsed_ms >= self._config.initial_wait_ms:
                self._node.get_logger().info(
                    f"[TURN_MANAGER] No speech detected in {self._config.initial_wait_ms}ms - "
                    "turn complete (robot re-takes turn)"
                )
                self._state = UserTurnState.TURN_COMPLETE
                if self._on_turn_complete_callback:
                    self._on_turn_complete_callback()
                return True

        elif self._state == UserTurnState.SPEECH_ACTIVE:
            # Waiting for VAD to go false (speech to end)
            pass

        elif self._state == UserTurnState.VAD_SILENCE:
            # VAD silence detected, check turn end detector
            time_since_vad_silence = timestamp - self._vad_silence_start_time
            time_since_vad_silence_ms = time_since_vad_silence * 1000.0
            
            # Check if we've exceeded overall turn time limit (5s from when speech started)
            time_since_speech_started = timestamp - self._last_vad_true_time
            time_since_speech_started_ms = time_since_speech_started * 1000.0

            # Only use turn end detector if ASR has returned text
            # (prevents premature ending on non-speech audio)
            has_asr_text = self._has_asr_text_callback() if self._has_asr_text_callback else False
            if has_asr_text:
                # If turn end detector says turn is complete, enter grace period
                if self._turn_end_detector_result == "complete":
                    self._node.get_logger().info(
                        "[TURN_MANAGER] Turn end detector says COMPLETE - "
                        f"entering {self._config.grace_period_ms}ms grace period"
                    )
                    self._state = UserTurnState.GRACE_PERIOD
                    self._grace_period_start_time = timestamp
                    return False

                # If turn end detector says incomplete, keep waiting for user to continue
                # But enforce a maximum wait time from when speech started
                elif self._turn_end_detector_result == "incomplete":
                    if time_since_speech_started_ms >= self._config.initial_wait_ms:
                        self._node.get_logger().info(
                            "[TURN_MANAGER] Turn end detector says INCOMPLETE but 5s limit exceeded - "
                            "turn complete (timeout)"
                        )
                        self._state = UserTurnState.TURN_COMPLETE
                        if self._on_turn_complete_callback:
                            self._on_turn_complete_callback()
                        return True
                    else:
                        # Keep waiting for user to continue speaking
                        pass
            
            # If no turn end detector result yet, use fallback 1.5s timeout
            if self._turn_end_detector_result is None:
                if time_since_vad_silence_ms >= self._config.vad_silence_timeout_ms:
                    self._node.get_logger().info(
                        "[TURN_MANAGER] No turn end detector result and 1.5s silence - "
                        "turn complete (fallback timeout)"
                    )
                    self._state = UserTurnState.TURN_COMPLETE
                    if self._on_turn_complete_callback:
                        self._on_turn_complete_callback()
                    return True

        elif self._state == UserTurnState.GRACE_PERIOD:
            # In grace period - wait 250ms to see if VAD detects more speech
            time_since_grace_start = timestamp - self._grace_period_start_time
            time_since_grace_start_ms = time_since_grace_start * 1000.0

            if time_since_grace_start_ms >= self._config.grace_period_ms:
                self._node.get_logger().info(
                    f"[TURN_MANAGER] Grace period elapsed ({self._config.grace_period_ms}ms) - "
                    "terminating user turn"
                )
                self._state = UserTurnState.TURN_COMPLETE
                if self._on_turn_complete_callback:
                    self._on_turn_complete_callback()
                return True

        return False

    def _on_vad(self, msg: Bool) -> None:
        """Handle VAD state updates."""
        if not self._active:
            return

        now = self._node.get_clock().now().nanoseconds / 1e9

        if msg.data:  # VAD is True - speech detected
            if self._state == UserTurnState.WAITING_FOR_SPEECH:
                self._node.get_logger().info("[TURN_MANAGER] Speech detected - entering SPEECH_ACTIVE state")
                self._state = UserTurnState.SPEECH_ACTIVE
                self._last_vad_true_time = now
            elif self._state == UserTurnState.VAD_SILENCE:
                # Speech resumed after silence
                self._node.get_logger().info("[TURN_MANAGER] Speech resumed - back to SPEECH_ACTIVE state")
                self._state = UserTurnState.SPEECH_ACTIVE
                self._last_vad_true_time = now
                self._turn_end_detector_result = None
            elif self._state == UserTurnState.GRACE_PERIOD:
                # Speech resumed during grace period
                self._node.get_logger().info("[TURN_MANAGER] Speech resumed during grace period - back to SPEECH_ACTIVE state")
                self._state = UserTurnState.SPEECH_ACTIVE
                self._last_vad_true_time = now
                self._turn_end_detector_result = None
            elif self._state == UserTurnState.SPEECH_ACTIVE:
                self._last_vad_true_time = now
        else:  # VAD is False - no speech
            if self._state == UserTurnState.SPEECH_ACTIVE:
                self._node.get_logger().info("[TURN_MANAGER] VAD silence detected - starting 1.5s timer")
                self._state = UserTurnState.VAD_SILENCE
                self._vad_silence_start_time = now
                self._turn_end_detector_result = None

    def _on_turn_completion(self, msg: String) -> None:
        """Handle turn end detector results from audio_processing."""
        if not self._active:
            return

        # Parse the result from audio_processing/turn_end_detector
        # Expected format: "complete,<probability>" or "incomplete,<probability>"
        try:
            parts = msg.data.split(',')
            if len(parts) >= 1:
                result = parts[0].strip().lower()
                if result in ("complete", "incomplete"):
                    self._turn_end_detector_result = result
                    self._node.get_logger().info(
                        f"[TURN_MANAGER] Received turn end detector result: {result}"
                    )
        except Exception as e:
            self._node.get_logger().warning(f"[TURN_MANAGER] Failed to parse turn completion: {e}")

    def get_state(self) -> UserTurnState:
        """Get current turn state."""
        return self._state

    def get_config(self) -> TurnManagerConfig:
        """Get turn manager configuration."""
        return self._config


def main(args: Optional[list] = None) -> None:
    """Main entry point (for potential standalone use)."""
    rclpy.init(args=args)
    node = rclpy.create_node("turn_manager_test")
    config = TurnManagerConfig()
    manager = TurnManager(node, config)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutdown requested")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
