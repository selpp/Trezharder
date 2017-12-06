# Bot
from pygame import event, KEYDOWN, KEYUP, K_z, K_q, K_s, K_d, K_LSHIFT
from data_manager import DataManager, SpriteSheetInfos
from animation import Animation, Animator
from monobehaviour import MonoBehaviour
from input_manager import InputManager
from physics_manager import PhysicsManager
from rigidbody import Rigidbody
from z_buffer import ZBuffer
from fsm import State, FSM
from transform import Transform
from vector import Vector
from collider import BoxCollider

# ===================================================
# BOTFSM

class BotFSM(FSM):
	def __init__(self):
		FSM.__init__(self)

	def update(self, dt, bot):
		if self.state.does_exit:
			self.state = self.state.exit(bot)
		else:
			self.state.update(dt, bot)

	def fixed_update(self, fixed_dt, bot):
		if self.state.does_exit:
			return
		else:
			self.state.fixed_update(fixed_dt, bot)

# ===================================================
# BOTSTATEWALKRUN

class BotStateWalkRunState(State):
	def __init__(self, bot):
		self.does_exit = False
		self.timer = 0
		self.explode = False
		self.enter(bot)

	def enter(self, bot):
		self.initial_speed = 200
		self.speed = 200
		self.speed_factor = 2

		self.initial_animation_speed = 1
		self.animation_speed = 1
		self.animation_speed_factor = 1.5
		bot.animator.set_animation('DOWN')

		self.shift = False
    
	def get_direction(self, bot):
		move_x, move_y = bot.action_vector[0], bot.action_vector[1]

		if abs(move_x) < 0.01 and abs(move_y) < 0.01:
			self.does_exit = True

		bot.velocity.set(Vector(move_x, move_y).normalized())

	def set_all_speeds(self, bot):
		shift = (bot.action_vector[2] > 0.5)
		if not self.shift and shift:
			self.shift = shift
			self.animation_speed = self.initial_animation_speed * self.animation_speed_factor
			self.speed = self.initial_speed * self.speed_factor
			bot.animator.current_animation.set_speed(self.animation_speed)
		elif self.shift and not shift:
			self.shift = shift
			self.animation_speed = self.initial_animation_speed
			self.speed = self.initial_speed
			bot.animator.current_animation.set_speed(self.animation_speed)

	def set_animations(self, bot):
		if bot.velocity.x < 0 and (bot.velocity.y < 0 or bot.velocity.y > 0):
			bot.animator.set_animation('LEFT')
		elif bot.velocity.x > 0 and (bot.velocity.y < 0 or bot.velocity.y > 0):
			bot.animator.set_animation('RIGHT')
		elif bot.velocity.x < 0:
			bot.animator.set_animation('LEFT')
		elif bot.velocity.x > 0:
			bot.animator.set_animation('RIGHT')
		elif bot.velocity.y < 0:
			bot.animator.set_animation('UP')
		elif bot.velocity.y > 0:
			bot.animator.set_animation('DOWN')

	def update(self, dt, bot): 
		if bot.action_vector[3] == 1:
			self.explode = True
			self.does_exit = True
		else: 
			self.get_direction(bot)
			self.set_all_speeds(bot)
			self.set_animations(bot)

	def fixed_update(self, fixed_dt, bot):
		bot.rigidbody.set_velocity(bot.velocity * self.speed)
		bot.rigidbody.update(fixed_dt)

	def exit(self, bot):
		if self.explode:
			return BotStateExplode(bot)
		return BotStateIdle(bot)

	def __str__(self):
		return 'Bot State: Walk/Run'

# ===================================================
# BOTSTATEIDLE

class BotStateIdle(State):
	def __init__(self, bot):
		self.does_exit = False
		self.timer = 0
		self.enter(bot)
		self.explode = False

	def enter(self, bot):
		current_animation_id = bot.animator.current_animation_id
		if current_animation_id is None:
 			bot.animator.set_animation('IDLE_DOWN')
 		elif current_animation_id == 'UP':
 			bot.animator.set_animation('IDLE_UP')
 		elif current_animation_id == 'DOWN':
 			bot.animator.set_animation('IDLE_DOWN')
 		elif current_animation_id == 'LEFT':
 			bot.animator.set_animation('IDLE_LEFT')
 		elif current_animation_id == 'RIGHT':
 			bot.animator.set_animation('IDLE_RIGHT')

	def update(self, dt, bot):
		if bot.action_vector[3] == 1:
			self.explode = True
			does_exit = True
		else: 
			x, y = bot.action_vector[0], bot.action_vector[1]
			if abs(x) > 0.01 or abs(y) > 0.01:
				self.does_exit = True

	def fixed_update(self, fixed_dt, bot):
		pass

	def exit(self, bot):
		if self.explode:
			return BotStateExplode(bot)
		return BotStateWalkRunState(bot)

	def __str__(self):
		return 'Bot State: Idle'

