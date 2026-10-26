from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='audio_processing',
            executable='google_tts',
            name='google_tts',
            output='screen'
        ),
        Node(
            package='audio_processing',
            executable='audio_playback',
            name='audio_playback',
            output='screen'
        )
    ])