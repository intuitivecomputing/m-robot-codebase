from setuptools import find_packages, setup
import glob
import os

package_name = 'audio_processing'

# Collect all files under launch/ to include them automatically
launch_files = [f for f in sorted(glob.glob('launch/*')) if os.path.isfile(f)]

data_files = [
    ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
    ('share/' + package_name, ['package.xml']),
    ('share/' + package_name + '/launch', launch_files),
]

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=data_files,
    package_data={
        package_name: ['interaction_prompts/*'],
    },
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='root',
    maintainer_email='root@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'mic_streamer = audio_processing.mic_streamer:main',
            'silero_vad = audio_processing.silero_vad:main',
            'vosk_asr = audio_processing.vosk_asr:main',
            'faster_whisper_asr = audio_processing.faster_whisper_asr:main',
            'whisper_streaming_asr = audio_processing.whisper_streaming_asr:main',
            'google_asr = audio_processing.google_streaming_asr:main',
            'audio_saver = audio_processing.audio_saver:main',
            'google_tts = audio_processing.google_tts:main',
            'openai_tts = audio_processing.openai_tts:main',
            'audio_playback = audio_processing.audio_playback:main',
            'audio_transcriber = audio_processing.audio_transcriber:main',
            'turn_end_detector = audio_processing.turn_end_detector:main',
        ],
    },
)
