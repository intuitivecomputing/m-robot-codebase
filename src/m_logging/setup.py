from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'm_logging'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='root',
    maintainer_email='root@todo.todo',
    description='Conversation logging for social robot interactions',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'conversation_logger = m_logging.conversation_logger:main',
        ],
    },
)
