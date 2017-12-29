from scene import Scene
from random_spawner import RandomSpawner
from gameobject import Gameobject
from map_manager import MapManager
from brawler import Brawler
from player import Player
from player_command import RandomPlayerCommand, HumanPlayerCommand
from rigidbody import Rigidbody
from restart_team_out import RestartTeamOut
from restart_time_out import RestartTimeOut
import random
from maze_generator import MazeGenerator 
from weapon import Weapon
from maze_voice import MazeVoice

class MazeMelee(Scene):
    def __init__(self):
        self.nb_players = 5
        self.nb_weapons = 10
        Scene.__init__(self)
    
    def load(self):
        gameobjects = []
        spawner = RandomSpawner()
        
        maze_genarator = MazeGenerator(8, 6)
        maze_voice = MazeVoice()
        map = maze_genarator.generate()
        
        my_map = Gameobject()
        mono_map = MapManager()
        my_map.add_mono([mono_map,maze_voice])
        mono_map.load(map)
        #mono_map.load_from_file(path = 'MAP0.map')
        gameobjects.append(my_map)
        
        self.players_rnd = []
        
        spawns = spawner.spawn(self.nb_players + self.nb_weapons,map)
        for i in range(self.nb_players):
            player_rnd = Gameobject('player',Rigidbody(),tag = 'player')
            if i == self.nb_players - 1:
                player_rnd.add_mono([Brawler(HumanPlayerCommand(),1,'player')])
            else:
                player_rnd.add_mono([Brawler(RandomPlayerCommand(),0,'player')])
            my_spawn = spawns.pop(random.randint(0,len(spawns) - 1))
            player_rnd.transform.get_position().x = my_spawn[1] * 100.0 + 50.0
            player_rnd.transform.get_position().y = my_spawn[0] * 100.0 + 50.0
            gameobjects.append(player_rnd)
            maze_voice.add_listener(player_rnd.get_mono(Brawler))
        
        for i in range(self.nb_weapons):
            weapon = Gameobject('weapon',Rigidbody(),tag = 'weapon')
            weapon.add_mono([Weapon()])
            my_spawn = spawns.pop(random.randint(0,len(spawns) - 1))
            weapon.transform.get_position().x = my_spawn[1] * 100.0 + 50.0
            weapon.transform.get_position().y = my_spawn[0] * 100.0 + 50.0
            gameobjects.append(weapon)

        restart_rule = Gameobject('')
        restart_rule.add_mono([RestartTimeOut(10.0)])
        gameobjects.append(restart_rule)
        

        return gameobjects
    
    