#!/usr/bin/env python3
"""Launch file for conversation logger node."""

from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    config_path = os.path.join(
        get_package_share_directory("m_logging"), "config", "config.yaml"
    )

    return LaunchDescription([
        Node(
            package="m_logging",
            executable="conversation_logger",
            name="conversation_logger",
            parameters=[config_path],
            output="screen",
        ),
    ])
