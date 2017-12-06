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
from player import Player, PlayerStateIdle, PlayerStateWalkRunState

# ===================================================
# HUMANPLAYERSTATEWALKRUN

class HumanPlayerStateWalkRunState(PlayerStateWalkRunState):    
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

    def exit(self, player):
        return HumanPlayerStateIdle(player)

    def __str__(self):
        return 'Human Player State: Walk/Run'

# ===================================================
# HUMANSTATEIDLE

class HumanPlayerStateIdle(PlayerStateIdle):
    def update(self, dt, player): 
        up = player.input_manager.is_key_pressed('UP')
        down = player.input_manager.is_key_pressed('DOWN')
        left = player.input_manager.is_key_pressed('LEFT')
        right = player.input_manager.is_key_pressed('RIGHT')
        if up or down or left or right:
            self.does_exit = True

    def exit(self, player):
        return HumanPlayerStateWalkRunState(player)

    def __str__(self):
        return 'Human Player State: Idle'

# ===================================================
# HUMANPLAYER

class HumanPlayer(Player):
    def __init__(self,ennemy_name):
        Player.__init__(self,ennemy_name)

    def start(self):
        Player.start(self)

        # ================= State Machine =========================
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