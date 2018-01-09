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
from scene import Scene
from restart_team_out import RestartTeamOut

class MonoTrezharder(Scene):
    def __init__(self):
        self.nb_ennemy = 8
        Scene.__init__(self)

    def load(self):
        gameobjects = []
        spawns = [(2,1),(1,2),(1,3),(6,2),(6,3),(3.5,2.5),(5,1),(2,4),(5,4)]

        self.players_rnd = []
        for i in range(self.nb_ennemy):
            player_rnd = Gameobject('player_rnd',Rigidbody(),tag = 'player')
            player_rnd.add_mono([Player(RandomPlayerCommand(),0,'player')])
            my_spawn = spawns.pop(random.randint(0,len(spawns) - 1))
            player_rnd.transform.get_position().x = my_spawn[0] * 100.0 + 50.0
            player_rnd.transform.get_position().y = my_spawn[1] * 100.0 + 50.0
            gameobjects.append(player_rnd)


        player_deep = Gameobject('player',Rigidbody(),tag = 'player')
        rc = RewardCoward()
        player_deep.add_mono([rc,Player(DeepPlayerCommand(rc),1,'player_rnd')])
        player_deep.transform.get_position().x = spawns[0][0] * 100.0 + 50.0
        player_deep.transform.get_position().y = spawns[0][1] * 100.0 + 50.0
        gameobjects.append(player_deep)

        my_map = Gameobject()
        mono_map = MapManager()
        my_map.add_mono([mono_map])
        mono_map.load_from_file(path = 'MAP0.map')
        gameobjects.append(my_map)

        restart_rule = Gameobject('')
        restart_rule.add_mono([RestartTeamOut(['player','player_rnd'])])
        gameobjects.append(restart_rule)

        return gameobjects
