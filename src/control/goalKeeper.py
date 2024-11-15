from tools import norm, ang, angError, sat, speeds2motors, fixAngle, filt, L
from tools.interval import Interval
from control import Control
import numpy as np
import math
import time 

# TODO: colocar lei de controle de pose - é bem mais simples!! 
class GoalKeeperControl(Control):
  def __init__(self, world, kw=6, kp=500, mu=0.4, vmax=0.8, L=L, enableInjection=False):
    Control.__init__(self, world)

  def output(self, robot):
    print("output do controle do robo")