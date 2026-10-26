"""Response delivery orchestration (migrated to positivity_pysch_coach).

Coordinates TTS synthesis, audio playback, and real-time behavior execution
(expressions and body sequences). Facial expressions are published via topic,
body sequences are scheduled as timed SetPose service calls.
"""

from __future__ import annotations

import base64
import io
import json
from typing import Callable, Dict, List

from pydub import AudioSegment
from rclpy.action import ActionClient
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.node import Node
from rclpy.task import Future
from rclpy.timer import Timer
from std_msgs.msg import Bool, String

from m_interfaces.action import AudioPlay
from m_interfaces.srv import TextToSpeech, SetPose

from positivity_pysch_coach.conversation_models import CoachReply


class ResponseDelivery:
    def __init__(self, node: Node) -> None:
        self._node = node
        self._tts_client = node.create_client(TextToSpeech, "tts_synthesize")
        self._pose_client = node.create_client(SetPose, "set_pose")
        self._callback_group = ReentrantCallbackGroup()
        self._audio_client = ActionClient(node, AudioPlay, "audio_play", callback_group=self._callback_group)
        self._robot_pub = node.create_publisher(Bool, "robot_speaking", 10)
        self._face_pub = node.create_publisher(String, "face_expression", 10)
        self._active_timers: List[Timer] = []
        self._pose_futures: List[Future] = []

    def speak(self, reply: CoachReply) -> Future:
        result_future: Future = Future()

        if not self._tts_client.wait_for_service(timeout_sec=1.0):
            exc = RuntimeError("TTS service unavailable")
            result_future.set_exception(exc)
            return result_future

        # Generate TTS requests for each utterance
        tts_futures = []
        for utterance_item in reply.utterances:
            request = TextToSpeech.Request()
            request.text = utterance_item.get("utterance", "")
            tts_futures.append(self._tts_client.call_async(request))

        self._process_utterances_pipelined(reply, result_future, tts_futures)
        return result_future

    def _process_utterances_pipelined(self, reply: CoachReply, result_future: Future, tts_futures: List[Future]) -> None:
        utterances = reply.utterances

        if not utterances:
            result_future.set_result(True)
            return

        self._robot_pub.publish(Bool(data=True))
        self._process_single_utterance(0, utterances, tts_futures, result_future)

    def _process_single_utterance(self, index: int, utterances: List[dict], tts_futures: List[Future], result_future: Future) -> None:
        tts_future = tts_futures[index]
        tts_future.add_done_callback(
            lambda fut: self._on_utterance_tts_completed(fut, index, utterances, tts_futures, result_future)
        )

    def _on_utterance_tts_completed(self, future: Future, index: int, utterances: List[dict], tts_futures: List[Future], result_future: Future) -> None:
        try:
            response = future.result()
            if not response.success:
                raise RuntimeError(f"TTS synthesis failed: {response.error_message}")
            wav_bytes = self._mp3_to_wav(response.audio_base64)
            self._play_utterance_audio(wav_bytes, index, utterances, tts_futures, result_future)
        except Exception as exc:
            self._node.get_logger().error(f"TTS failed for utterance {index}: {exc}")
            self._robot_pub.publish(Bool(data=False))
            result_future.set_exception(exc)

    def _play_utterance_audio(self, audio_data: bytes, index: int, utterances: List[dict], tts_futures: List[Future], result_future: Future) -> None:
        if not self._audio_client.wait_for_server(timeout_sec=1.0):
            exc = RuntimeError("Audio playback action unavailable")
            self._robot_pub.publish(Bool(data=False))
            result_future.set_exception(exc)
            return

        utterance_item = utterances[index]
        
        # Calculate audio duration for gesture timing
        audio_duration = self._calculate_audio_duration(audio_data)
        
        # Execute expression and gesture with timing
        self._execute_utterance_behavior(utterance_item, audio_duration)
        
        # Start talking animation when audio begins
        self._execute_expression("talking")

        goal = AudioPlay.Goal()
        goal.data = audio_data

        send_future = self._audio_client.send_goal_async(goal)
        send_future.add_done_callback(
            lambda goal_future: self._on_utterance_audio_goal(
                goal_future, index, utterances, tts_futures, result_future
            )
        )

    def _on_utterance_audio_goal(self, goal_future: Future, index: int, utterances: List[dict], tts_futures: List[Future], result_future: Future) -> None:
        try:
            goal_handle = goal_future.result()
            if not goal_handle.accepted:
                raise RuntimeError("Audio goal rejected")

            result = goal_handle.get_result_async()
            result.add_done_callback(
                lambda fut: self._on_utterance_audio_result(
                    fut, index, utterances, tts_futures, result_future
                )
            )
        except Exception as exc:
            self._node.get_logger().error(f"Audio goal failed for utterance {index}: {exc}")
            self._robot_pub.publish(Bool(data=False))
            result_future.set_exception(exc)

    def _on_utterance_audio_result(self, future: Future, index: int, utterances: List[dict], tts_futures: List[Future], result_future: Future) -> None:
        try:
            future.result()
            
            # Stop talking animation
            self._execute_expression("stopTalking")
            
            is_last = (index + 1 >= len(utterances))
            
            if is_last:
                # Final utterance complete - wait 1 second then reset to neutral
                self._create_oneshot_timer(1.0, lambda: self._final_reset())
                self._robot_pub.publish(Bool(data=False))
                result_future.set_result(True)
            else:
                # Process next utterance
                next_index = index + 1
                self._process_single_utterance(next_index, utterances, tts_futures, result_future)
        except Exception as exc:
            self._node.get_logger().error(f"Audio playback failed for utterance {index}: {exc}")
            self._execute_expression("stopTalking")
            self._robot_pub.publish(Bool(data=False))
            result_future.set_exception(exc)

    def _calculate_audio_duration(self, audio_data: bytes) -> float:
        """Calculate duration of audio data in seconds."""
        try:
            audio = AudioSegment.from_file(io.BytesIO(audio_data), format="wav")
            return len(audio) / 1000.0  # Duration in seconds
        except Exception as e:
            self._node.get_logger().warning(f"Failed to calculate audio duration: {e}")
            return 2.0  # Default fallback duration

    def _execute_utterance_behavior(self, utterance_item: dict, audio_duration: float) -> None:
        """Execute facial expression and gesture with timing for an utterance.
        
        Args:
            utterance_item: Dictionary with 'utterance', 'expression', 'gesture' fields
            audio_duration: Duration of the audio in seconds
        """
        self._node.get_logger().info(f"[BEHAVIOR] Executing behavior for utterance, audio_duration={audio_duration:.2f}s")
        self._node.get_logger().info(f"[BEHAVIOR] utterance_item={utterance_item}")
        
        # Clear any ongoing body animations
        self._clear_body_timers()
        
        # Parse and execute expression
        expression_str = utterance_item.get("expression", "neutral:low")
        self._node.get_logger().info(f"[BEHAVIOR] Executing expression: {expression_str}")
        self._execute_parsed_expression(expression_str)
        
        # Parse and execute gesture with timing
        gesture_str = utterance_item.get("gesture", "")
        self._node.get_logger().info(f"[BEHAVIOR] Gesture string: {gesture_str}")
        if gesture_str and gesture_str != "null":
            self._node.get_logger().info(f"[BEHAVIOR] Executing gesture with timing: {gesture_str}")
            self._execute_gesture_with_timing(gesture_str, audio_duration)
        else:
            self._node.get_logger().info(f"[BEHAVIOR] No gesture to execute")

    def _execute_parsed_expression(self, expression_str: str) -> None:
        """Parse and execute expression string (e.g., 'happy:low').
        
        Args:
            expression_str: Expression string in format 'emotion:intensity'
        """
        parts = expression_str.split(":")
        if len(parts) >= 1:
            expression = parts[0]
            # intensity = parts[1] if len(parts) > 1 else "low"
            # For now, just use the base expression
            if expression and expression != "neutral":
                self._execute_expression(expression)

    def _execute_gesture_with_timing(self, gesture_str: str, audio_duration: float) -> None:
        """Execute gesture with timing (start, mid, end) relative to audio duration.
        
        Args:
            gesture_str: Gesture string in format 'primitive_name:timing'
            audio_duration: Duration of the audio in seconds
        """
        parts = gesture_str.split(":")
        if len(parts) < 2:
            self._node.get_logger().warning(f"[GESTURE] Invalid gesture format: {gesture_str}")
            return
        
        primitive_name = parts[0]
        timing = parts[1]
        
        # Calculate timing offset based on timing marker
        if timing == "start":
            delay = 0.0
        elif timing == "mid":
            delay = audio_duration / 2.0
        elif timing == "end":
            delay = max(0.0, audio_duration - 1.5)  # 1.5 seconds before end
        else:
            delay = 0.0
        
        self._node.get_logger().info(f"[GESTURE] Scheduling primitive '{primitive_name}' at timing '{timing}' (delay={delay:.2f}s)")
        
        # Import and execute the primitive
        self._execute_primitive_with_delay(primitive_name, delay)

    def _execute_primitive_with_delay(self, primitive_name: str, delay: float) -> None:
        """Execute a primitive gesture after a delay.
        
        Args:
            primitive_name: Name of the primitive function
            delay: Delay in seconds before executing
        """
        try:
            # Import primitives module
            from motor_control import primitives
            
            # Get the primitive function
            if not hasattr(primitives, primitive_name):
                self._node.get_logger().warning(f"Unknown primitive: {primitive_name}")
                return
            
            primitive_func = getattr(primitives, primitive_name)
            
            # Schedule the primitive execution
            self._create_oneshot_timer(delay, lambda: self._execute_primitive(primitive_func))
        except ImportError as e:
            self._node.get_logger().error(f"Failed to import primitives module: {e}")
        except Exception as e:
            self._node.get_logger().error(f"Failed to execute primitive {primitive_name}: {e}")

    def _execute_primitive(self, primitive_func) -> None:
        """Execute a primitive gesture function.
        
        Args:
            primitive_func: Primitive function from motor_control.primitives
        """
        try:
            # Call the primitive function to get the pose stages
            stages = primitive_func(start_at=0.0)
            
            # Execute each stage
            for stage in stages:
                pose = stage.get("pose", {})
                duration = float(stage.get("duration", 1.0))
                offset = float(stage.get("at", 0.0))
                
                if pose:
                    self._create_oneshot_timer(offset, lambda p=pose, d=duration: self._send_pose(p, d))
        except Exception as e:
            self._node.get_logger().error(f"Failed to execute primitive: {e}")

    def _final_reset(self) -> None:
        """Reset to neutral after final utterance."""
        try:
            self._execute_expression("reset")
            self._reset_body_to_neutral()
        except Exception as e:
            self._node.get_logger().error(f"Error during final reset: {e}")

    def _execute_expression(self, expression: str) -> None:
        """Publish facial expression to face controller.
        
        Args:
            expression: Expression name to execute
        """
        msg = String()
        msg.data = expression
        self._face_pub.publish(msg)
        self._node.get_logger().info(f"Publishing expression: {expression}")

    def _send_pose(self, joints: Dict[str, float], duration: float) -> None:
        """Send a pose command to the SetPose service.
        
        Args:
            joints: Dictionary mapping joint names to target angles
            duration: Time in seconds to reach the pose
        """
        if not joints:
            return
        if not self._pose_client.wait_for_service(timeout_sec=1.0):
            self._node.get_logger().warning("set_pose service unavailable; skipping pose command")
            return
        
        request = SetPose.Request()
        request.joint_names = list(joints.keys())
        request.joint_angles = [float(value) for value in joints.values()]
        request.duration = float(duration)
        
        future = self._pose_client.call_async(request)
        self._pose_futures.append(future)
        future.add_done_callback(lambda f: self._on_pose_result(f, joints))

    def _on_pose_result(self, future: Future, joints: Dict[str, float]) -> None:
        """Handle SetPose service response."""
        try:
            response = future.result()
            if response.success:
                self._node.get_logger().debug(f"Pose executed: {joints}")
            else:
                self._node.get_logger().warning(f"Pose failed: {response.message}")
        except Exception as e:
            self._node.get_logger().error(f"Pose service call failed: {e}")
        finally:
            if future in self._pose_futures:
                self._pose_futures.remove(future)

    def _reset_body_to_neutral(self) -> None:
        """Send neutral pose to all joints."""
        neutral_pose = {
            "base_rotation": 0.0,
            "head_pitch": 0.0,
            "arm_left": 0.0,
            "arm_right": 0.0,
            "head_yaw": 0.0,
        }
        self._send_pose(neutral_pose, duration=1.0)

    def _create_oneshot_timer(self, delay: float, callback: Callable[[], None]) -> None:
        """Create a timer that fires once after delay and auto-cancels.
        
        Args:
            delay: Delay in seconds before firing
            callback: Function to call when timer fires
        """
        timer_ref: Timer | None = None

        def wrapper() -> None:
            try:
                callback()
            finally:
                if timer_ref is not None:
                    timer_ref.cancel()
                    if timer_ref in self._active_timers:
                        self._active_timers.remove(timer_ref)

        timer_ref = self._node.create_timer(delay, wrapper, callback_group=self._callback_group)
        self._active_timers.append(timer_ref)

    def _clear_body_timers(self) -> None:
        """Cancel all active body animation timers."""
        for timer in list(self._active_timers):
            timer.cancel()
        self._active_timers.clear()

    @staticmethod
    def _mp3_to_wav(audio_base64: str) -> bytes:
        raw_bytes = base64.b64decode(audio_base64.split(",")[-1])
        audio = AudioSegment.from_file(io.BytesIO(raw_bytes), format="mp3")
        buffer = io.BytesIO()
        audio.export(buffer, format="wav")
        return buffer.getvalue()
