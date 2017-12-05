from pygame import display, event, font
from time import clock, sleep
from data_manager import DataManager
from physics_manager import PhysicsManager
from input_manager import InputManager
from z_buffer import ZBuffer
from map_manager import MapManager
from player import Player
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
        self.fps_font = font.SysFont("monospace", 30)
        
    def init_graphics(self):
        self.data_manager = DataManager.get_instance()
        self.z_buffer = ZBuffer()
        
    def init_scene(self):
        self.monobehaviours = []
        self.waiting_mono = []
        
    def show_fps(self):
        fps_label = self.fps_font.render('FPS: ' + str(self.current_fps), 1, (0, 255, 0))
        self.screen.blit(fps_label, (0, 0))
        
    def init_fixed_update(self):
        self.current_fixed_time = clock()
        self.fixed_dt = 0
        self.fixed_timer = 0
        self.fixed_rate = 0.02
        self.time_scale = 1.0
        
    def init_physics(self):
        self.pm = PhysicsManager.get_instance()
    
    def add_object(self,obj):
        self.waiting_mono.append(obj)
        
    def fixed_update(self):
        self.fixed_timer = 0
        self.fixed_dt = clock() - self.current_fixed_time
        self.current_fixed_time += self.fixed_dt
        
        for mono in self.monobehaviours:
            mono.fixed_update(self.fixed_dt)
            
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
        
            dt = (clock() - self.current_time) * self.time_scale
            self.current_time += dt
            
            self.fps_timer += dt
            self.tick_counter += 1
            
            self.fixed_timer += dt
            if self.fixed_timer > self.fixed_rate:
                self.fixed_update()
            
            if self.fps_timer > 1.0:
                self.current_fps = self.tick_counter
                self.tick_counter = 0
                self.fps_timer -= 1.0
                
            self.update(dt)
                
            self.z_buffer.draw(self.screen)
            self.show_fps()
            display.flip()  
            
ge = GameEngine()
player = Player()
player.transform.get_position().x = 6 * 100.0 + 50.0
player.transform.get_position().y = 4 * 100.0 + 50.0

player2 = Player()
player2.transform.get_position().x = 3 * 100.0 + 50.0
player2.transform.get_position().y = 2 * 100.0 + 50.0

map_manager = MapManager(DataManager.get_instance())
map_manager.load(path = 'MAP0.map')

ge.add_object(player)
ge.add_object(player2)
ge.add_object(map_manager)
ge.loop()
'''
# ===== SCREEN ==================
width = 800
height = 600
BLACK = (0, 0, 0)
screen = display.set_mode((width, height))
screen.fill(BLACK)

# ===== ENTITIES ================
data = DataManager()    
z_buffer = ZBuffer()

player = Player(data)
player.transform.get_position().x = 6 * 100.0 + 50.0
player.transform.get_position().y = 4 * 100.0 + 50.0

bot = Bot(data)
bot.transform.get_position().x = 100.0 + 50.0
bot.transform.get_position().y = 100.0 + 50.0

map_manager = MapManager(data)
map_manager.load(path = 'MAP0.map')

# ===== DELTA TIME ==============
current_time = clock()
dt = 0

# ===== current_fps =====================
fps_cap = 60
current_fps = 60
tick_counter = 0
fps_timer = 0
font.init()
fps_font = font.SysFont("monospace", 30)

def show_fps(fps):
    fps_label = fps_font.render('FPS: ' + str(fps), 1, (0, 255, 0))
    screen.blit(fps_label, (0, 0))

# ===== FIXED DELTA TIME ========
current_fixed_time = clock()
fixed_dt = 0
fixed_timer = 0
fixed_rate = 0.02

time_scale = 1.0

# ===== GET PhysicsManager ========
pm = PhysicsManager.get_instance()

# ===== Random Bot actions ========
bot_timer = 0
# v_x, v_y, shift, fire1
bot_action = [1, 0, 1, 0]
bot.action_vector = bot_action

# ===== LOOP ====================
while True:
    InputManager.get_instance().update(event.get())

    screen.fill(BLACK)
    z_buffer.reset()

    # ====================================================================
    # ===== Update =====
    dt = (clock() - current_time) * time_scale
    current_time += dt
    
    fps_timer += dt
    tick_counter += 1
    if fps_timer > 1:
        current_fps = tick_counter
        tick_counter = 0
        fps_timer = 0

    # ===== Bot ========
    bot_timer += dt

    # ===== Update =====
    player.update(dt)
    bot.update(dt)

    if bot_timer > 1:
		bot_timer = 0
		# v_x, v_y, shift, fire1
		bot_action = [round(randint(-1, 1)), round(randint(-1, 1)), randint(0, 1), randint(0, 1)]
		bot.action_vector = bot_action

    # ===== FixedUpdate =====
    fixed_timer += dt
    if fixed_timer > fixed_rate:
        fixed_timer = 0
        fixed_dt = clock() - current_fixed_time
        current_fixed_time += fixed_dt

        player.fixed_update(fixed_dt)
        bot.fixed_update(fixed_dt)
        pm.update_collision()

    # ===== Draw =====
    map_manager.z_buff(0, z_buffer)
    player.z_buff(2, z_buffer)
    bot.z_buff(2, z_buffer)

    z_buffer.draw(screen)

    # ====================================================================
    show_fps(fps)

    display.flip()                  
            # ===== Draw =====
            map_manager.z_buff(0, z_buffer)
            player.z_buff(2, z_buffer)
            bot.z_buff(2, z_buffer)
        
            z_buffer.draw(screen)

        
            # ====================================================================

# ===== ENTITIES ================

data = DataManager()    
z_buffer = ZBuffer()

player = Player(data)
player.transform.get_position().x = 6 * 100.0 + 50.0
player.transform.get_position().y = 4 * 100.0 + 50.0

bot = Bot(data)
bot.transform.get_position().x = 100.0 + 50.0
bot.transform.get_position().y = 100.0 + 50.0

map_manager = MapManager(data)
map_manager.load(path = 'MAP0.map')
'''