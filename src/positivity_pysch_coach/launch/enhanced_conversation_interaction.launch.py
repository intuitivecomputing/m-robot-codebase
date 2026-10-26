#!/usr/bin/env python3
"""Launch file for enhanced conversation interaction with turn management."""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """Generate launch description for enhanced conversation interaction."""
    return LaunchDescription([
        # Audio input pipeline
        Node(
            package='audio_processing',
            executable='mic_streamer',
            name='mic_streamer',
            output='screen'
        ),
        
        # Voice Activity Detection
        Node(
            package='audio_processing',
            executable='silero_vad',
            name='silero_vad', 
            output='screen'
        ),

        # Turn End Detection (from audio_processing)
        Node(
            package='audio_processing',
            executable='turn_end_detector',
            name='turn_end_detector',
            output='screen'
        ),
        
        # Automatic Speech Recognition
        Node(
            package='audio_processing',
            executable='google_asr',
            name='google_streaming_asr',
            output='screen'
        ),
        
        
        # Text-to-Speech Service
        Node(
            package='audio_processing', 
            executable='openai_tts',
            name='openai_tts_service',
            output='screen'
        ),
        
        # Audio Playback
        Node(
            package='audio_processing',
            executable='audio_playback',
            name='audio_playback_server',
            output='screen'
        ),
        
        # Motor Control
        Node(
            package='motor_control',
            executable='motor_controller', 
            name='motor_controller',
            output='screen'
        ),
        
        # Face Expression Control
        Node(
            package='m_commons',
            executable='face_controller',
            name='face_controller',
            output='screen'
        ),

        Node(
            package='m_commons',
            executable='led_controller',
            name='led_controller',
            output='screen'
        ),
        
        # Enhanced Conversation Orchestrator
        Node(
            package='positivity_pysch_coach',
            executable='conversation_orchestrator',
            name='conversation_orchestrator',
            output='screen',
            parameters=[
                {'initial_wait_ms': 5000.0},
                {'vad_silence_timeout_ms': 1500.0}
            ]
        )
    ])

