import numpy as np

# Constantes físicas do robô
wheel_reduction = 1

# Supostamente devia ser
#r = 0.0325
#L = 0.075

# O que realmente é
r = 0.0159
L = 0.0756
wheel_reduction = 1
wheel_w_max = 110
conversion = 127 / wheel_w_max

def deadzone(vin, up, down):
  if (vin!=0):
    return vin+up if (vin > 0) else vin-abs(down)
  return 0

def speeds2motors(v: float, w: float) -> (int, int):
  """Recebe velocidade linear e angular e retorna velocidades para as duas rodas"""

  # Computa a velocidade angular de rotação de cada roda
  vr = (v + (L/2)*w) / r#/ (2*np.pi*r) * wheel_reduction
  vl = (v - (L/2)*w) / r#/ (2*np.pi*r) * wheel_reduction

  #if fabs(vr) > max_motor_speed or fabs(vl) > max_motor_speed:
  #  vr = max_motor_speed * vr / max(vr, vl)
  #  vl = max_motor_speed * vl / max(vr, vl)
  
  # vr *= convertion
  # vl *= convertion
  
  return vr, vl

def motors2linvel(vl: float, vr: float) -> float:
  # Computa a velocidade angular de rotação de cada roda
  return (vr + vl) * (2*np.pi*r) / wheel_reduction / 2

def angl(p0: tuple):
  """Calcula o ângulo da tupla `p0` no plano este ângulo está em \\((-\\pi,\\pi]\\)"""
  return np.arctan2(p0[1], p0[0])

def unit(angle):
  """Retorna um vetor unitário de ângulo `angle` no formato de numpy array"""
  return np.array([np.cos(angle), np.sin(angle)])

def norm(p0: tuple, p1: tuple):
  """Calcula a distância entre as tuplas `p0` e `p1` no plano"""
  return np.sqrt((p1[0]-p0[0])**2+(p1[1]-p0[1])**2)

def norml(p0: tuple):
  """Calcula a norma de `p0"""
  return np.sqrt((p0[0])**2+(p0[1])**2)

def angError(reference: float, current: float) -> float:
  """Calcula o erro angular entre `reference` e `current` de modo que este erro esteja no intervalo de \\((-\\pi,\\pi]\\) e o sinal do erro indique qual deve ser a orientação para seguir a referência, de modo que positivo é anti-horário e negativo é horário"""
  diff = np.arccos(np.cos(reference-current))
  sign = (np.sin(reference-current) >= 0)*2-1
  return sign * diff

def adjustAngle(angle: float) -> float:
  """Pega um ângulo em \\(\\mathbb{R}\\) e leva para o correspondente em \\((-\\pi,\\pi]\\)"""
  return angError(angle, 0)

def sat(x: float, amp: float):
  """Satura um número real `x` entre `amp` e `-amp`"""
  return max(min(x, amp), -amp)

def sats(x: float, ampn: float, ampp: float):
  return max(min(x, ampp), ampn)

def ang(p0: tuple, p1: tuple):
  """Calcula o ângulo entre as tuplas `p0` e `p1` no plano, este ângulo está em \\((-\\pi,\\pi]\\)"""
  return np.arctan2(p1[1]-p0[1], p1[0]-p0[0])

def filt(x: float, amp: float):
  if np.abs(x) > np.abs(amp): return 0
  else: return x

def fixAngle(angle: float):
  if abs(angle) > np.pi/2:
    return (angle + np.pi/2) % (np.pi) - np.pi/2
  else:
    return angle

def derivative(F, x, d=0.00001, *args):
  return (F(x+d, *args) - F(x, *args)) / d

def angularDerivative(vs, dt, order=1):
    if order == 1: return adjustAngle(vs[0] - vs[1]) / dt
    elif order == 2: return adjustAngle(vs[0] - 2*vs[1] + vs[2]) / dt**2

def howFrontBall(rb, rr, rg):
    return np.dot(rr[:2]-rb, unit(angl(rg-rb)))

def howPerpBall(rb, rr, rg):
    return np.dot(rr[:2]-rb, unit(angl(rg-rb)+np.pi/2))

def insideRect(r, rm, s):
  return np.all(r-rm < s)

def projectLine(r, v, xline):
  return ((xline-r[0])/v[0])*v[1] + r[1] if v[0] != 0 else 0

def insideEllipse(r, a, b, rm):
  """ Retorna se a posição r está dentro da elipse de parâmetros a, b e centro rm"""
  return ((r[0]-rm[0])/a)**2+((r[1]-rm[1])/b)**2 < 1

def angleRange(th):
  if th >= 0 and th <= np.pi: return th
  else: return th + 2*np.pi

def deadZone(x, w):
  return x-np.sign(x)*w if np.abs(x) > w else 0

def deadZoneDisc(x, w):
  return x if np.abs(x) > w else 0

def distToBall(pa, pb, pc):
  """ Retorna a distância entre ponto c e reta que passa por a e b"""
  a = (pa[1] - pb[1])
  b = (pa[0] - pb[1])
  c = pa[0]*pb[1] - (pb[0] + pa[1])
  return np.abs((a*pc[0] + b*pc[1] + c)) / np.sqrt(a**2 + b**2)

def perpl(r):
  return np.array([r[1], -r[0]])
  
def bestWithHyst(state: int, possibleStates: list, possibleStatesDistances: list, hyst: float):
  if state in possibleStates:
    distances = np.array(possibleStatesDistances) + [hyst for s in possibleStates if s != state]
    
  else:
    distances = np.array(possibleStatesDistances)
  #Se o len > 2 (mais de 2 robôs) descobrimos qual melhor robô, se não, 0
  if len(distances) >= 2: best = np.argmin(distances)
  else: best = 0
  return possibleStates[best]

def encodeSpeeds(vx: float, vy: float, w: float) -> (int, int,int):
  
  venc_x = int(vx/2 * 32767)
  venc_y = int(vy/2 * 32767)
  wenc = int(w/64 * 32767)

  return int((1 if venc_x >= 0 else -1) * (abs(venc_x) % 32767)), int((1 if venc_y >= 0 else -1) * (abs(venc_y) % 32767)), int((1 if wenc >= 0 else -1) * (abs(wenc) % 32767))
                                                                  
def RangeKutta(pos, vel, th, T, delta_t, w=0):

  #Calcula o ângulo futuro que o robô vai estar baseado no seu ângulo atual e sua velocidade angular.
  new_th = th * T + delta_t * w * T

  #Calcula a posição futura usando a média entre o ângulo atual e o futuro, a posição atual e a velocidade na coordenada
  new_x = pos[0] + delta_t * np.cos( (th * T + new_th)/2 ) * vel[0]
  new_y = pos[1] + delta_t * np.cos( (th * T + new_th)/2 ) * vel[1]

  return((new_x, new_y, new_th))