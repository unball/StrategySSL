from strategy import MainStrategy
from communication.serialWifi import SerialRadio
from world import World
import logging
import time
import sys
import signal
from client.client_pickle import ClientPickle
from UnBall/Client/UnBallSSLclient/game_controller import gc_sync

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
        self.strategy = MainStrategy(self.world)

        # Variáveis
        self.loopTime = 1.0 / loop_freq
        self.running = True
        self.lastupdatecount = 0
        self.radio = SerialRadio(control = control, debug = self.world.debug)

        self.pclient = ClientPickle(port)

        self.gc = gc_sync.SyncGameController()

        self.control_output = [None,None,None]
    
    def send_state(self,velocities):
        self.control_output = velocities
        for robot in self.world.raw_team: 
            if robot is not None: robot.turnOn()   
            self.radio.send(self.world.n_robots, control_output)
    
    def determine_state(self):
        
        message = self.gc.get_state()["command"]

        if message == '0': #Halt
            self.send_state([0,0,0])

        elif message == "1": #Stop
            self.send_state([0.1,0.1,0.1])

        elif message == "2": #Start
            self.send_state([10,0,0])
            time.sleep(5)

    # Função do sinal de interrupção (faz com que pare o robô imediatamente, (0,0) )
    def handle_SIGINT(self, signum, frame):
        if self.world.mainvision:
            self.radio.send(self.world.n_robots, [(0,0,0) for robot in self.world.team])
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

        control_output = [robot.entity.control.actuate(robot) for robot in self.world.team if robot is not None] 

        #[ATENCAO] Para testar se a comunicação está funcionando a partir daqui, basta descomentar a linha abaixo
        # A linha abaixo seta para enviar uma velocidade vx = 10 m/s (em teoria) para o robo 
        # control_output = [(10,0,0)]

        if self.execute:
            for robot in self.world.raw_team: 
                if robot is not None: robot.turnOn()   
            self.radio.send(self.world.n_robots, control_output)

    def busyLoop(self):

        # Atribuimos a mensagem que queremos passar para a função update_main_vision
        message = self.pclient.receive()
        self.execute = message["running"]
        if message is not None: 
            self.world.update_main_vision(message)

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

        ##[ATENCAO] Se conseguirmos receber start ou stop do game controller pode ser que role algo tipo 
        # if(recebemos comando de start) -> enviar control_output[(10,0,0)] por 5segundos e depois control_output[(-10,0,0)] 
        # em teoria com isso o robo vai para um lado por 5 segundos e depois para outro por 5 segundos. Nesse caso tem que comentar self.loop 
        # Vai ficar um codigo dentro do def run(): tipo assim
        # i = 1
        # for (5 sengundos):
            # control_output = [(10*i,0,0)]
        # i *= -1
        # if self.execute:
            # for robot in self.world.raw_team: 
            #     if robot is not None: robot.turnOn()   
            # self.radio.send(self.world.n_robots, control_output)

        logging.info("System stopped")

