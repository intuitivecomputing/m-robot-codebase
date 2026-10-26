import time
from collections import deque
from threading import Thread, Lock

import rclpy
from rclpy.node import Node

from motor_control.motor_executor import MotorExecutor
from m_interfaces.srv import SetPose, PlayPoseSequence, ExecutePrimitive
from motor_control.primitives import (
    beat, open_encourage, invite, invite_double, point_arm,
    body_shift, head_tilt, ack_nod, slow_nod, ReturnToNeutral
)
import json
import os
import inspect


ROBOT_CFG = {
    "motors": {
        "base_rotation": {"channel": 0,  "range": [-120, 120], "offset": 135, "servo_range": [0, 270]},
        "head_pitch":    {"channel": 2,  "range": [-40, 40],   "offset": 40,  "servo_range": [0, 270]},
        "head_yaw":      {"channel": 4,  "range": [-90, 90],   "offset": 120, "servo_range": [0, 270]},
        "arm_left":      {"channel": 8,  "range": [-45, 135],  "offset": 135, "flip": True,  "servo_range": [0, 180]},
        "arm_right":     {"channel": 10, "range": [-45, 135],  "offset": 45,  "servo_range": [0, 180]},
    }
}
# ROBOT_CFG = {
#     "motors": {
#         "base_rotation": {"channel": 0,  "range": [-120, 120], "offset": 145, "servo_range": [0, 270]},
#         "head_pitch":    {"channel": 2,  "range": [-40, 40],   "offset": 50,  "servo_range": [0, 270]},
#         "head_yaw":      {"channel": 4,  "range": [-90, 90],   "offset": 150, "servo_range": [0, 270]},
#         "arm_left":      {"channel": 8,  "range": [-45, 135],  "offset": 135, "flip": True,  "servo_range": [0, 180]},
#         "arm_right":     {"channel": 10, "range": [-45, 135],  "offset": 45,  "servo_range": [0, 180]},
#     }
# }


