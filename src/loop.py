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
                loop_freq=90,
                team_yellow=False,
                immediate_start=False,
                static_entities=False,
                referee=False,
                firasim=False,
                vssvision=False,
                mainvision=False,
                simulado=False,
                control=False,
                debug =False,
                port=5002,
                mirror=False, 
                n_robots=[0,1,2]
            ):

        # Instancia de sinal caso haja interrupções no processo (ctrl + C)
        signal.signal(signal.SIGINT, self.handle_SIGINT)

        # Instancia o mundo e a estratégia
        team_side = -1 if mirror else 1
        self.world = World(n_robots=n_robots, side=team_side, team_yellow=team_yellow, immediate_start=immediate_start, referee=referee, firasim=firasim, vssvision=vssvision, mainvision=mainvision, simulado=simulado, control=control, debug=debug, mirror=mirror)        
        self.strategy = MainStrategy(self.world, static_entities=static_entities)

        # Variáveis
        self.loopTime = 1.0 / loop_freq
        self.running = True
        self.lastupdatecount = 0
        self.radio = SerialRadio(control = control, debug = self.world.debug)

        if self.world.mainvision:
            self.pclient = ClientPickle(port)

    # Função do sinal de interrupção (faz com que pare o robô imediatamente, (0,0) )
    def handle_SIGINT(self, signum, frame):
        if self.world.mainvision:
            self.radio.send(self.world.n_robots, [(0,0) for robot in self.world.team])
            for robot in self.world.raw_team: 
                if robot is not None: robot.turnOff()
        elif self.world.simulado:
            self.simulado.step([(0,0) for robot in self.world.team])
            for robot in self.world.raw_team: 
                if robot is not None: robot.turnOff()
        sys.exit(0) #OBS, já que se foi dado ctrl+c, o programa chamará essa função e qualquer coisa que acontecerá depois não ocorrerá por causa do sys.exit(0)

    def loop(self):
        if self.world.updateCount == self.lastupdatecount: return
        # print("loop ALP:",(time.time()-self.t0)*1000)

        self.t0 = time.time()
        self.lastupdatecount = self.world.updateCount
        
        # Executa estratégia
        self.strategy.update(self.world)

        if self.world.mainvision: control_output = [robot.entity.control.actuate(robot) for robot in self.world.team if robot is not None]
        if self.world.simulado: control_output = [robot.entity.control.actuateSimu(robot) for robot in self.world.team if robot is not None]

        if self.world.mainvision:   
            if self.execute:
                for robot in self.world.raw_team: 
                    if robot is not None: robot.turnOn()   
                self.radio.send(self.world.n_robots, control_output)
        if self.world.simulado:
            for robot in self.world.raw_team:
                if robot is not None: robot.turnOn()
            robos = control_output
            self.simulado.step(robos)
                
        # Desenha no ALP-GUI
        self.draw()

    def busyLoop(self):

        if self.world.mainvision:
            # Atribuimos a mensagem que queremos passar para a função update_main_vision
            message = self.pclient.receive()
            self.execute = message["running"]
            if message is not None: 
                self.world.update_main_vision(message)

        if self.world.simulado:
            message = self.simulado.get_state()
            self.execute = True if message else False
            if self.execute:
                self.world.update(message)
        
        elif((self.world.debug) and not (self.world.vssvision) and not (self.world.firasim) and not self.world.mainvision and not self.world.simulado):
            print("_________")
            print("Executando sem pacote:")

    def run(self):
        t0 = 0

        logging.info("System is running")

        while self.running:
            
            # Executa o loop de visão e referee até dar o tempo de executar o resto
            self.busyLoop()
            while time.time() - t0 < self.loopTime:
                self.busyLoop()
            self.world.execTime = time.time() - t0
                
            # Tempo inicial do loop
            t0 = time.time()

            # Executa o loop
            self.loop()

            if self.draw_uvf:
                self.UVF_screen.updateScreen()

        logging.info("System stopped")