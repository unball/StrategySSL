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

        v, w = self.output(robot)
        
        robot.lastControlLinVel = v
        w = self.world.field.side * w * -1
        
        return v, w