# ===================================================
# BOTSTATEEXPLODE

class  BotStateExplode(State):
	def __init__(self, bot):
		self.does_exit = False
		self.timer = 0
		self.enter(bot)

	def enter(self, bot):
 		bot.animator.set_animation('EXPLODE')

	def update(self, dt, bot):
		if bot.explode:
			return
		if bot.animator.current_animation_finished:
			bot.explode = True

	def fixed_update(self, fixed_dt, bot):
		pass

	def exit(self, bot):
		return None

	def __str__(self):
		return 'Bot State: Explode'

# ===================================================
# BOT

class Bot(MonoBehaviour):
    def __init__(self, data_manager):
        self.start(data_manager)

    def start(self, data_manager):
		self.state_machine = BotFSM()
		self.action_vector = [0, 0, 0]
		self.explode = False

		# ================= Transform =========================
		self.transform = Transform(Vector(0.0, 0.0), 0.0, Vector(100, 100))
		self.velocity = Vector(0.0, 0.0)

		# ================= Collider ==========================
		self.collider = BoxCollider(None, self.transform, Vector(0.0, 25.0), Vector(0.3, 0.3))
		self.rigidbody = Rigidbody(self.transform, self.collider)

		# ================= Animator ==========================
		self.animator = Animator()

		scale = self.transform.get_scale()
		infos = SpriteSheetInfos(6, 4, (scale.x, scale.y))
		data_manager.load_sprite_sheet('TRUMP', 'TEST1.png', infos)
		spriteSheet = data_manager.get_sprite_sheet('TRUMP')
		duration = 0.2
		a_down = Animation(spriteSheet, [(i, 0) for i in range(6)], duration, 1, loop = True)
		a_right = Animation(spriteSheet, [(i, 1) for i in range(6)], duration, 1, loop = True)
		a_up = Animation(spriteSheet, [(i, 2) for i in range(6)], duration, 1, loop = True)
		a_left = Animation(spriteSheet, [(i, 3) for i in range(6)], duration, 1, loop = True)
		a_idle_down = Animation(spriteSheet, [(1, 0)], duration, 1, loop = True)
		a_idle_right = Animation(spriteSheet, [(1, 1)], duration, 1, loop = True)
		a_idle_up = Animation(spriteSheet, [(1, 2)], duration, 1, loop = True)
		a_idle_left = Animation(spriteSheet, [(1, 3)], duration, 1, loop = True)

		scale = Vector(128.0, 128.0)
		infos = SpriteSheetInfos(4, 4, (scale.x, scale.y))
		data_manager.load_sprite_sheet('EXPLOSION', 'EXPLOSION.png', infos)
		spriteSheet = data_manager.get_sprite_sheet('EXPLOSION')
		duration = 0.2
		anim_pos = [(x, y) for y in range(4) for x in range(4)]
		a_explode = Animation(spriteSheet, anim_pos, duration, 1, loop = False)

		self.animator.add_animation('DOWN', a_down)
		self.animator.add_animation('RIGHT', a_right)
		self.animator.add_animation('UP', a_up)
		self.animator.add_animation('LEFT', a_left)
		self.animator.add_animation('IDLE_DOWN', a_idle_down)
		self.animator.add_animation('IDLE_RIGHT', a_idle_right)
		self.animator.add_animation('IDLE_UP', a_idle_up)
		self.animator.add_animation('IDLE_LEFT', a_idle_left)
		self.animator.add_animation('EXPLODE', a_explode)

		self.state_machine.state = BotStateIdle(self)

    def update(self, dt):
		self.animator.update(dt)
		self.state_machine.update(dt, self)

    def fixed_update(self, fixed_dt):
    	self.state_machine.fixed_update(fixed_dt, self)

    def draw(self, screen):
        scale = self.transform.get_scale() / 2.0
        draw_pos = self.transform.get_position() - scale
        screen.blit(self.animator.current_sprite, (draw_pos.x, draw_pos.y))

    def z_buff(self, z_index, z_buffer):
    	z_buffer.insert(z_index, self)