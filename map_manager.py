# Map Manager
from data_manager import TileInfos

# ===================================================
# MAPMANAGER

class TileMap(object):
	def __init__(self, id, position, angle, scale, data_manager, is_collider = False):
		self.data_manager = data_manager
		self.id = id
		self.transform = Transform(position, angle, scale)
		self.collider = None
		if is_collider:
			self.collider = BoxCollider(None, self.transform, Vector(0.0, 0.0), Vector(1.0, 1.0))

	def draw(self, screen):
		tile = self.data_manager.get_tile(self.id)
		top_left = self.transform.get_position() - self.transform.get_scale() / 2.0
		screen.blit(tile.img, (top_left.x, top_left.y))
	
	def draw_debug(self, screen):
		if self.collider is not None:
			self.collider.draw_debug(screen)

	def z_buff(self, z_index, z_buffer):
		z_buffer.insert(z_index, self)

class MapManager(object):
	def __init__(self, data_manager):
		self.map = None
		self.width = 0
		self.height = 0
		self.data_manager = data_manager

		self.types = {
			'CLAY': 0,
			'STONE': 1,
			'WOOD': 2
		}

		self.infos = TileInfos(100, 100)
		data.load_tile('CLAY', 'CLAY.jpg', self.infos)
		data.load_tile('STONE', 'STONE.jpg', self.infos)
		data.load_tile('WOOD', 'WOOD.jpg', self.infos)

	def load(self, path = None):
		self.map = []
		with open(path) as file:
			lines = file.readlines()
			for line in lines:
				row = []
				for char in line:
					if char != '\n':
						row.append(int(char))
				if len(row) > 0:
					self.map.append(row)
		self.width = len(self.map[0])
		self.height = len(self.map)


		for y in range(len(self.map)):
			for x in range(len(self.map[0])):
				position = Vector(x * self.infos.width + self.infos.width / 2.0, y * self.infos.height + self.infos.height / 2.0)
				value = self.map[y][x]
				is_collider = False if value == 0 else True
				key = self.types.keys()[self.types.values().index(value)]
				self.map[y][x] = TileMap(key, position, 0.0, Vector(self.infos.width, self.infos.height), self.data_manager, is_collider)

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

# ===================================================
# EXAMPLE: Input Manager test with key actions

