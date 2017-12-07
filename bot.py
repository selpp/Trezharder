# Bot
from data_manager import DataManager, SpriteSheetInfos
from animation import Animation
from fsm import State
from vector import Vector
from player import Player, PlayerStateIdle, PlayerStateWalkRunState
from game_engine import GameEngineTools
import random as rnd
# ===================================================
# BOTSTATEWALKRUN

class BotStateWalkRunState(PlayerStateWalkRunState):
    def __init__(self, bot):
        PlayerStateWalkRunState.__init__(self, bot)

    def enter(self, bot):
        PlayerStateWalkRunState.enter(self, bot)
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

    def update(self, dt, bot): 
        PlayerStateWalkRunState.update(self, dt, bot)

    def exit(self, bot):
        return BotStateIdle(bot)

    def __str__(self):
        return 'Bot State: Walk/Run'

# ===================================================
# BOTSTATEIDLE

class BotStateIdle(PlayerStateIdle):
    def __init__(self, bot):
        PlayerStateIdle.__init__(self, bot)

    def update(self, dt, bot):
        x, y = bot.action_vector[0], bot.action_vector[1]
        if abs(x) > 0.01 or abs(y) > 0.01:
            self.does_exit = True

    def exit(self, bot):
        return BotStateWalkRunState(bot)

    def __str__(self):
        return 'Bot State: Idle'

# ===================================================
# BOTSTATEEXPLODE

class  BotStateExplode(State):
    def __init__(self, bot):
        self.does_exit = False
        self.enter(bot)

    def enter(self, bot):
        bot.animator.set_animation('EXPLODE')
        bot.gameobject.rigidbody.set_velocity(Vector(0,0))

    def update(self, dt, bot):
        if bot.animator.current_animation_finished:
            self.does_exit = True
        return

    def fixed_update(self, fixed_dt, bot):
        pass

    def exit(self, bot):
        return BotDeathState(bot)

    def __str__(self):
        return 'Bot State: Explode'
        
class  BotDeathState(State):
    def __init__(self, bot):
        self.does_exit = False
        self.enter(bot)

    def enter(self, bot):
        GameEngineTools.DestroyObject(bot.gameobject)
        
    def update(self, dt, bot):
        pass

    def fixed_update(self, fixed_dt, bot):
        pass

    def exit(self, bot):
        return None

    def __str__(self):
        return 'Bot State: RIP'

# ===================================================
# BOT

class Bot(Player):
    def __init__(self,is_rnd = True):
        self.action_vector = [0 for i in range(4)]
        self.explode = False
        self.rip = False
        self.is_rnd = is_rnd
        if not self.is_rnd:
            self.action_vector[3] = 1
        Player.__init__(self)

    def start(self):
        Player.start(self)

        # ================= State Machine =========================
        self.state_machine.state = BotStateIdle(self)
        self.explode = False

        # ================= Animator ==========================
        scale = Vector(128.0, 128.0)
        infos = SpriteSheetInfos(4, 4, (scale.x, scale.y))
        data_manager = DataManager.get_instance()
        data_manager.load_sprite_sheet('EXPLOSION', 'EXPLOSION.png', infos)
        spriteSheet = data_manager.get_sprite_sheet('EXPLOSION')
        duration = 0.2
        anim_pos = [(x, y) for y in range(4) for x in range(4)]
        a_explode = Animation(spriteSheet, anim_pos, duration, 1, loop = False)

        self.animator.add_animation('EXPLODE', a_explode)

    def update(self, dt):
        Player.update(self, dt)

    def fixed_update(self, fixed_dt):
        if self.rip:
            return
        Player.fixed_update(self, fixed_dt)
        for ennemy in self.ennemies:
            if ennemy is None or ennemy is self.gameobject or not ennemy.is_alive:
                continue
            if self.action_vector[3] and (ennemy.transform.get_position() - self.transform.get_position()).magnitude() < 100.0:
        		    self.explode = True
        		    self.state_machine.state = BotStateExplode(self) 
        		    self.rip = True
        if self.is_rnd:
            if rnd.randint(0,10) == 10:
                self.action_vector = [rnd.randint(-1,1),rnd.randint(-1,1),rnd.randint(0,1),1 if rnd.randint(0,10) > 7 else 0]
    
    def draw(self, screen):
        Player.draw(self, screen)

    def z_buff(self, z_index, z_buffer):
        Player.z_buff(self, z_index, z_buffer)