#!/usr/bin/env python3
"""Simple diagnostic to monitor ASR outputs."""
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
import time


class ASRMonitor(Node):
    def __init__(self):
        super().__init__('asr_monitor')
        
        self.create_subscription(String, 'google_asr_text', 
                                lambda m: self.get_logger().info(f'[GOOGLE FINAL] {m.data}'), 10)
        self.create_subscription(String, 'google_asr_partial',
                                lambda m: self.get_logger().info(f'[GOOGLE PARTIAL] {m.data}'), 10)
        self.create_subscription(String, 'whisper_asr_text',
                                lambda m: self.get_logger().info(f'[WHISPER FINAL] {m.data}'), 10)
        self.create_subscription(Bool, 'vad_result',
                                lambda m: self.get_logger().info(f'[VAD] {m.data}'), 10)
        
        self.get_logger().info('ASR Monitor ready - watching all ASR outputs')


def main():
    rclpy.init()
    node = ASRMonitor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
