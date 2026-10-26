from .robot import Robot
from .animator import RobotAnimator
from .timeline import Timeline

class MotorExecutor:
    def __init__(self, config: dict):
        self.robot = Robot(config)
        self.animator = RobotAnimator(self.robot)

    def set_pose(self, pose: dict, duration: float = 1.0):
        timeline = Timeline()
        timeline.add_keyframe(at=0.0, pose=pose, duration=1.0)
        self.animator.play_timeline(timeline, duration=duration)