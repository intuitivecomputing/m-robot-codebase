#!/bin/bash
# Launch script for positivity_pysch_coach interaction session

# Load environment variables
set -a
source /root/m_ws/.env
set +a

# Source ROS2 Humble
source /opt/ros/humble/setup.bash

# Source workspace
source /root/m_ws/install/setup.bash

# Launch the interaction
ros2 launch positivity_pysch_coach enhanced_conversation_interaction.launch.py
