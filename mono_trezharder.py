from monobehaviour import MonoBehaviour
from bot import Bot
from game_engine import GameEngineTools
from gameobject import Gameobject
from rigidbody import Rigidbody
from map_manager import MapManager
from bot_behaviour import BotBehaviour
from reward_calculator import RewardCalculator

class MonoTrezharder(MonoBehaviour):
    def __init__(self):
        MonoBehaviour.__init__(self)
        
    def start(self):
        '''
        players = [Gameobject('player',Rigidbody(),tag = 'player') for i in range(10)]
        for i in range(3):
            players[i].add_mono([Bot()])
        players[0].transform.get_position().x = 3 * 100.0 + 50.0
        players[0].transform.get_position().y = 4 * 100.0 + 50.0
        players[1].transform.get_position().x = 6 * 100.0 + 50.0
        players[1].transform.get_position().y = 4 * 100.0 + 50.0
        players[2].transform.get_position().x = 6 * 100.0 + 50.0
        players[2].transform.get_position().y = 2 * 100.0 + 50.0
        self.players = players
        '''
        player_rnd = Gameobject('player',Rigidbody(),tag = 'player')
        player_rnd.add_mono([Bot()])
        player_rnd.transform.get_position().x = 3 * 100.0 + 50.0
        player_rnd.transform.get_position().y = 4 * 100.0 + 50.0
        self.player_rnd = player_rnd
        
        player_deep = Gameobject('player',Rigidbody(),tag = 'player')
        player_deep.add_mono([BotBehaviour(),RewardCalculator(),Bot(is_rnd = False)])
        player_deep.transform.get_position().x = 6 * 100.0 + 50.0
        player_deep.transform.get_position().y = 4 * 100.0 + 50.0
        self.player_deep = player_deep
        
        my_map = Gameobject()
        mono_map = MapManager()
        my_map.add_mono([mono_map])
        mono_map.load(path = 'MAP0.map')
        self.my_map = my_map
        
        #GameEngineTools.instantiate(player)
        #for i in range(3):
        GameEngineTools.instantiate(player_rnd)
        GameEngineTools.instantiate(player_deep)
        GameEngineTools.instantiate(my_map)
        self.time = 0.0
        
    def restart(self):
        GameEngineTools.DestroyObject(self.gameobject)
        GameEngineTools.DestroyObject(self.my_map)
        #if self.player.is_alive:
            #GameEngineTools.DestroyObject(self.player)
        #for i in range(3):
            #if self.players[i].is_alive:
                #GameEngineTools.DestroyObject(self.players[i])
        if self.player_rnd.is_alive:
            GameEngineTools.DestroyObject(self.player_rnd)
        if self.player_deep.is_alive:
            GameEngineTools.DestroyObject(self.player_deep)
        game_manager = Gameobject(name='trezharder')
        game_manager.add_mono([MonoTrezharder()])
        GameEngineTools.instantiate(game_manager)
            
        
    def update(self,dt):
        pass
    
    def fixed_update(self,fdt):
        self.time += fdt
        if self.time > 5.0:
            self.restart()
    
    def draw(self):
        pass
    
    def z_buff(self, z_index, z_buffer):
        pass