from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='video_processing',
            executable='camera_streamer',
            name='camera_streamer',
            output='screen'
        ),
        Node(
            package='audio_processing',
            executable='mic_streamer',
            name='mic_streamer',
            output='screen'
        ),
        Node(
            package='video_processing',
            executable='video_saver',
            name='video_saver',
            output='screen'
        ),
    ])
