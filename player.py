from data_manager import DataManager, SpriteSheetInfos
from animation import Animation, Animator
from monobehaviour import MonoBehaviour
from vector import Vector
from collider import BoxCollider
from game_engine import GameEngineTools
from fsm import State, FSM
import pygame
from pygame import Rect, transform

# ===================================================
# PLAYERFSM

class PlayerFSM(FSM):
	def __init__(self):
		FSM.__init__(self)

	def update(self, dt, player):
		if self.state.does_exit:
			self.state = self.state.exit(player)
		else:
			self.state.update(dt, player)

	def fixed_update(self, fixed_dt, player):
		if self.state.does_exit:
			return
		else:
			self.state.fixed_update(fixed_dt, player)

# ===================================================
# PLAYERSTATEWALKRUN

class PlayerStateWalkRunState(State):
	def __init__(self, player):
		self.does_exit = False
		self.enter(player)

	def enter(self, player):
		self.initial_speed = 200
		self.speed = 200
		self.speed_factor = 2

		self.initial_animation_speed = 1
		self.animation_speed = 1
		self.animation_speed_factor = 1.5
		player.animator.set_animation('DOWN')

	def get_direction(self, player):
		move_x, move_y = 0, 0

		if player.command.up:
			move_y -= 1.0
		if player.command.down:
			move_y += 1.0
		if player.command.left:
			move_x -= 1.0
		if player.command.right:
			move_x += 1.0

		if not(player.command.up or player.command.down or player.command.left or player.command.right):
			self.does_exit = True

		player.velocity.set(Vector(move_x, move_y).normalized())

	def set_all_speeds(self, player):
		if player.command.just_pressed(player.command.prev_A,player.command.A):
			self.animation_speed = self.initial_animation_speed * self.animation_speed_factor
			self.speed = self.initial_speed * self.speed_factor
			player.animator.current_animation.set_speed(self.animation_speed)
		elif player.command.just_released(player.command.prev_A,player.command.A):
			self.animation_speed = self.initial_animation_speed
			self.speed = self.initial_speed
			player.animator.current_animation.set_speed(self.animation_speed)

	def set_animations(self, player):
		if player.velocity.x < 0 and (player.velocity.y < 0 or player.velocity.y > 0):
			player.animator.set_animation('LEFT')
		elif player.velocity.x > 0 and (player.velocity.y < 0 or player.velocity.y > 0):
			player.animator.set_animation('RIGHT')
		elif player.velocity.x < 0:
			player.animator.set_animation('LEFT')
		elif player.velocity.x > 0:
			player.animator.set_animation('RIGHT')
		elif player.velocity.y < 0:
			player.animator.set_animation('UP')
		elif player.velocity.y > 0:
			player.animator.set_animation('DOWN')

	def update(self, dt, player):
		self.get_direction(player)
		self.set_all_speeds(player)
		self.set_animations(player)

	def fixed_update(self, fixed_dt, player):
		player.gameobject.rigidbody.set_velocity(player.velocity * self.speed)
		player.gameobject.rigidbody.fixed_update(fixed_dt)

	def exit(self, player):
		return PlayerStateIdle(player)

	def __str__(self):
		return 'Player State: Walk/Run'

# ===================================================
# PLAYERSTATEIDLE

class PlayerStateIdle(State):
	def __init__(self, player):
		self.does_exit = False
		self.enter(player)

	def enter(self, player):
		player.velocity.set(Vector(0.0, 0.0))
		player.gameobject.rigidbody.set_velocity(player.velocity)

		current_animation_id = player.animator.current_animation_id
		if current_animation_id is None:
			player.animator.set_animation('IDLE_DOWN')
		elif current_animation_id == 'UP':
			player.animator.set_animation('IDLE_UP')
		elif current_animation_id == 'DOWN':
			player.animator.set_animation('IDLE_DOWN')
		elif current_animation_id == 'LEFT':
			player.animator.set_animation('IDLE_LEFT')
		elif current_animation_id == 'RIGHT':
			player.animator.set_animation('IDLE_RIGHT')

	def update(self, dt, player):
		if player.command.up or player.command.down or player.command.left or player.command.right:
			self.does_exit = True

	def fixed_update(self, fixed_dt, player):
		player.gameobject.rigidbody.fixed_update(fixed_dt)

	def exit(self, player):
		return PlayerStateWalkRunState(player)

	def __str__(self):
		return 'Player State: Idle'


class  PlayerStateExplode(State):
	def __init__(self, player):
		self.does_exit = False
		self.enter(player)

	def enter(self, player):
		player.animator.set_animation('EXPLODE')
		player.gameobject.rigidbody.set_velocity(Vector(0,0))
		data_manager = DataManager.get_instance()
		# data_manager.sounds['EXPLODE'].play()

	def update(self, dt, player):
		if player.explode:
			if player.animator.current_animation_finished:
				self.does_exit = True
			return
		if player.animator.current_animation_finished:
			player.explode = True

	def fixed_update(self, fixed_dt, bot):
		pass

	def exit(self, player):
		return PlayerDeathState(player)

	def __str__(self):
		return 'Bot State: Explode'


class  PlayerDeathState(State):
	def __init__(self, player):
		self.does_exit = False
		self.enter(player)

	def enter(self, player):
		GameEngineTools.DestroyObject(player.gameobject)

	def update(self, dt, player):
		pass

	def fixed_update(self, fixed_dt, player):
		pass

	def exit(self, player):
		return None

	def __str__(self):
		return 'Bot State: RIP'

# ===================================================
# PLAYER

