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

# ===================================================
# EXAMPLE: Data Manager to load sprites

if __name__ == '__main__':
	from pygame import display
	from time import clock

	data = DataManager()

	infos = SpriteSheetInfos(6, 4, (600/6, 400/4))
	data.load_sprite_sheet('TEST1', 'TEST1.png', infos)
	spriteSheet = data.get_sprite_sheet('TEST1')
	print str(data)

	infos = TileInfos(100, 100)
	data.load_tile('CLAY', 'CLAY.jpg', infos)
	tile = data.get_tile('CLAY')
	print str(data)

	width = 800
	height = 600
	BLACK = (0, 0, 0)
	screen = display.set_mode((width, height))
	screen.fill(BLACK)

	current_time = clock()
	dt = 0

	index = 0
	anim_timer = 0
	sprite = spriteSheet.get_sprite(index, 0)
	rate = 0.02

	while True:
		screen.fill(BLACK)
		dt = clock() - current_time
		current_time += dt

		screen.blit(tile.img, (0, 0))

		# ====== ANIMATION =============
		anim_timer += dt

		if index > 5:
			index = 0

		screen.blit(sprite, (0, 0))
		if anim_timer > rate:
			anim_timer = 0
			sprite = spriteSheet.get_sprite(index, 0)
			index += 1
		# ==============================
		
		display.flip()