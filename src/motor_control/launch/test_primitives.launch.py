from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    """Launch the motor controller for primitive testing.

    This launch file starts the `motor_controller` node so you can
    exercise the `execute_primitive` service from the command line.
    """
    return LaunchDescription([
        Node(
            package='motor_control',
            executable='motor_controller',
            name='motor_controller',
            output='screen'
        )
    ])
