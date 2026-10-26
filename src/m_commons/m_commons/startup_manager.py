"""Startup manager orchestrating node readiness and waking animation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

import rclpy
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.task import Future
from std_msgs.msg import String

from m_interfaces.srv import NodeReady


@dataclass
class NodeReadinessTracker:
    """Track readiness state of dependent nodes."""

    required_nodes: Set[str] = field(default_factory=set)
    ready_nodes: Set[str] = field(default_factory=set)
    node_futures: Dict[str, Future] = field(default_factory=dict)

    def mark_ready(self, node_name: str) -> None:
        """Mark a node as ready."""
        self.ready_nodes.add(node_name)

    def all_ready(self) -> bool:
        """Check if all required nodes are ready."""
        return self.required_nodes.issubset(self.ready_nodes)

    def get_pending_nodes(self) -> Set[str]:
        """Get names of nodes still pending readiness."""
        return self.required_nodes - self.ready_nodes

    def reset(self) -> None:
        """Reset readiness state."""
        self.ready_nodes.clear()
        self.node_futures.clear()


class ReadinessPoller:
    """Poll required nodes for readiness via NodeReady service."""

    def __init__(self, node: Node, required_nodes: List[str]) -> None:
        """Initialize readiness poller.

        Args:
            node: ROS node for creating service clients
            required_nodes: List of node names to poll for readiness
        """
        self._node = node
        self._required_nodes = required_nodes
        self._clients: Dict[str, rclpy.clients.Client] = {}
        self._create_clients()

    def _create_clients(self) -> None:
        """Create NodeReady service clients for all required nodes."""
        for node_name in self._required_nodes:
            service_name = f"/{node_name}/node_ready"
            client = self._node.create_client(NodeReady, service_name)
            self._clients[node_name] = client
            self._node.get_logger().debug(f"Created client for {service_name}")

    def poll_node(self, node_name: str) -> Future:
        """Poll a single node for readiness.

        Args:
            node_name: Name of the node to poll

        Returns:
            Future that completes when readiness response is received
        """
        if node_name not in self._clients:
            raise ValueError(f"No client for node: {node_name}")

        client = self._clients[node_name]
        if not client.wait_for_service(timeout_sec=0.5):
            self._node.get_logger().debug(f"Service not available for {node_name}")
            return Future()

        request = NodeReady.Request()
        request.node_name = node_name
        return client.call_async(request)

    def poll_all(self) -> Dict[str, Future]:
        """Poll all required nodes concurrently.

        Returns:
            Dictionary mapping node names to their poll Futures
        """
        futures = {}
        for node_name in self._required_nodes:
            try:
                futures[node_name] = self.poll_node(node_name)
            except ValueError:
                self._node.get_logger().warning(f"Could not poll {node_name}")
        return futures


class AnimationController:
    """Manage waking animation during startup."""

    WAKING_ANIMATION = "exec:waking_up"

    def __init__(self, node: Node) -> None:
        """Initialize animation controller.

        Args:
            node: ROS node for publishing animation commands
        """
        self._node = node
        self._animation_pub = node.create_publisher(String, "face_expression", 10)

    def play_waking_animation(self) -> None:
        """Publish waking animation command."""
        msg = String(data=self.WAKING_ANIMATION)
        self._animation_pub.publish(msg)
        self._node.get_logger().info("Published waking animation")

    def stop_animation(self) -> None:
        """Stop animation and reset to neutral."""
        msg = String(data="reset")
        self._animation_pub.publish(msg)
        self._node.get_logger().info("Reset animation to neutral")


class StartupStateMachine:
    """Manage startup sequence state transitions."""

    class State:
        """Startup states."""
        INITIALIZING = "INITIALIZING"
        WAITING_FOR_NODES = "WAITING_FOR_NODES"
        ANIMATION_COMPLETE = "ANIMATION_COMPLETE"
        READY = "READY"
        FAILED = "FAILED"

    def __init__(self, logger) -> None:
        """Initialize state machine.

        Args:
            logger: ROS logger for status messages
        """
        self._state = self.State.INITIALIZING
        self._logger = logger

    def transition(self, new_state: str) -> None:
        """Transition to a new state."""
        old_state = self._state
        self._state = new_state
        self._logger.info(f"[STARTUP] {old_state} → {new_state}")

    def get_state(self) -> str:
        """Get current state."""
        return self._state

    def is_ready(self) -> bool:
        """Check if startup completed successfully."""
        return self._state == self.State.READY


class StartupManager(Node):
    """Orchestrate startup sequence: poll nodes, show animation, signal readiness."""

    def __init__(self) -> None:
        """Initialize startup manager node."""
        super().__init__("startup_manager")

        # Configuration
        self.declare_parameter("required_nodes", [
            "face_controller",
            "expression_controller",
            "conversation_orchestrator",
            "audio_playback",
        ])
        self.declare_parameter("polling_interval_ms", 500)
        self.declare_parameter("max_startup_time_s", 30.0)
        self.declare_parameter("poll_timeout_s", 2.0)

        required_nodes: List[str] = self.get_parameter("required_nodes").value
        polling_interval_ms: float = self.get_parameter("polling_interval_ms").value
        max_startup_time_s: float = self.get_parameter("max_startup_time_s").value

        # Initialize components
        self._state_machine = StartupStateMachine(self.get_logger())
        self._readiness_tracker = NodeReadinessTracker(required_nodes=set(required_nodes))
        self._poller = ReadinessPoller(self, required_nodes)
        self._animation = AnimationController(self)

        # Timing
        self._polling_interval = polling_interval_ms / 1000.0
        self._max_startup_time = max_startup_time_s
        self._startup_start_time = self.get_clock().now().nanoseconds / 1e9

        # State tracking
        self._active_polls: Dict[str, Future] = {}
        self._animation_started = False

        # Service for external readiness checking
        self.create_service(NodeReady, "startup_manager/node_ready", self._handle_ready_check)

        # Start polling loop
        self.create_timer(self._polling_interval, self._polling_loop)

        self._state_machine.transition(self.State.WAITING_FOR_NODES)
        self.get_logger().info(
            f"Startup manager initialized - waiting for {len(required_nodes)} nodes"
        )

    def _polling_loop(self) -> None:
        """Main polling loop checking node readiness."""
        if not self._state_machine.get_state() == self.State.WAITING_FOR_NODES:
            return

        # Start animation on first poll
        if not self._animation_started:
            self._animation.play_waking_animation()
            self._animation_started = True

        # Check timeout
        elapsed = self.get_clock().now().nanoseconds / 1e9 - self._startup_start_time
        if elapsed > self._max_startup_time:
            self.get_logger().error(
                f"Startup timeout after {elapsed:.1f}s. "
                f"Pending nodes: {self._readiness_tracker.get_pending_nodes()}"
            )
            self._state_machine.transition(self.State.FAILED)
            return

        # Process completed polls
        completed_polls = [name for name, fut in self._active_polls.items() if fut.done()]
        for node_name in completed_polls:
            self._process_poll_result(node_name, self._active_polls.pop(node_name))

        # Start new polls for pending nodes
        for node_name in self._readiness_tracker.get_pending_nodes():
            if node_name not in self._active_polls:
                future = self._poller.poll_node(node_name)
                if future.done():
                    self._process_poll_result(node_name, future)
                else:
                    self._active_polls[node_name] = future

        # Check if all nodes are ready
        if self._readiness_tracker.all_ready():
            self._on_all_nodes_ready()

    def _process_poll_result(self, node_name: str, future: Future) -> None:
        """Process result from a single node readiness poll.

        Args:
            node_name: Name of polled node
            future: Completed Future from poll
        """
        try:
            response = future.result()
            if response.ready:
                self._readiness_tracker.mark_ready(node_name)
                self.get_logger().debug(f"Node ready: {node_name}")
            else:
                self.get_logger().debug(f"Node not ready: {node_name} ({response.message})")
        except Exception as exc:
            self.get_logger().debug(f"Poll failed for {node_name}: {exc}")

    def _on_all_nodes_ready(self) -> None:
        """Handle completion of all nodes becoming ready."""
        self._animation.stop_animation()
        self._state_machine.transition(self.State.ANIMATION_COMPLETE)
        self._state_machine.transition(self.State.READY)

        elapsed = self.get_clock().now().nanoseconds / 1e9 - self._startup_start_time
        self.get_logger().info(f"All nodes ready after {elapsed:.1f}s - startup complete")

    def _handle_ready_check(
        self, request: NodeReady.Request, response: NodeReady.Response
    ) -> NodeReady.Response:
        """Service handler for external readiness checks.

        Args:
            request: Request with node_name (unused for startup manager itself)
            response: Response to populate

        Returns:
            Response indicating startup manager readiness
        """
        response.ready = self._state_machine.is_ready()
        response.message = self._state_machine.get_state()
        return response

    def destroy_node(self) -> bool:
        """Cleanup on shutdown."""
        self._animation.stop_animation()
        return super().destroy_node()


def main(args: Optional[List[str]] = None) -> None:
    """Entry point for startup manager node."""
    rclpy.init(args=args)
    node = StartupManager()
    executor = MultiThreadedExecutor()
    executor.add_node(node)

    try:
        executor.spin()
    finally:
        executor.remove_node(node)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":  # pragma: no cover
    main()
