#!/bin/bash

cd /home/ella-deployment-6/Documents/pilot-deployment/face-server

# Cleanup function to stop all processes on exit
cleanup() {
    echo "Stopping social robot services..."
    kill $FIREFOX_PID 2>/dev/null
    kill $NODE_PID 2>/dev/null
    docker stop ella_robot_session 2>/dev/null
}

on_exit() {
    status=$?
    cleanup
    exit $status
}

on_signal() {
    cleanup
    exit 0
}

# Trap signals to run cleanup; preserve exit code on EXIT for systemd restart logic
trap on_exit EXIT
trap on_signal SIGTERM SIGINT SIGHUP

# Open Firefox in fullscreen kiosk mode (runs in background)
firefox --kiosk "http://localhost:3001/face.html" &
FIREFOX_PID=$!

# Start the Node.js server in the background
/home/ella-deployment-6/.nvm/versions/node/v21.7.3/bin/node server.js &
NODE_PID=$!

# Wait 4 seconds before starting docker container
sleep 4

# Remove any existing container with same name and start fresh
docker rm -f ella_robot_session 2>/dev/null
docker run --rm --privileged --network=host -v /home/ella-deployment-6/Documents/pilot-deployment/data:/root/data -v /home/ella-deployment-6/Documents/pilot-deployment/config:/root/m_ws/src/early_language_learning_agent/config -v /home/ella-deployment-6/Documents/pilot-deployment/stories:/root/m_ws/src/early_language_learning_agent/stories -v /home/ella-deployment-6/Documents/pilot-deployment/motor_config:/root/m_ws/src/motor_control/config --name ella_robot_session ella:deploy /root/launch_session.sh &
DOCKER_PID=$!

# Wait for Firefox (main process) to keep service alive
wait $FIREFOX_PID
