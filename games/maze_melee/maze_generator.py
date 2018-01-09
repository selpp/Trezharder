import numpy as np
import random as rnd

from engine.core.maths.vector import Vector

class MazeGenerator:
	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.map = np.ones((height, width), dtype = int)
		self.walls_list = []

		self.dig(Vector(rnd.randint(1, width - 2),rnd.randint(1, height - 2)))

	def is_in_range(self, position):
		return 0 <= position.x < self.width and 0 <= position.y < self.height

	def set_position(self, position, value):
		if self.is_in_range(position):
			self.map[position.y, position.x] = value

	def get_neighbours(self, position):
		neighbours = []
		for i in range(4):
			neighbours.append(Vector(position.x, position.y))
		neighbours[0].x -= 1
		neighbours[1].x += 1
		neighbours[2].y += 1
		neighbours[3].y -= 1
		for neighbour in neighbours:
			if not self.is_in_range(neighbour):
				neighbours.remove(neighbour)
		return neighbours

	def get_empty_neighbour(self, position):
		neighbours = self.get_neighbours(position)
		for neighbour in neighbours:
			if self.map[neighbour.y, neighbour.x] == 0:
				return neighbour
		return None

	def get_opposite(self, position, pivot):
		return pivot + (pivot - position)

	def is_complete(self):
		return len(self.walls_list) == 0

	def pop_random_wall(self):
		return self.walls_list.pop(rnd.randint(0, len(self.walls_list) - 1))

	def dig(self, position, get_walls = True):
		self.set_position(position, 0)
		if not get_walls:
			return

		walls = self.get_neighbours(position)
		for wall in walls:
			self.walls_list.append(wall)

	def step(self):
		wall = self.pop_random_wall()
		empty_neighbour = self.get_empty_neighbour(wall)

		opposite = self.get_opposite(empty_neighbour, wall)
		if not self.is_in_range(opposite) or self.map[opposite.y, opposite.x] == 0:
			return

		opposite2 = self.get_opposite(wall, opposite)
		if not self.is_in_range(opposite2) or self.map[opposite2.y, opposite2.x] == 0:
			self.dig(wall, get_walls = False)
			return

		self.dig(wall, get_walls = False)
		self.dig(opposite)

	def generate(self):
		while not self.is_complete():
			self.step()
		return self.map.tolist()

	def show(self):
		msg = ''
		for y in range(self.height):
			for x in range(self.width):
				msg += u"\u25A0" + ' ' if self.map[y, x] == 1 else ' ' + ' '
			msg += '\n'
		print(msg)

if __name__ == '__main__':
	maze = MazeGenerator(20, 20)
	maze.generate()
	maze.show()
