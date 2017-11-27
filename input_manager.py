# Input Manager
from pygame import KEYDOWN, KEYUP, K_z, K_q, K_s, K_d, K_SPACE, K_LSHIFT

# ===================================================
# INPUTMANAGER

class InputManager(object):
	def __init__(self):
		self.key_booleans = {
			'UP': [False, K_z], 
			'DOWN': [False, K_s], 
			'LEFT': [False, K_q], 
			'RIGHT': [False, K_d],
			'FIRE1': [False, K_SPACE],
			'LSHIFT': [False, K_LSHIFT]
		}

		self.events = None
	
	instance = None

	@staticmethod
	def get_instance():
		if InputManager.instance is None:
			InputManager.instance = InputManager()
		return InputManager.instance

	def is_key_pressed(self, key):
		if key in self.key_booleans:
			return self.key_booleans[key][0]
		return False

	def is_key_down(self, key):
		if key in self.key_booleans:
			for e in self.events:
				if e.type == KEYDOWN:
					if e.key == self.key_booleans[key][1]:
						return True
		return False

	def is_key_up(self, key):
		if key in self.key_booleans:
			for e in self.events:
				if e.type == KEYUP:
					if e.key == self.key_booleans[key][1]:
						return True
		return False

	def update(self, events):
		self.events = events

		for e in events:
			if e.type == KEYDOWN:
				for key, value in self.key_booleans.iteritems():
					if e.key == value[1]:
						self.key_booleans[key][0] = True
			if e.type == KEYUP:
				for key, value in self.key_booleans.iteritems():
					if e.key == value[1]:
						self.key_booleans[key][0] = False

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

    # =====================================================================

    class Player(MonoBehaviour):
        def __init__(self, data_manager, bot = False):
            self.start(data_manager, bot)

        def start(self, data_manager, bot):
			self.bot = bot
            
            # ================= Transform =========================
			self.transform = Transform(Vector(0.0,0.0), 0.0, Vector(100, 100))
			self.velocity = Vector(0.0, 0.0)
            
			self.speed = 200
			self.speed_factor = 2

			# ================= Collider ==========================
			self.collider = BoxCollider(None, self.transform, Vector(0.0, 0.0), Vector(0.65, 0.8))

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
            self.transform.move(self.velocity * self.speed * fixed_dt)

        def test_collision(self, collider):
            if self.collider.try_collision(collider):
                print('Collision has been detected')

        def draw(self, screen):
            scale = self.transform.get_scale() / 2.0
            draw_pos = self.transform.get_position() - scale
            screen.blit(self.animator.current_sprite, (draw_pos.x, draw_pos.y))

    # ===== SCREEN ==================
    width = 800
    height = 600
    BLACK = (0, 0, 0)
    screen = display.set_mode((width, height))
    screen.fill(BLACK)

    # ===== ENTITIES ================
    data = DataManager()    
    
    player = Player(data)

    fixed_bot = Player(data, bot = True)
    fixed_bot.transform.get_position().x = 100.0
    fixed_bot.transform.get_position().y = 100.0

    # ===== DELTA TIME ==============
    current_time = clock()
    dt = 0

    # ===== FIXED DELTA TIME ========
    current_fixed_time = clock()
    fixed_dt = 0
    fixed_rate = 0.02

    # ===== LOOP ====================
    while True:
        InputManager.get_instance().update(event.get())

        screen.fill(BLACK)

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

            #player.test_collision(fixed_bot.collider)

        # ===== Draw =====
        player.draw(screen)
        fixed_bot.draw(screen)

        player.collider.draw_debug(screen)
        fixed_bot.collider.draw_debug(screen)

        # ====================================================================
        display.flip()
