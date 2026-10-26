from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='audio_processing',
            executable='mic_streamer',
            name='mic_streamer',
            output='screen'
        ),
        Node(
            package='audio_processing',
            executable='silero_vad',
            name='silero_vad',
            output='screen'
        ),
        Node(
            package='audio_processing',
            executable='whisper_streaming_asr',
            name='whisper_streaming_asr',
            output='screen'
        ),
    ])
