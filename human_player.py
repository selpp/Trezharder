# Human Player
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
from player import Player

# ===================================================
# HUMANPLAYERFSM

class HumanPlayerFSM(FSM):
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
# HUMANPLAYERSTATEWALKRUN

class HumanPlayerStateWalkRunState(State):
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
        player.rigidbody.fixed_update(fixed_dt)

    def exit(self, player):
        return HumanPlayerStateIdle(player)

    def __str__(self):
        return 'Player State: Walk/Run'

# ===================================================
# HUMANSTATEIDLE

class HumanPlayerStateIdle(State):
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
        return HumanPlayerStateWalkRunState(player)

    def __str__(self):
        return 'Player State: Idle'

# ===================================================
# HUMANPLAYER

class HumanPlayer(Player):
    def __init__(self):
        Player.__init__(self)

    def start(self):
        Player.start(self)

        # ================= State Machine =========================
        self.state_machine = HumanPlayerFSM()
        self.state_machine.state = HumanPlayerStateIdle(self)

        # ================= Input Manager =========================
        self.input_manager = InputManager.get_instance()
        
    def update(self, dt):
        Player.update(self, dt)

    def fixed_update(self, fixed_dt):
        Player.fixed_update(self, fixed_dt)

    def draw(self, screen):
        Player.draw(self, screen)

    def z_buff(self, z_index, z_buffer):
        Player.z_buff(self, z_index, z_buffer)