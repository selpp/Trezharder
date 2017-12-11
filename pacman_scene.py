from scene import Scene
from maze_generator import MazeGenerator
from gameobject import Gameobject
from map_manager import MapManager

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

		

		return gameobjects