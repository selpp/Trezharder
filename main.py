from game_engine import GameEngine , GameEngineTools
from gameobject import Gameobject
from mono_trezharder import MonoTrezharder
from maze_melee import MazeMelee
from scene import SceneManager

ge = GameEngine()
ge_tools = GameEngineTools(ge)
SceneManager.load(MazeMelee)
ge.loop()