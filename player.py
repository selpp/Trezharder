# Player
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
		self.timer = 0
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

		up = player.input_manager.is_key_pressed('UP')
		down = player.input_manager.is_key_pressed('DOWN')
		left = player.input_manager.is_key_pressed('LEFT')
		right = player.input_manager.is_key_pressed('RIGHT')

		if up:
			move_y = -1.0
		elif down:
			move_y = 1.0
		if left:
			move_x = -1.0
		elif right:
			move_x = 1.0

		if not(up or down or left or right):
			self.does_exit = True

		player.velocity.set(Vector(move_x, move_y).normalized())

	def set_all_speeds(self, player):
		if player.input_manager.is_key_down('LSHIFT'):
			self.animation_speed = self.initial_animation_speed * self.animation_speed_factor
			self.speed = self.initial_speed * self.speed_factor
			player.animator.current_animation.set_speed(self.animation_speed)
		elif player.input_manager.is_key_up('LSHIFT'):
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
		player.rigidbody.set_velocity(player.velocity * self.speed)
		player.rigidbody.update(fixed_dt)

	def exit(self, player):
		return PlayerStateIdle(player)

	def __str__(self):
		return 'Player State: Walk/Run'

# ===================================================
# PLAYERSTATEIDLE

class PlayerStateIdle(State):
	def __init__(self, player):
		self.does_exit = False
		self.timer = 0
		self.enter(player)

	def enter(self, player):
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
		up = player.input_manager.is_key_pressed('UP')
		down = player.input_manager.is_key_pressed('DOWN')
		left = player.input_manager.is_key_pressed('LEFT')
		right = player.input_manager.is_key_pressed('RIGHT')
		if up or down or left or right:
			self.does_exit = True

	def fixed_update(self, fixed_dt, player):
		pass

	def exit(self, player):
		return PlayerStateWalkRunState(player)

	def __str__(self):
		return 'Player State: Idle'

# ===================================================
# PLAYER

class Player(MonoBehaviour):
    def __init__(self, data_manager):
        self.start(data_manager)

    def start(self, data_manager):
		self.state_machine = PlayerFSM()

		# ================= Transform =========================
		self.transform = Transform(Vector(0.0, 0.0), 0.0, Vector(100, 100),tag='player')
		self.velocity = Vector(0.0, 0.0)        

		# ================= Collider ==========================
		self.collider = BoxCollider(None, self.transform, Vector(0.0, 25.0), Vector(0.3, 0.3))
		self.rigidbody = Rigidbody(self.transform,self.collider)

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

		self.animator.add_animation('DOWN', a_down)
		self.animator.add_animation('RIGHT', a_right)
		self.animator.add_animation('UP', a_up)
		self.animator.add_animation('LEFT', a_left)
		self.animator.add_animation('IDLE_DOWN', a_idle_down)
		self.animator.add_animation('IDLE_RIGHT', a_idle_right)
		self.animator.add_animation('IDLE_UP', a_idle_up)
		self.animator.add_animation('IDLE_LEFT', a_idle_left)

		# ============== Input Manager =====================
		self.input_manager = InputManager.get_instance()
		
		self.state_machine.state = PlayerStateIdle(self)

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

# ===================================================
# EXAMPLE

if __name__ == '__main__':
    from pygame import display
    from time import clock
    from map_manager import MapManager

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

    map_manager = MapManager(data)
    map_manager.load(path = 'MAP0.map')

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

        # ===== FixedUpdate =====
        if current_fixed_time % fixed_rate:
            fixed_dt = clock() - current_fixed_time
            current_fixed_time += fixed_dt

            player.fixed_update(fixed_dt)
            pm.update_collision()

        # ===== Draw =====
        map_manager.z_buff(0, z_buffer)
        player.z_buff(2, z_buffer)

        z_buffer.draw(screen)

        # ====================================================================
        display.flip()
