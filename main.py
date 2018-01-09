from engine.core.game_engine import GameEngine , GameEngineTools
from engine.core.gameobject import Gameobject
from engine.core.scene import SceneManager

from games.pacman.pacman_scene import PacManScene
from games.maze_melee.maze_melee import MazeMelee

ge = GameEngine()
ge_tools = GameEngineTools(ge)
SceneManager.load(PacManScene)
ge.loop()
