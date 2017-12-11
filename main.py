from game_engine import GameEngine , GameEngineTools
from gameobject import Gameobject
from mono_trezharder import MonoTrezharder
from scene import SceneManager

ge = GameEngine()
ge_tools = GameEngineTools(ge)
SceneManager.load(MonoTrezharder)
ge.loop()