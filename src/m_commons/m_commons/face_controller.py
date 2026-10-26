"""HTTP-based face expression controller ported into `m_commons`."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import requests
import rclpy
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from std_msgs.msg import String


@dataclass
class FaceControllerConfig:
    express_url: str = "http://localhost:3001/express"
    exec_func_url: str = "http://localhost:3001/exec-func"
    request_timeout: float = 2.0


class FaceController(Node):
    def __init__(self) -> None:
        super().__init__("face_controller")
        self._config = FaceControllerConfig(
            express_url=self.declare_parameter("express_url", FaceControllerConfig.express_url).value,
            exec_func_url=self.declare_parameter("exec_func_url", FaceControllerConfig.exec_func_url).value,
            request_timeout=self.declare_parameter("request_timeout", FaceControllerConfig.request_timeout).value,
        )
        self.create_subscription(String, "face_expression", self.listener_callback, 10)
        self.get_logger().info(
            "Face Controller ready (express=%s, exec_func=%s)" % (self._config.express_url, self._config.exec_func_url)
        )

    def listener_callback(self, msg: String) -> None:
        data = msg.data.strip()
        if data.startswith("exec:"):
            program_code = data[5:].strip()
            self._send_exec_func(program_code)
        else:
            self._send_expression(data)

    def _send_expression(self, expression: str) -> None:
        try:
            res = requests.post(
                self._config.express_url,
                json={"expression": expression},
                timeout=self._config.request_timeout,
            )
            self._handle_response(res, f"expression '{expression}'")
        except requests.exceptions.RequestException as e:
            self.get_logger().error(f"Failed to send expression: {e}")

    def _send_exec_func(self, program: str) -> None:
        try:
            res = requests.post(
                self._config.exec_func_url,
                json={"program": program},
                timeout=self._config.request_timeout,
            )
            self._handle_response(res, "exec-func program")
        except requests.exceptions.RequestException as e:
            self.get_logger().error(f"Failed to send exec-func: {e}")

    def _handle_response(self, response: requests.Response, context: str) -> None:
        if response.status_code == 200:
            self.get_logger().info(f"{context} sent successfully")
        else:
            self.get_logger().warning(f"Failed to send {context}: HTTP {response.status_code}")


def main(args: Optional[list[str]] = None) -> None:
    rclpy.init(args=args)
    node = FaceController()
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
