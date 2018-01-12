import numpy as np
import engine.deep_learning.double_dueling_deep_q_learning as dddqn
import engine.deep_learning.config as conf

from pygame import display, event, font , image, transform, quit, QUIT
from time import clock
from engine.core.data_manager import DataManager
from engine.core.physics.physics_manager import PhysicsManager
from engine.core.inputs.input_manager import InputManager
from engine.core.graphics.z_buffer import ZBuffer
from pygame import image, surfarray, Surface
from PIL import Image
from sys import exit

class GameEngine:
    def __init__(self):
        self.init_scene()
        self.init_screen()
        self.init_graphics()
        self.init_time()
        self.init_fixed_update()
        self.init_physics()
        self.new_scene = None
        self.exit_game = False

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
        self.time_scale = conf.TIME_SCALE

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

    def set_scene(self,scene_loader):
        self.new_scene_loader = scene_loader

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

        if self.new_scene_loader is not None:
            self.new_scene_loader()
            self.new_scene_loader = None


        while len(self.destruct_list) > 0:
            gameobject = self.destruct_list.pop()
            if gameobject.is_alive:
                self.gameobjects.remove(gameobject)
                gameobject.is_alive = False

        while len(self.waiting_gameobjects) > 0:
            new_gameobject = self.waiting_gameobjects.pop()
            self.gameobjects.append(new_gameobject)

        self.pm.update_collision()


    def update(self,dt):
        for gameobject in self.gameobjects:
            gameobject.update(dt)
            gameobject.z_buff(self.z_buffer)

    def loop(self):
        while not self.exit_game:
            events = event.get()
            InputManager.get_instance().update(events)
            for e in events:
                if e.type == QUIT:
                    self.exit_game = True

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

            # Modes
            if InputManager.get_instance().is_key_down('DEEP_MODE'):
                GameEngineTools.set_learning_mode(not GameEngineTools.get_learning_mode())

            # Screen
            training_mode = GameEngineTools.get_learning_mode()
            self.screen.fill(self.BLACK)
            self.screen_ai.fill(self.BLACK)
            self.z_buffer.update()
            if not training_mode:
                self.z_buffer.draw(self.screen)
            else:
                self.ai_view_mode()
            self.show_debug()
            display.flip()

        quit()
        exit()

    def ai_view_mode(self):
        i = 0
        for id, feature_map in self.data_manager.feature_maps.iteritems():
            i += 1

            feature_map.fill(self.BLACK)
            self.z_buffer.draw_feature_map(id)
            self.draw_feature_map(id, i)

    def draw_feature_map(self, id, n):
        cfr = GameEngineTools.get_current_feature_map(id)
        if cfr is None:
            return
        w, _ = GameEngineTools.get_screen_ai_size()
        ai_debug = surfarray.make_surface(np.stack([cfr, cfr, cfr], axis = 2))
        self.screen.blit(ai_debug, (self.width - w * n, 0))

    def pause_timers(self):
        self.dt_pause = clock() - self.current_time

    def restart_timers(self):
        self.current_time = clock() - self.dt_pause

class GameEngineTools(object):
    def __init__(self,ge):
        self.ge = ge
        ge.pause_timers()

        self.deep_width = conf.WIDTH
        self.deep_height = conf.HEIGHT
        self.model = dddqn.DDDQN(load = conf.LOAD)
        self.learning_mode = False

        self.current_feature_maps = {}

        # DataManager.get_instance().add_feature_map('COLLISIONS', self.ge.width, self.ge.height)
        # DataManager.get_instance().add_feature_map('PLAYER', self.ge.width, self.ge.height)
        # DataManager.get_instance().add_feature_map('RANGE', self.ge.width, self.ge.height)
        DataManager.get_instance().add_feature_map('SIMPLIFIED', self.ge.width, self.ge.height)

        ge.restart_timers()
        GameEngineTools.instance = self

    instance = None

    @staticmethod
    def get_model():
        return GameEngineTools.instance.model

    @staticmethod
    def get_learning_mode():
        return GameEngineTools.instance.learning_mode

    @staticmethod
    def set_learning_mode(b):
        GameEngineTools.instance.learning_mode = b

    @staticmethod
    def get_screen_size():
        ge_tools = GameEngineTools.instance
        return ge_tools.ge.width, ge_tools.ge.height

    @staticmethod
    def get_screen_ai_size():
        ge_tools = GameEngineTools.instance
        return ge_tools.deep_width, ge_tools.deep_height

    @staticmethod
    def get_current_feature_map(id):
        ge_tools = GameEngineTools.instance
        if not id in ge_tools.current_feature_maps:
            return None
        arr = ge_tools.current_feature_maps[id]
        return arr

    @staticmethod
    def update_feature_map(id):
        ge_tools = GameEngineTools.instance
        arr = DataManager.get_instance().feature_map_to_array(id, ge_tools.deep_width, ge_tools.deep_height)
        ge_tools.current_feature_maps[id] = arr

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

    @staticmethod
    def destroy_scene():
        ge_tools = GameEngineTools.instance
        for gameobject in ge_tools.ge.gameobjects:
            ge_tools.ge.destruct_list.append(gameobject)

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
    def set_new_scene(scene_loader):
        ge_tools = GameEngineTools.instance
        ge_tools.ge.set_scene(scene_loader)
