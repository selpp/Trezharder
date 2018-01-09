# Map Manager
from data_manager import TileInfos
from vector import Vector
from transform import Transform
from collider import BoxCollider
from monobehaviour import MonoBehaviour
from data_manager import DataManager
import pygame
from pygame import Rect, transform
# ===================================================
# MAPMANAGER

class TileMap(object):
	def __init__(self, id, gameobject, position, angle, scale, data_manager, is_collider = False):
		self.data_manager = data_manager
		self.id = id
		self.transform = Transform(position, angle, scale)
		self.collider = None
		if is_collider:
			self.collider = BoxCollider(self.transform, Vector(0.0, 0.0), Vector(1.0, 1.0),gameobject)

	def draw(self, screen):
		tile = self.data_manager.get_tile(self.id)
		top_left = self.transform.get_position() - self.transform.get_scale() / 2.0
		scale = self.transform.get_scale()
		resized = transform.scale(tile.img, (scale.x, scale.y))
		screen.blit(resized, (top_left.x, top_left.y))

	def draw_collision_vision(self, screen):
		scale = self.transform.get_scale() / 2.0
		draw_pos = self.transform.get_position() - scale
		color = (0, 0, 0) if self.id == 'STONE' or self.id == 'WOOD' else (255, 255, 255)
		pygame.draw.rect(screen, color, Rect(draw_pos.x, draw_pos.y, scale.x * 2.0, scale.y * 2.0))

	def draw_simplified(self, screen):
		scale = self.transform.get_scale() / 2.0
		draw_pos = self.transform.get_position() - scale
		color = (0, 0, 0) if self.id == 'STONE' or self.id == 'WOOD' else (255, 255, 255)
		pygame.draw.rect(screen, color, Rect(draw_pos.x, draw_pos.y, scale.x * 2.0, scale.y * 2.0))

	def draw_feature_map(self, id):
		if id == 'COLLISIONS':
			self.draw_collision_vision(DataManager.get_instance().feature_maps[id])
		elif id == 'SIMPLIFIED':
			self.draw_simplified(DataManager.get_instance().feature_maps[id])

	def draw_debug(self, screen):
		if self.collider is not None:
			self.collider.draw_debug(screen)

	def z_buff(self, z_index, z_buffer):
		z_buffer.insert(z_index, self)

class MapManager(MonoBehaviour):
	def __init__(self):
		self.map = None
		MonoBehaviour.__init__(self,0)
		self.width = 0
		self.height = 0
		self.data_manager = DataManager.get_instance()

		self.types = {
			'CLAY': 0,
			'STONE': 1,
			'WOOD': 2
		}

		self.infos = TileInfos(100, 100)
		self.data_manager.load_tile('CLAY', 'CLAY.jpg', self.infos)
		self.data_manager.load_tile('STONE', 'STONE.jpg', self.infos)
		self.data_manager.load_tile('WOOD', 'WOOD.jpg', self.infos)

	def start(self):
		 pass

	def load_from_file(self, path = None):
		raw_map = []
		with open(path) as file:
			lines = file.readlines()
			for line in lines:
				row = []
				for char in line:
					if char != '\n':
						row.append(int(char))
				if len(row) > 0:
					raw_map.append(row)
		self.load(raw_map)

	def load(self,raw_map):
		self.raw_map = raw_map
		self.width = len(self.raw_map[0])
		self.height = len(self.raw_map)
		self.map = [[None for x in range(self.width)] for y in range(self.height)]
		for y in range(self.height):
			for x in range(self.width):
				position = Vector(x * self.infos.width + self.infos.width / 2.0, y * self.infos.height + self.infos.height / 2.0)
				value = self.raw_map[y][x]
				is_collider = False if value == 0 else True
				key = self.types.keys()[self.types.values().index(value)]
				self.map[y][x] = TileMap(key,self.gameobject, position, 0.0, Vector(self.infos.width, self.infos.height), self.data_manager, is_collider)


	def update(self,dt):
		 pass

	def fixed_update(self,fdt):
		 pass

	def save(self, path):
		if self.map is None:
			return

		msg = ''
		for y in range(len(self.map)):
			for x in range(len(self.map[0])):
				msg += str(self.types[self.map[y][x].id])
			msg += '\n'

		with open(path, 'w') as file:
			file.write(msg)

	def draw(self, screen):
		if self.map is None:
			return
		for y in range(len(self.map)):
			for x in range(len(self.map[0])):
				self.map[y][x].draw(screen)

	def draw_feature_map(self, id):
		if self.map is None:
			return
		for y in range(len(self.map)):
			for x in range(len(self.map[0])):
				self.map[y][x].draw_feature_map(id)

	def draw_debug(self, screen):
		if self.map is None:
			return
		for y in range(len(self.map)):
			for x in range(len(self.map[0])):
				self.map[y][x].draw_debug(screen)


	def z_buff(self, z_index, z_buffer):
		if self.map is None:
			return
		for y in range(len(self.map)):
			for x in range(len(self.map[0])):
				self.map[y][x].z_buff(z_index, z_buffer)
