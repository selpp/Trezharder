from scene import Scene
from maze_generator import MazeGenerator
from gameobject import Gameobject
from map_manager import MapManager
from random_spawner import RandomSpawner
from rigidbody import Rigidbody
from player import Player
from player_command import RandomPlayerCommand , StaticPlayerCommand
from restart_team_out import RestartTeamOut
from restart_time_out import RestartTimeOut

class PacManScene(Scene):
    def __init__(self):
        Scene.__init__(self)

    def load(self):
        gameobjects = []
        maze_genarator = MazeGenerator(8,6)
        map = maze_genarator.generate()
        
        my_map = Gameobject()
        mono_map = MapManager()
        my_map.add_mono([mono_map])
        mono_map.load(map)
        gameobjects.append(my_map)
        
        spawner = RandomSpawner()
        my_spawn = spawner.spawn(2,map)
        
        player_rnd = Gameobject('player_rnd',Rigidbody(),tag = 'player')
        player_rnd.add_mono([Player(RandomPlayerCommand(),1,'object')])
        player_rnd.transform.get_position().x = my_spawn[0][1] * 100.0 + 50.0
        player_rnd.transform.get_position().y = my_spawn[0][0] * 100.0 + 50.0
        gameobjects.append(player_rnd)
        
        player_target = Gameobject('object',Rigidbody(),tag = 'player')
        player_target.add_mono([Player(StaticPlayerCommand(),0,'object')])
        player_target.transform.get_position().x = my_spawn[1][1] * 100.0 + 50.0
        player_target.transform.get_position().y = my_spawn[1][0] * 100.0 + 50.0
        gameobjects.append(player_target)
        
        restart_rule = Gameobject('')
        restart_rule.add_mono([RestartTimeOut(10.0),RestartTeamOut(['object','player_rnd'])])
        gameobjects.append(restart_rule)
        
        return gameobjects