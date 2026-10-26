from setuptools import find_packages, setup

package_name = 'm_commons'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
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
            'face_controller = m_commons.face_controller:main',
            'startup_manager = m_commons.startup_manager:main',
            'led_controller = m_commons.led_controller:main',
        ],
    },
)