if __name__ == '__main__':
    from pygame import display, event, KEYDOWN, KEYUP, K_z, K_q, K_s, K_d, K_LSHIFT
    from time import clock
    from data_manager import DataManager, SpriteSheetInfos
    from animation import Animation, Animator
    from monobehaviour import MonoBehaviour
    from transform import Transform
    from collider import BoxCollider
    from vector import Vector
    from input_manager import InputManager
    from physics_manager import PhysicsManager
    from rigidbody import Rigidbody
    from z_buffer import ZBuffer

    # =====================================================================

    class Player(MonoBehaviour):
        def __init__(self, data_manager, bot = False):
            self.start(data_manager, bot)

        def start(self, data_manager, bot):
			self.bot = bot
            
            # ================= Transform =========================
			self.transform = Transform(Vector(0.0, 0.0), 0.0, Vector(100, 100))
			self.velocity = Vector(0.0, 0.0)
            
			self.speed = 200
			self.speed_factor = 2

			# ================= Collider ==========================
			self.collider = BoxCollider(None, self.transform, Vector(0.0, 25.0), Vector(0.3, 0.3))
			self.rb = Rigidbody(self.transform,self.collider)


			# ================= Animator ==========================
			self.animator = Animator()

			scale = self.transform.get_scale()
			infos = SpriteSheetInfos(6, 4, (scale.x, scale.y))
			data.load_sprite_sheet('TRUMP', 'TEST1.png', infos)
			spriteSheet = data.get_sprite_sheet('TRUMP')

			duration = 0.2
			self.animation_speed = 1
			self.animation_speed_factor = 1.5
			a_down = Animation(spriteSheet, [(i, 0) for i in range(6)], duration, self.animation_speed, loop = True)
			a_right = Animation(spriteSheet, [(i, 1) for i in range(6)], duration, self.animation_speed, loop = True)
			a_up = Animation(spriteSheet, [(i, 2) for i in range(6)], duration, self.animation_speed, loop = True)
			a_left = Animation(spriteSheet, [(i, 3) for i in range(6)], duration, self.animation_speed, loop = True)

			self.animator.add_animation('DOWN', a_down)
			self.animator.add_animation('RIGHT', a_right)
			self.animator.add_animation('UP', a_up)
			self.animator.add_animation('LEFT', a_left)

			self.animator.set_animation('DOWN')

			# ============== Input Manager =====================
			self.input_manager = InputManager.get_instance()

        def get_direction(self):
			move_x, move_y = 0, 0

			if self.input_manager.is_key_pressed('UP'):
				move_y = -1.0
			elif self.input_manager.is_key_pressed('DOWN'):
				move_y = 1.0
			if self.input_manager.is_key_pressed('LEFT'):
				move_x = -1.0
			elif self.input_manager.is_key_pressed('RIGHT'):
				move_x = 1.0

			return Vector(move_x, move_y).normalized()

        def set_all_speeds(self):
			if self.input_manager.is_key_down('LSHIFT'):
				self.animation_speed *= self.animation_speed_factor
				self.speed *= self.speed_factor
				self.animator.current_animation.set_speed(self.animation_speed)
			elif self.input_manager.is_key_up('LSHIFT'):
				self.animation_speed /= self.animation_speed_factor
				self.speed /= self.speed_factor
				self.animator.current_animation.set_speed(self.animation_speed)

        def set_animations(self):
        	if self.velocity.x < 0 and (self.velocity.y < 0 or self.velocity.y > 0):
        		self.animator.set_animation('LEFT')
        	elif self.velocity.x > 0 and (self.velocity.y < 0 or self.velocity.y > 0):
        		self.animator.set_animation('RIGHT')
        	elif self.velocity.x < 0:
        		self.animator.set_animation('LEFT')
        	elif self.velocity.x > 0:
        		self.animator.set_animation('RIGHT')
        	elif self.velocity.y < 0:
        		self.animator.set_animation('UP')
        	elif self.velocity.y > 0:
        		self.animator.set_animation('DOWN')

        def update(self, dt):
			self.animator.update(dt)

			if self.bot:
				return
			self.velocity = self.get_direction()
			self.set_all_speeds()
			self.set_animations()

        def fixed_update(self, fixed_dt):
            self.rb.set_velocity(self.velocity * self.speed)
            self.rb.update(fixed_dt)
            #self.transform.move(self.velocity * self.speed * fixed_dt)

        def test_collision(self, collider):
            if self.collider.try_collision(collider):
                print('Collision has been detected')

        def draw(self, screen):
            scale = self.transform.get_scale() / 2.0
            draw_pos = self.transform.get_position() - scale
            screen.blit(self.animator.current_sprite, (draw_pos.x, draw_pos.y))

        def z_buff(self, z_index, z_buffer):
        	z_buffer.insert(z_index, self)

    # ===== SCREEN ==================
    width = 800
    height = 600
    BLACK = (0, 0, 0)
    screen = display.set_mode((width, height))
    screen.fill(BLACK)

    # ===== ENTITIES ================
    data = DataManager()    
    z_buffer = ZBuffer()
    
    player = Player(data)
    player.transform.get_position().x = 6 * 100.0 + 50.0
    player.transform.get_position().y = 4 * 100.0 + 50.0

    fixed_bot = Player(data, bot = True)
    fixed_bot.transform.get_position().x = 100.0 + 50.0
    fixed_bot.transform.get_position().y = 100.0 + 50.0

    map_manager = MapManager(data)
    map_manager.load(path = 'MAP0.map')
    map_manager.save(path = 'MAP0SAVE.map')

    # ===== DELTA TIME ==============
    current_time = clock()
    dt = 0

    # ===== FIXED DELTA TIME ========
    current_fixed_time = clock()
    fixed_dt = 0
    fixed_rate = 0.02
    
    # ===== GET PhysicsManager ========
    pm = PhysicsManager.get_instance()

    # ===== LOOP ====================
    while True:
        InputManager.get_instance().update(event.get())

        screen.fill(BLACK)
        z_buffer.reset()

        # ====================================================================
        # ===== Update =====
        dt = clock() - current_time
        current_time += dt

        player.update(dt)
        fixed_bot.update(dt)

        # ===== FixedUpdate =====
        if current_fixed_time % fixed_rate:
            fixed_dt = clock() - current_fixed_time
            current_fixed_time += fixed_dt

            player.fixed_update(fixed_dt)
            fixed_bot.fixed_update(fixed_dt)
            pm.update_collision()
            #player.test_collision(fixed_bot.collider)

        # ===== Draw =====
        map_manager.z_buff(0, z_buffer)
        player.z_buff(2, z_buffer)
        fixed_bot.z_buff(2, z_buffer)

        z_buffer.draw(screen)

        map_manager.draw_debug(screen)
        player.collider.draw_debug(screen)
        fixed_bot.collider.draw_debug(screen)

        # ====================================================================
        display.flip()