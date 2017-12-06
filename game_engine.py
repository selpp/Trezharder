from pygame import display, event, font
from time import clock, sleep
from data_manager import DataManager
from physics_manager import PhysicsManager
from input_manager import InputManager
from z_buffer import ZBuffer
from map_manager import MapManager
from human_player import HumanPlayer
from bot import Bot
from random import randint


class GameEngine:
    def __init__(self):
        self.init_scene()
        self.init_screen()
        self.init_graphics()
        self.init_time()
        self.init_fixed_update()
        self.init_physics()
        
    # ===== SCREEN ==================
    def init_screen(self,width=800,height=600):
        self.width = width
        self.height = height
        BLACK = (0, 0, 0)
        self.screen = display.set_mode((width, height))
        self.screen.fill(BLACK)

    def init_time(self):
        self.current_time = clock()
        self.dt = 0
        
        #self.fps_cap = 60
        self.current_fps = 60
        self.tick_counter = 0
        self.fps_timer = 0
        
        font.init()
        self.fps_font = font.SysFont("monospace", 20)
        self.time_scale = 5.0
        
    def init_graphics(self):
        self.data_manager = DataManager.get_instance()
        self.z_buffer = ZBuffer()
        
    def init_scene(self):
        self.monobehaviours = []
        self.waiting_mono = []
        
    def show_debug(self):
        fps_label = self.fps_font.render('CLOCK: ' + str(clock()), 1, (0, 255, 0))
        self.screen.blit(fps_label, (0, 0))
        fps_label = self.fps_font.render('FPS: ' + str(self.current_fps), 1, (0, 255, 0))
        self.screen.blit(fps_label, (0, 22))
        fps_label = self.fps_font.render('FDT: ' + str(self.fixed_timer), 1, (0, 255, 0))
        self.screen.blit(fps_label, (0, 44))
        
    def init_fixed_update(self):
        self.current_fixed_time = clock()
        self.fixed_dt = 0
        self.fixed_timer = 0
        self.fixed_rate = 0.02
        
    def init_physics(self):
        self.pm = PhysicsManager.get_instance()
    
    def add_object(self,obj):
        self.waiting_mono.append(obj)
        
    def fixed_update(self):
        self.fixed_timer -= self.fixed_rate / self.time_scale
        #self.fixed_dt = clock() - self.current_fixed_time
        #self.current_fixed_time += self.fixed_dt
        
        for mono in self.monobehaviours:
            mono.fixed_update(self.fixed_rate)
            
        while len(self.waiting_mono) > 0:
            new_mono = self.waiting_mono.pop()
            new_mono.start()
            self.monobehaviours.append(new_mono)
            
        self.pm.update_collision()
    
    def update(self,dt):
        for mono in self.monobehaviours:
            mono.update(dt)
            mono.z_buff(mono.z_index,self.z_buffer)
        
    def loop(self):
        while True:
            InputManager.get_instance().update(event.get())
        
            self.screen.fill((0,0,255))
            self.z_buffer.reset()
        
            dt = (clock() - self.current_time)
            self.current_time += dt
            
            self.fps_timer += dt
            self.tick_counter += 1
            
            self.fixed_timer += dt
            while self.fixed_timer  *  self.time_scale > self.fixed_rate:
                self.fixed_update()
            
            if self.fps_timer > 4.0:
                self.current_fps = self.tick_counter // 4.0
                self.tick_counter = 0
                self.fps_timer = 0.0
                
            self.update(dt)
                
            self.z_buffer.draw(self.screen)
            self.show_debug()
            display.flip()
            
ge = GameEngine()
player = HumanPlayer()
player.transform.get_position().x = 6 * 100.0 + 50.0
player.transform.get_position().y = 4 * 100.0 + 50.0

player2 = HumanPlayer()
player2.transform.get_position().x = 3 * 100.0 + 50.0
player2.transform.get_position().y = 2 * 100.0 + 50.0

bots = [Bot() for i in range(1)]
for i,bot in enumerate(bots):
    bot.transform.get_position().x = 3 * 100.0 + 50.0 + 3.0 * i
    bot.transform.get_position().y = 2 * 100.0 + 50.0 + 3.0 * i
    bot.action_vector = [1, 0, 1, 0]

map_manager = MapManager(DataManager.get_instance())
map_manager.load(path = 'MAP0.map')

ge.add_object(player)
ge.add_object(player2)
for bot in bots:
    ge.add_object(bot)
ge.add_object(map_manager)
ge.loop()