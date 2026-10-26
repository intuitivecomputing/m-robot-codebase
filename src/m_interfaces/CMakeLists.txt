cmake_minimum_required(VERSION 3.5)
project(m_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/InteractionCue.msg"
  "msg/CueComplete.msg"
  "srv/SetPose.srv"
  "srv/GenerateStory.srv"
  "srv/PlayPoseSequence.srv"
  "srv/TextToSpeech.srv"
  "srv/TranscribeAudio.srv"
  "srv/TurnProcess.srv"
  "srv/ScaffoldProcess.srv"
  "srv/ExecuteStory.srv"
  "srv/InteractionCue.srv"
  "srv/ExecutePrimitive.srv"
  "srv/NodeReady.srv"
  "srv/ControlLED.srv"
  "action/AudioPlay.action"
  "action/DeliverResponse.action"
  "action/RealtimeDeliverResponse.action"
)

ament_package()