class MotorController(Node):
    """Low‑level motor node exposing two services:

    • ``set_pose``            – legacy single‑pose interface (kept for backward compatibility)
    • ``play_pose_sequence``  – NEW flattened‑array interface for queued key‑frames

    The sequence service accepts 1‑D arrays only (``at``, ``duration``, ``joint_angles``)
    to stay within .srv constraints while still supporting any number of key‑frames.
    """

    # ─────────────────────────────────────────────────────────────────────
    def __init__(self):
        super().__init__('motor_controller')
        
        config_path = "/root/m_ws/src/motor_control/config/config.json"
        try:
            with open(config_path, 'r') as f:
                robot_cfg_from_file = json.load(f)
                ROBOT_CFG = robot_cfg_from_file
                self.get_logger().info(f'Loaded robot config from {config_path}')
        except Exception as e:
            self.get_logger().warn(f'Failed to load config.json, using default ROBOT_CFG: {e}')


        # Low‑level executor
        self.motor_executor = MotorExecutor(ROBOT_CFG)

        # Services
        self.srv_pose = self.create_service(SetPose,          'set_pose',           self._set_pose_cb)
        self.srv_seq  = self.create_service(PlayPoseSequence, 'play_pose_sequence', self._play_seq_cb)
        self.srv_primitive = self.create_service(ExecutePrimitive, 'execute_primitive', self._execute_primitive_cb)

        # Internal queue + worker
        self._queue: deque[PlayPoseSequence.Request] = deque()
        self._lock = Lock()
        self._worker = Thread(target=self._run_queue, daemon=True)
        self._worker.start()

        # Primitive function mapping
        self.primitives = {
            'beat': beat,
            'open_encourage': open_encourage,
            'invite': invite,
            'invite_double': invite_double,
            'point_arm': point_arm,
            'body_shift': body_shift,
            'head_tilt': head_tilt,
            'ack_nod': ack_nod,
            'slow_nod': slow_nod,
            'ReturnToNeutral': ReturnToNeutral,
        }

        self.get_logger().info('Motor Controller ready → services: {set_pose, play_pose_sequence, execute_primitive}')

    # ─────────────────────────────────────────────────────────────────────
    #  set_pose (legacy)
    # ─────────────────────────────────────────────────────────────────────
    def _set_pose_cb(self, request: SetPose.Request, response: SetPose.Response):
        try:
            if len(request.joint_names) != len(request.joint_angles):
                raise ValueError('joint_names and joint_angles length mismatch')

            pose     = dict(zip(request.joint_names, request.joint_angles))
            duration = float(request.duration)
            self.motor_executor.set_pose(pose, duration=duration)
            response.success = True
            response.message = 'Pose command accepted'
        except Exception as e:
            response.success = False
            response.message = str(e)
            self.get_logger().error(f'Failed to set pose: {e}')
        return response

    # ─────────────────────────────────────────────────────────────────────
    #  execute_primitive (primitive motion functions)
    # ─────────────────────────────────────────────────────────────────────
    def _execute_primitive_cb(self, request: ExecutePrimitive.Request, response: ExecutePrimitive.Response):
        try:
            function_name = request.function_name
            param_names = request.param_names
            param_values = request.param_values
            start_at = float(request.start_at)

            # Check if function exists
            if function_name not in self.primitives:
                raise ValueError(f'Unknown primitive function: {function_name}')

            # Get the function
            func = self.primitives[function_name]
            
            # Check parameter count
            if len(param_names) != len(param_values):
                raise ValueError('param_names and param_values length mismatch')

            # Get function signature to understand expected parameters
            sig = inspect.signature(func)
            expected_params = list(sig.parameters.keys())
            
            # Build arguments dictionary
            kwargs = {'start_at': start_at}
            
            # Convert parameter values to appropriate types
            for i, (name, value_str) in enumerate(zip(param_names, param_values)):
                if name not in expected_params:
                    raise ValueError(f'Parameter {name} not expected for function {function_name}')
                
                # Type conversion based on parameter name patterns
                if name in ['amplitude', 'angle', 'start_at']:
                    kwargs[name] = float(value_str)
                elif name in ['cycles']:
                    kwargs[name] = int(value_str)
                elif name in ['speed']:
                    kwargs[name] = value_str.lower()  # Speed is a string literal
                elif name in ['side']:
                    kwargs[name] = value_str.lower()  # Side is a string literal
                else:
                    # Default to string
                    kwargs[name] = value_str

            # Call the primitive function
            self.get_logger().info(f'Executing primitive {function_name} with args: {kwargs}')
            keyframes = func(**kwargs)
            
            # Convert keyframes to PlayPoseSequence format
            if not keyframes:
                raise ValueError(f'Primitive function {function_name} returned empty keyframes')
                
            # Extract data from keyframes
            at_times = []
            durations = []
            all_joint_names = set()
            
            # Collect all unique joint names
            for kf in keyframes:
                all_joint_names.update(kf['pose'].keys())
            
            joint_names = sorted(list(all_joint_names))
            joint_angles = []
            
            # Build the flattened arrays
            for kf in keyframes:
                at_times.append(kf['at'])
                durations.append(kf['duration'])
                
                # Add joint angles in consistent order
                for joint_name in joint_names:
                    angle = kf['pose'].get(joint_name, 0.0)  # Default to 0 if joint not in this keyframe
                    joint_angles.append(angle)
            
            # Create and queue the pose sequence request
            seq_request = PlayPoseSequence.Request()
            seq_request.at = at_times
            seq_request.duration = durations
            seq_request.joint_names = joint_names
            seq_request.joint_angles = joint_angles
            
            # Queue the sequence for execution
            with self._lock:
                self._queue.append(seq_request)
            
            response.success = True
            response.message = f'Primitive {function_name} queued with {len(keyframes)} keyframes'
            self.get_logger().info(f'Queued primitive {function_name} with {len(keyframes)} keyframes')
            
        except Exception as e:
            response.success = False
            response.message = str(e)
            self.get_logger().error(f'Failed to execute primitive {function_name}: {e}')
        
        return response

    # ─────────────────────────────────────────────────────────────────────
    #  play_pose_sequence (queued key‑frames)
    # ─────────────────────────────────────────────────────────────────────
    def _play_seq_cb(self, request: PlayPoseSequence.Request, response: PlayPoseSequence.Response):
        try:
            N = len(request.at)
            J = len(request.joint_names)
            if N == 0:
                raise ValueError('"at" array must contain at least one element')
            if J == 0:
                raise ValueError('joint_names must not be empty')
            if len(request.duration) != N:
                raise ValueError('duration length must equal at length')
            if len(request.joint_angles) != N * J:
                raise ValueError('joint_angles length must be len(at) * len(joint_names)')

            with self._lock:
                self._queue.append(request)
            response.success = True
            response.message = 'Sequence queued'
            self.get_logger().info(f'Queued sequence with {N} key‑frames')
        except Exception as e:
            response.success = False
            response.message = str(e)
            self.get_logger().warn(f'play_pose_sequence rejected: {e}')
        return response

    # ─────────────────────────────────────────────────────────────────────
    #  Worker: execute queued sequences with accurate timing
    # ─────────────────────────────────────────────────────────────────────
    def _run_queue(self):
        while rclpy.ok():
            if not self._queue:
                time.sleep(0.01)
                continue

            with self._lock:
                req = self._queue.popleft()

            N = len(req.at)
            J = len(req.joint_names)
            t0 = time.monotonic()

            for i in range(N):
                # Wait until scheduled start time
                wait = t0 + req.at[i] - time.monotonic()
                if wait > 0:
                    time.sleep(wait)

                start = i * J
                angles_slice = req.joint_angles[start : start + J]
                pose = {joint: angles_slice[j] for j, joint in enumerate(req.joint_names)}
                duration = req.duration[i]

                self.get_logger().debug(
                    f'Key‑frame {i+1}/{N} – pose {pose} (dur {duration:.2f}s)')
                try:
                    self.motor_executor.set_pose(pose, duration=duration)
                except Exception as e:
                    self.get_logger().error(f'MotorExecutor error: {e}')
                    break  # abort the rest of this sequence on error

# ─────────────────────────────────────────────────────────────────────
#  main()
# ─────────────────────────────────────────────────────────────────────

def main(args=None):
    rclpy.init(args=args)
    node = MotorController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()