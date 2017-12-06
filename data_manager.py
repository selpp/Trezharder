# Data Manager
from pygame import image, Surface, Rect

# ===================================================
# DATAMANAGER

class DataManager(object):
	def __init__(self):
		self.sprite_sheets = {}
		self.tiles = {}
    
	instance = None
	@staticmethod
	def get_instance():
		if DataManager.instance is None:
			DataManager.instance = DataManager()
		return DataManager.instance
         
    
	def load_sprite_sheet(self, id, sprite_sheet_path, infos):
		if id in self.sprite_sheets:
			return
		img = image.load(sprite_sheet_path)
		self.sprite_sheets[id] = SpriteSheet(img, infos)

	def load_tile(self, id, tile_path, infos):
		if id in self.tiles:
			return
		img = image.load(tile_path)
		self.tiles[id] = Tile(img, infos)

	def get_sprite_sheet(self, id):
		if id in self.sprite_sheets:
			return self.sprite_sheets[id]
		raise NameError('Sprtie sheet ' + str(id) + ' does not exist')

	def get_tile(self, id):
		if id in self.tiles:
			return self.tiles[id]
		raise NameError('Tile ' + str(id) + ' does not exist')

	def __str__(self):
		msg = 'Data Manager:\n  Sprite sheets: '
		msg += ' '.join(id for id in self.sprite_sheets)
		msg += '\n  Tiles: '
		msg += ' '.join(id for id in self.tiles)
		return msg

# ===================================================
# SPRITESHEET

class SpriteSheetInfos(object):
	def __init__(self, col, row, size):
		self.row = row
		self.col = col
		self.size = size

	def __str__(self):
		msg = '(row: ' + str(self.row)
		msg += ' col: ' + str(self.col)
		msg += ' size: ' + str(self.size) + ')'
		return msg

class SpriteSheet(object):
	def __init__(self, sprite_sheet_image, infos):
		self.img = sprite_sheet_image
		self.infos = infos

	def get_sprite(self, col, row):
		location = (col * self.infos.size[0], row * self.infos.size[1])
		sprite = self.img.subsurface(Rect(location, self.infos.size))
		return sprite

# ===================================================
# TILE

class TileInfos(object):
	def __init__(self, width, height):
		self.width = width
		self.height = height

	def __str__(self):
		msg = '(width: ' + str(self.width)
		msg += ' height: ' + str(self.height)
		msg += ')'
		return msg

class Tile(object):
	def __init__(self, tile_image, infos):
		self.img = tile_image
		self.infos = infos