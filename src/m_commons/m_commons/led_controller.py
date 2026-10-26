#!/usr/bin/env python3
"""ROS 2 LED Controller Node.

Controls LED via GPIO on Raspberry Pi.
Provides a service to turn LED on/off.
"""
from typing import Optional

import rclpy
from rclpy.node import Node


try:
    import lgpio
    HAS_LGPIO = True
except ImportError:
    HAS_LGPIO = False

from m_interfaces.srv import ControlLED



class LEDController(Node):
    LED_PIN = 24

    def __init__(self) -> None:
        super().__init__('led_controller')

        if HAS_LGPIO:
            try:
                self._h = lgpio.gpiochip_open(0)
                lgpio.gpio_claim_output(self._h, self.LED_PIN)
                lgpio.gpio_write(self._h, self.LED_PIN, 0)
                self.get_logger().info(f'LED initialized on GPIO pin {self.LED_PIN} (lgpio)')
            except Exception as e:
                self.get_logger().error(f'Failed to initialize lgpio: {e}')
                raise
        else:
            self.get_logger().warn('lgpio not available - running in simulation mode')

        self.service = self.create_service(
            ControlLED, 'control_led', self.control_led_callback
        )
        self.get_logger().info('LED Control service is ready')

    def control_led_callback(
        self, request: ControlLED.Request, response: ControlLED.Response
    ) -> ControlLED.Response:
        try:
            if HAS_LGPIO:
                lgpio.gpio_write(self._h, self.LED_PIN, 1 if request.enabled else 0)
                self.get_logger().info(f'LED turned {"ON" if request.enabled else "OFF"}')
            else:
                state = 'ON' if request.enabled else 'OFF'
                self.get_logger().info(f'LED {state} (simulation mode)')

            response.success = True
            response.message = 'LED control successful'
        except Exception as e:
            response.success = False
            response.message = f'LED control failed: {str(e)}'
            self.get_logger().error(response.message)
        return response

    def destroy_node(self) -> bool:
        if HAS_LGPIO:
            try:
                lgpio.gpio_write(self._h, self.LED_PIN, 0)
                lgpio.gpiochip_close(self._h)
            except Exception as e:
                self.get_logger().error(f'Error during lgpio cleanup: {e}')
        return super().destroy_node()


def main(args: Optional[list[str]] = None) -> None:
    """Main entry point."""
    rclpy.init(args=args)
    node = LEDController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutdown request (Ctrl-C).')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
