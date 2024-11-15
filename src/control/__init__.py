from abc import ABC, abstractmethod
from tools import speeds2motors, deadzone, sat

class Control(ABC):
    def __init__(self, world):
        ABC.__init__(self)

        self.world = world

    @abstractmethod
    def output(self, robot):
        pass

    def actuate(self, robot):
        if not robot.on: return (0, 0,0)

        vx, vy, w = self.output(robot)
        
        return vx, vy , w