# Human Player
from input_manager import InputManager
from vector import Vector
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
    def __init__(self):
        Player.__init__(self)

    def start(self):
        Player.start(self)

        # ================= State Machine =========================
        self.state_machine.state = HumanPlayerStateIdle(self)

        # ================= Input Manager =========================
        self.input_manager = InputManager.get_instance()
    
    def on_collision(self,collider):
        print('yeah')