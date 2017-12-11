from monobehaviour import MonoBehaviour
from bot import Bot
from game_engine import GameEngineTools
from gameobject import Gameobject
from rigidbody import Rigidbody
from map_manager import MapManager
from bot_behaviour import BotBehaviour
from reward_murderer import RewardMurederer
from reward_coward import RewardCoward
from player import Player
from player_command import *
from deep_player_command import DeepPlayerCommand
import random

class MonoTrezharder(MonoBehaviour):
    def __init__(self):
        MonoBehaviour.__init__(self)
        self.nb_ennemy = 8
        
    def start(self):
        spawns = [(2,1),(1,2),(1,3),(6,2),(6,3),(3.5,2.5),(5,1),(2,4),(5,4)]

        self.players_rnd = []
        for i in range(self.nb_ennemy):
            player_rnd = Gameobject('player_rnd',Rigidbody(),tag = 'player')
            player_rnd.add_mono([Player(RandomPlayerCommand(),0,'player')])
            my_spawn = spawns.pop(random.randint(0,len(spawns) - 1))
            player_rnd.transform.get_position().x = my_spawn[0] * 100.0 + 50.0
            player_rnd.transform.get_position().y = my_spawn[1] * 100.0 + 50.0
            self.players_rnd.append(player_rnd) 
        
        
        player_deep = Gameobject('player',Rigidbody(),tag = 'player')
        rc = RewardCoward()
        player_deep.add_mono([rc,Player(DeepPlayerCommand(rc),1,'player_rnd')])
        player_deep.transform.get_position().x = spawns[0][0] * 100.0 + 50.0
        player_deep.transform.get_position().y = spawns[0][1] * 100.0 + 50.0
        self.player_deep = player_deep
        
        my_map = Gameobject()
        mono_map = MapManager()
        my_map.add_mono([mono_map])
        mono_map.load(path = 'MAP0.map')
        self.my_map = my_map
        
        #GameEngineTools.instantiate(player)
        #for i in range(3):
        for i in range(self.nb_ennemy):
            GameEngineTools.instantiate(self.players_rnd[i])
        GameEngineTools.instantiate(player_deep)
        GameEngineTools.instantiate(my_map)
        self.time = 0.0
        
    def restart(self):
        GameEngineTools.DestroyObject(self.gameobject)
        GameEngineTools.DestroyObject(self.my_map)
        for i in range(self.nb_ennemy):
            if self.players_rnd[i].is_alive:
                GameEngineTools.DestroyObject(self.players_rnd[i])
        if self.player_deep.is_alive:
            GameEngineTools.DestroyObject(self.player_deep)
        game_manager = Gameobject(name='trezharder')
        game_manager.add_mono([MonoTrezharder()])
        GameEngineTools.instantiate(game_manager)
        
    def update(self,dt):
        pass
    
    def fixed_update(self,fdt):
        if not self.player_deep.is_alive:# or not self.player_rnd.is_alive:
            self.restart()
            return
        for i in range(self.nb_ennemy):
            if self.players_rnd[i].is_alive:
                return
        self.restart()
    
    def draw(self):
        pass
    
    def z_buff(self, z_index, z_buffer):
        pass