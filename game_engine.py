from pygame import display, event, font , image, transform
from time import clock
from data_manager import DataManager
from physics_manager import PhysicsManager
from input_manager import InputManager
from z_buffer import ZBuffer
from pygame import image, surfarray, Surface
from PIL import Image
import numpy as np
from model_1 import DeepQModel

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
        self.BLACK = (0, 0, 0)
        self.screen = display.set_mode((width, height))
        self.screen.fill(self.BLACK)

        self.screen_ai = Surface((width, height))
        self.screen_ai.fill(self.BLACK)

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
        self.gameobjects = []
        self.waiting_gameobjects = []
        self.destruct_list = []
        
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
        self.waiting_gameobjects.append(obj)
        
    def fixed_update(self):
        self.fixed_timer -= self.fixed_rate / self.time_scale
        #self.fixed_dt = clock() - self.current_fixed_time
        #self.current_fixed_time += self.fixed_dt
        
        for gameobject in self.gameobjects:
            gameobject.fixed_update(self.fixed_rate)
          
        while len(self.destruct_list) > 0:
            self.gameobjects.remove(self.destruct_list.pop())
            
        while len(self.waiting_gameobjects) > 0:
            new_gameobject = self.waiting_gameobjects.pop()
            self.gameobjects.append(new_gameobject)
            
        self.pm.update_collision()
        
    
    def update(self,dt):
        for gameobject in self.gameobjects:
            gameobject.update(dt)
            gameobject.z_buff(self.z_buffer)
        
    def loop(self):
        while True:
            InputManager.get_instance().update(event.get())
        
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
            self.screen.fill(self.BLACK)
            self.screen_ai.fill(self.BLACK)
            
            self.z_buffer.draw_ai(self.screen_ai)
            self.z_buffer.draw(self.screen)

            self.show_debug()

            self.draw_screen_ai()
            
            display.flip()

    def draw_screen_ai(self):
        if GameEngineTools.get_current_screen_ai() is not None:
            w, _ = GameEngineTools.get_screen_ai_size()
            ai_screen = GameEngineTools.get_current_screen_ai()
            ai_debug = surfarray.make_surface(np.stack([ai_screen, ai_screen, ai_screen], axis = 2))
            self.screen.blit(ai_debug, (self.width - w, 0))

    def pause_timers(self):
        self.dt_pause = clock() - self.current_time

    def restart_timers(self):
        self.current_time = clock() - self.dt_pause
            
class GameEngineTools(object):
    def __init__(self,ge):
        self.ge = ge
        ge.pause_timers()
        self.deep_width = 84
        self.deep_height = 84
        self.model = DeepQModel(width = self.deep_width, height = self.deep_height)
        self.current_screen_ai = None
        ge.restart_timers()
        GameEngineTools.instance = self
        
    instance = None

    @staticmethod
    def get_model():
        return GameEngineTools.instance.model

    @staticmethod
    def get_screen_size():
        ge_tools = GameEngineTools.instance
        return ge_tools.ge.width, ge_tools.ge.height

    @staticmethod
    def get_screen_ai_size():
        ge_tools = GameEngineTools.instance
        return ge_tools.deep_width, ge_tools.deep_height

    @staticmethod
    def get_current_screen_ai():
        ge_tools = GameEngineTools.instance
        return ge_tools.current_screen_ai

    @staticmethod
    def update_current_screen_ai():
        ge_tools = GameEngineTools.instance
        ge_tools.current_screen_ai = ge_tools.screen_ai_to_array()
        
    @staticmethod
    def find(name):
        ge_tools = GameEngineTools.instance
        for gameobject in ge_tools.ge.gameobjects:
            if gameobject.name == name:
                return gameobject
        return None
    
    @staticmethod
    def find_all(name):
        ge_tools = GameEngineTools.instance
        gameobjects = []
        for gameobject in ge_tools.ge.gameobjects:
            if gameobject.name == name:
                gameobjects.append(gameobject)
        return gameobjects
        
    @staticmethod
    def instantiate(gameobject):
        ge_tools = GameEngineTools.instance
        ge_tools.ge.add_object(gameobject)
    
    @staticmethod
    def DestroyObject(gameobject):
        ge_tools = GameEngineTools.instance
        ge_tools.ge.destruct_list.append(gameobject)
        gameobject.is_alive = False

    @staticmethod
    def pause():
        ge_tools = GameEngineTools.instance
        ge_tools.ge.pause_timers()

    @staticmethod
    def restart():
        ge_tools = GameEngineTools.instance
        ge_tools.ge.restart_timers()

    @staticmethod
    def screen_to_array():
        #from PIL import Image
        
        ge_tools = GameEngineTools.instance
        surface = ge_tools.ge.screen
        #surface = transform.scale(surface, (ge_tools.deep_width, ge_tools.deep_height))
        arr = surfarray.array3d(surface)
        image = Image.fromarray(arr)
        image = image.resize((ge_tools.deep_height,ge_tools.deep_width),Image.NEAREST)
        #img = Image.fromarray(arr)
        # image.save('Out.jpg')
        
        return np.array(image)

    @staticmethod
    def screen_ai_to_array():
        ge_tools = GameEngineTools.instance
        surface = ge_tools.ge.screen_ai
        arr = surfarray.array3d(surface) 
        image = Image.fromarray(arr)
        image = image.resize((ge_tools.deep_height,ge_tools.deep_width), Image.NEAREST)
        image = image.convert('L',(0.2889,0.5870,0.1140,0))

        return np.array(image)