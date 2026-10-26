from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """Launch mic_streamer, silero_vad and turn_end_detector for testing."""

    mic_node = Node(
        package='audio_processing',
        executable='mic_streamer',
        name='mic_streamer',
        output='screen',
    )

    vad_node = Node(
        package='audio_processing',
        executable='silero_vad',
        name='silero_vad',
        output='screen',
    )

    turn_node = Node(
        package='audio_processing',
        executable='turn_end_detector',
        name='turn_end_detector',
        output='screen',
    )

    return LaunchDescription([
        mic_node,
        vad_node,
        turn_node,
    ])