class Player(MonoBehaviour):
	def __init__(self,command,color,ennemies_name=''):
		MonoBehaviour.__init__(self,1)
		self.command = command
		self.color = color
		self.ennemies_name = ennemies_name

	def start(self):
		# ================= State Machine =========================
		self.state_machine = PlayerFSM()
		self.ennemies = GameEngineTools.find_all(self.ennemies_name)
		self.rip = False
		self.murderer = False
		# ================= Transform =========================
		self.transform.get_scale().x = 100
		self.transform.get_scale().y = 100
		self.transform.tag = 'player'
		self.velocity = Vector(0.0, 0.0)
		self.explode = False

		# ================= Collider ==========================
		self.gameobject.rigidbody.set_collider(BoxCollider(self.transform, Vector(0.0, 25.0), Vector(0.3, 0.3) , self.gameobject))
		# ================= Animator ==========================
		self.animator = Animator()

		scale = self.transform.get_scale()
		infos = SpriteSheetInfos(6, 4, (scale.x, scale.y))
		data_manager = DataManager.get_instance()
		if self.color == 0:
			data_manager.load_sprite_sheet('TRUMP1', 'TEST1.png', infos)
			spriteSheet = data_manager.get_sprite_sheet('TRUMP1')
		else:
			data_manager.load_sprite_sheet('TRUMP2', 'TEST2.png', infos)
			spriteSheet = data_manager.get_sprite_sheet('TRUMP2')
		duration = 0.6
		a_down = Animation(spriteSheet, [(i, 0) for i in range(6)], duration, 1, loop = True)
		a_right = Animation(spriteSheet, [(i, 1) for i in range(6)], duration, 1, loop = True)
		a_up = Animation(spriteSheet, [(i, 2) for i in range(6)], duration, 1, loop = True)
		a_left = Animation(spriteSheet, [(i, 3) for i in range(6)], duration, 1, loop = True)
		a_idle_down = Animation(spriteSheet, [(1, 0)], duration, 1, loop = True)
		a_idle_right = Animation(spriteSheet, [(1, 1)], duration, 1, loop = True)
		a_idle_up = Animation(spriteSheet, [(1, 2)], duration, 1, loop = True)
		a_idle_left = Animation(spriteSheet, [(1, 3)], duration, 1, loop = True)

		self.animator.add_animation('DOWN', a_down)
		self.animator.add_animation('RIGHT', a_right)
		self.animator.add_animation('UP', a_up)
		self.animator.add_animation('LEFT', a_left)
		self.animator.add_animation('IDLE_DOWN', a_idle_down)
		self.animator.add_animation('IDLE_RIGHT', a_idle_right)
		self.animator.add_animation('IDLE_UP', a_idle_up)
		self.animator.add_animation('IDLE_LEFT', a_idle_left)

		scale = Vector(128.0, 128.0)
		infos = SpriteSheetInfos(4, 4, (scale.x, scale.y))
		data_manager = DataManager.get_instance()
		data_manager.load_sprite_sheet('EXPLOSION', 'EXPLOSION.png', infos)
		spriteSheet = data_manager.get_sprite_sheet('EXPLOSION')
		duration = 0.2
		anim_pos = [(x, y) for y in range(4) for x in range(4)]
		a_explode = Animation(spriteSheet, anim_pos, duration, 1, loop = False)

		self.animator.add_animation('EXPLODE', a_explode)

		# ===================== Sound ========================
		# data_manager.load_sound('EXPLODE', 'EXPLODE.wav')

		self.state_machine.state = PlayerStateIdle(self)

		# Params
		self.range = 50.0

	def update(self, dt):
		self.animator.update(dt)
		self.state_machine.update(dt, self)

	def fixed_update(self, fixed_dt):
		self.murderer = False
		self.state_machine.fixed_update(fixed_dt, self)
		if self.rip:
			return

		self.command.update_command()

		if self.command.B:
			self.try_kill()

	def try_kill(self):
		for ennemy in self.ennemies:
			if ennemy is None or ennemy is self.gameobject or not ennemy.is_alive:
				continue
			if (ennemy.transform.get_position() - self.transform.get_position()).magnitude() < self.range:
					ennemy.get_mono(Player).die()
					self.murderer = True

	def die(self):
		self.rip = True
		self.state_machine.state = PlayerStateExplode(self)

	def draw(self, screen):
		scale = self.transform.get_scale()
		scale_half = scale / 2.0
		draw_pos = self.transform.get_position() - scale_half
		resized = transform.scale(self.animator.current_sprite, (scale.x, scale.y))
		screen.blit(resized, (draw_pos.x, draw_pos.y))

	def draw_collision_vision(self, screen):
		if self.rip or self.color == 1:
			return
		x, y, w, h = self.gameobject.rigidbody.collider.get_world_box()
		color = (120, 120, 120)
		pygame.draw.rect(screen, color, Rect(x - w, y - h, w * 2, h * 2))

	def draw_player_vision(self, screen):
		if self.rip or self.color == 0:
			return
		x, y, w, h = self.gameobject.rigidbody.collider.get_world_box()
		color = (255, 255, 255)
		pygame.draw.rect(screen, color, Rect(x - w, y - h, w * 2, h * 2))

	def draw_range_vision(self, screen):
		if self.rip or self.color == 0:
			return
		pos = self.transform.get_position()
		half_range = self.range / 2.0
		color = (255, 255, 255)
		pygame.draw.circle(screen, color, (int(pos.x), int(pos.y)), int(self.range))

	def draw_feature_map(self, id):
		if not id in DataManager.get_instance().feature_maps:
			return
		if id == 'COLLISIONS':
			self.draw_collision_vision(DataManager.instance.feature_maps[id])
		elif id == 'PLAYER':
			self.draw_player_vision(DataManager.instance.feature_maps[id])
		elif id == 'RANGE':
			self.draw_range_vision(DataManager.instance.feature_maps[id])

	def z_buff(self, z_index, z_buffer):
		z_buffer.insert(z_index, self)
