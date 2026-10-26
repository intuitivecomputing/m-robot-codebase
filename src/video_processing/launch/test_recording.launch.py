#!/usr/bin/env python3
"""Launch file to test video+audio recording for 10 seconds.

This launch file:
1. Starts camera_streamer, mic_streamer, and video_saver nodes
2. Automatically starts recording after nodes are ready
3. Records for 10 seconds
4. Stops recording and saves to /root/data/
"""

from launch import LaunchDescription
from launch.actions import (
    ExecuteProcess,
    TimerAction,
    RegisterEventHandler,
    LogInfo,
)
from launch.event_handlers import OnProcessStart
from launch_ros.actions import Node


def generate_launch_description():
    # Output directory for recordings
    output_dir = "/root/data"

    # LED controller node (required by mic_streamer and camera_streamer)
    led_controller = Node(
        package="m_commons",
        executable="led_controller",
        name="led_controller",
        output="screen",
    )

    # Camera streamer node
    camera_streamer = Node(
        package="video_processing",
        executable="camera_streamer",
        name="camera_streamer",
        output="screen",
        parameters=[{"device_path": "/dev/video10"}],
    )

    # Microphone streamer node
    mic_streamer = Node(
        package="audio_processing",
        executable="mic_streamer",
        name="mic_streamer",
        output="screen",
    )

    # Video saver node with output directory parameter
    video_saver = Node(
        package="video_processing",
        executable="video_saver",
        name="video_saver",
        output="screen",
        parameters=[{"output_directory": output_dir}],
    )

    # Start recording after 3 seconds (give nodes time to initialize)
    start_recording = TimerAction(
        period=3.0,
        actions=[
            LogInfo(msg="Starting recording..."),
            ExecuteProcess(
                cmd=[
                    "ros2",
                    "service",
                    "call",
                    "/start_recording",
                    "std_srvs/srv/SetBool",
                    "{data: true}",
                ],
                output="screen",
            ),
        ],
    )

    # Stop recording after 13 seconds (3s init + 10s recording)
    stop_recording = TimerAction(
        period=13.0,
        actions=[
            LogInfo(msg="Stopping recording after 10 seconds..."),
            ExecuteProcess(
                cmd=[
                    "ros2",
                    "service",
                    "call",
                    "/stop_recording",
                    "std_srvs/srv/SetBool",
                    "{data: true}",
                ],
                output="screen",
            ),
        ],
    )

    return LaunchDescription(
        [
            led_controller,
            camera_streamer,
            mic_streamer,
            video_saver,
            start_recording,
            stop_recording,
        ]
    )
