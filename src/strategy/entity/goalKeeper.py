from ..entity import Entity
from strategy.field.UVF import UVF, UVFDefault
from strategy.field.UVF import UVF, UVFDefault
from strategy.field.DirectionalField import DirectionalField
from strategy.field.attractive import AttractiveField
from strategy.movements import goalkeep, spinGoalKeeper
from tools import angError, howFrontBall, howPerpBall, ang, norml, norm, angl
from tools.interval import Interval
from control.goalKeeper import GoalKeeperControl
import numpy as np
import math
import time

class GoalKeeper(Entity):
    def __init__(self, world, robot, side=1):
        super().__init__(world, robot)

        self._control = GoalKeeperControl(self.world)
        self.lastChat = 0
        self.state = "Stable"

    @property
    def control(self):
        return self._control

    def equalsTo(self, otherGoalKeeper):
        return True

    def onExit(self):
        pass

    def setGoalKeeperControl(self):
        self._control = GoalKeeperControl(self.world)

    # TODO: ao inves de usar fieldDecider, usar posições fixas e deixar o robo indo para uma ponta e outra no gol. Material de base no one drive -> principio de controle de robos -> controle de trajetoria
    # passar apenas o ponto final, fodase como o robo vai pra la.
    def fieldDecider(self):
        print("how goalkeeper should move")
