from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='motor_control',
            executable='motor_controller',
            name='motor_controller',
            output='screen'
        )
    ])
