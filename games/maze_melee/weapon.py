import random as rnd
import games.maze_melee.resources_config as res

from engine.core.monobehaviour import MonoBehaviour
from engine.core.game_engine import GameEngineTools
from engine.core.data_manager import DataManager , SpriteSheetInfos
from pygame import transform as pyg_transform
from engine.core.animations.animation import Animation , Animator
from engine.core.physics.collider import BoxCollider
from engine.core.maths.vector import Vector

class Weapon(MonoBehaviour):
    def __init__(self):
        MonoBehaviour.__init__(self,2)

    def start(self):
        self.power = rnd.randint(1,10)
        self.data_manager = DataManager.get_instance()
        self.animator = Animator()
        self.transform.get_scale().x = 50
        self.transform.get_scale().y = 50
        self.data_manager.load_sprite_sheet('COINS', res.GRAPHICS + 'COINS.png',SpriteSheetInfos(10,1,(100,100)))
        roll = Animation(self.data_manager.get_sprite_sheet('COINS'), [(i, 0) for i in range(10)], 0.5, 1, loop = True)
        self.animator.add_animation('ROLL', roll)
        self.animator.set_animation('ROLL')
        self.transform.tag = 'weapon'
        self.collider = BoxCollider(self.transform,Vector(0,0),Vector(1,1),self.gameobject,is_trigger = True)
        self.owned = False

    def update(self,dt):
        self.animator.update(dt)

    def damage(self):
        self.power -= 1
        if self.power == 0:
             GameEngineTools.DestroyObject(self.gameobject)

    def get_power(self):
        return self.power

    def draw(self,screen):
        top_left = self.transform.get_position() - self.transform.get_scale() / 2.0
        scale = self.transform.get_scale()
        resized = pyg_transform.scale(self.animator.current_sprite, (int(scale.x),int(scale.y) ))
        screen.blit(resized, (top_left.x, top_left.y))

    def z_buff(self,z_index,z_buffer):
        z_buffer.insert(z_index, self)
