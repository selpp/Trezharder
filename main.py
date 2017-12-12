from game_engine import GameEngine , GameEngineTools
from gameobject import Gameobject
from mono_trezharder import MonoTrezharder
from pacman_scene import PacManScene
from scene import SceneManager

ge = GameEngine()
ge_tools = GameEngineTools(ge)
SceneManager.load(PacManScene)
ge.loop()
