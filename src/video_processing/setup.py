from setuptools import find_packages, setup
import glob
import os

package_name = 'video_processing'

# Collect all launch files
launch_files = [f for f in sorted(glob.glob('launch/*.launch.py')) if os.path.isfile(f)]

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', launch_files),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='root',
    maintainer_email='vantony@u.rochester.edu',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'camera_streamer = video_processing.camera_streamer:main',
            'video_saver = video_processing.video_saver:main',
            'recording_controller = video_processing.recording_controller:main',
            'session_recording_coordinator = video_processing.session_recording_coordinator:main',
        ],
    },
)
