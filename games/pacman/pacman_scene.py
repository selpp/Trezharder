from engine.core.scene import Scene
from games.pacman.maze_generator import MazeGenerator
from engine.core.gameobject import Gameobject
from games.pacman.map_manager import MapManager
from games.pacman.random_spawner import RandomSpawner
from engine.core.physics.rigidbody import Rigidbody
from games.pacman.player import Player
from engine.core.inputs.player_command import RandomPlayerCommand , StaticPlayerCommand
from engine.deep_learning.deep_player_command import DeepPlayerCommand
from games.pacman.restart_time_out import RestartTimeOut
from games.pacman.restart_team_out import RestartTeamOut
from games.pacman.reward_loot import RewardLoot

class PacManScene(Scene):
    maze_genarator = MazeGenerator(8, 6)
    map = maze_genarator.generate()

    def __init__(self):
        Scene.__init__(self)

    def load(self):
        gameobjects = []
        map = PacManScene.map

        my_map = Gameobject()
        mono_map = MapManager()
        my_map.add_mono([mono_map])
        mono_map.load(map)
        gameobjects.append(my_map)

        spawner = RandomSpawner()
        my_spawn = spawner.spawn(-1,map)

        player_rnd = Gameobject('player_rnd', Rigidbody(), tag = 'player')
        reward = RewardLoot()
        player_rnd.add_mono([reward, Player(DeepPlayerCommand(reward), 1, 'object')])
        player_rnd.transform.get_position().x = my_spawn[0][1] * 100.0 + 50.0
        player_rnd.transform.get_position().y = my_spawn[0][0] * 100.0 + 50.0
        gameobjects.append(player_rnd)

        for i in range(1,len(my_spawn)):
            player_target = Gameobject('object',Rigidbody(),tag = 'player')
            player_target.add_mono([Player(StaticPlayerCommand(),0,'object')])
            player_target.transform.get_position().x = my_spawn[i][1] * 100.0 + 50.0
            player_target.transform.get_position().y = my_spawn[i][0] * 100.0 + 50.0
            gameobjects.append(player_target)


        restart_rule = Gameobject('')
        restart_rule.add_mono([RestartTimeOut(8.0), RestartTeamOut(['object','player_rnd'])])
        gameobjects.append(restart_rule)


        return gameobjects
