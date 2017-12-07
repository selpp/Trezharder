from game_engine import GameEngine , GameEngineTools
from gameobject import Gameobject
from mono_trezharder import MonoTrezharder

ge = GameEngine()
ge_tools = GameEngineTools(ge)

game_manager = Gameobject(name='trezharder')
game_manager.add_mono([MonoTrezharder()])   
ge.add_object(game_manager)
ge.loop()