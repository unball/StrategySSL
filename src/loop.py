from strategy import MainStrategy
from communication.serialWifi import SerialRadio
from world import World
import logging
import time
import sys
import signal
from client.client_pickle import ClientPickle

class Loop:

    def __init__(self,
                debug =False,
                port=5002,
                n_robots=[0,1,2]
            ):

        # Instancia de sinal caso haja interrupções no processo (ctrl + C)
        signal.signal(signal.SIGINT, self.handle_SIGINT)

        self.n_robots = n_robots

        # Variáveis
        self.running = True
        self.radio = SerialRadio()

    # Função do sinal de interrupção (faz com que pare o robô imediatamente, (0,0) )
    def handle_SIGINT(self, signum, frame):
        self.radio.send(self.n_robots, [(0,0,0)])
        sys.exit(0) #OBS, já que se foi dado ctrl+c, o programa chamará essa função e qualquer coisa que acontecerá depois não ocorrerá por causa do sys.exit(0)

    def loop(self):

        #[ATENCAO] Para testar se a comunicação está funcionando a partir daqui, basta descomentar a linha abaixo
        # A linha abaixo seta para enviar uma velocidade vx = 10 m/s (em teoria) para o robo 
        control_output = [(10,0,0)]
  
        self.radio.send(self.n_robots, control_output)

    def run(self):

        logging.info("System is running")

        while self.running:

            # Executa o loop
            self.loop()

        ##[ATENCAO] Se conseguirmos receber start ou stop do game controller pode ser que role algo tipo 
        # podemos receber start ou stop a partir de um input digitado pelo terminal tbm 
        # if(recebemos comando de start) -> enviar control_output[(10,0,0)] por 5segundos e depois control_output[(-10,0,0)] 
        # em teoria com isso o robo vai para um lado por 5 segundos e depois para outro por 5 segundos. Nesse caso tem que comentar self.loop 
        # Vai ficar um codigo dentro do def run(): tipo assim --> 

        # enquanto o usuario nao digitar 'p' no terminal: 
        # i = 1
        # for (5 sengundos):
            # control_output = [(10*i,0,0)]
        # i *= -1
        # if self.execute:
            # for robot in self.world.raw_team: 
            #     if robot is not None: robot.turnOn()   
            # self.radio.send(self.world.n_robots, control_output)
        # se usuario digitou p no terminal
        # control_output = [(0,0,0)]
        # if self.execute:
            # for robot in self.world.raw_team: 
            #     if robot is not None: robot.turnOn()   
            # self.radio.send(self.world.n_robots, control_output)

        logging.info("System stopped")

