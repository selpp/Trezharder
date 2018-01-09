from random_spawner import RandomSpawner
import random 
from gameobject import Gameobject
from rigidbody import Rigidbody
from game_engine import GameEngineTools

class WeaponShuffler():
    def __init__(self,map):
        self.map = map
        self.weapons_mono = []
        self.spawner = RandomSpawner()
        
    def add_weapon(self,weapon):
        self.weapons_mono.append(weapon)
        
    def shuffle(self):
        spawns = self.spawner.spawn(len(self.weapons_mono),self.map)
        for weapon_mono in self.weapons_mono:
            if weapon_mono.gameobject is not None:
                GameEngineTools.DestroyObject(weapon_mono.gameobject)
            weapon_mono.gameobject = None
            weapon = Gameobject('weapon',Rigidbody(),tag = 'weapon')
            weapon.add_mono([weapon_mono])
            GameEngineTools.instantiate(weapon)
            my_spawn = spawns.pop(random.randint(0,len(spawns) - 1))
            weapon.transform.get_position().x = my_spawn[1] * 100.0 + 50.0
            weapon.transform.get_position().y = my_spawn[0] * 100.0 + 50.0
            
    def on_notify(self,message):
        if message == 'dispatch':
            self.shuffle()