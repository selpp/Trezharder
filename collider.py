# -*- coding: utf-8 -*-
from abc import ABCMeta , abstractmethod
from transform import Transform
from vector import Vector
from pygame import draw, Rect

class Collider:
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def __init__(self,collision_handler,parent_transform,position,scale):
        self.handler = collision_handler
        self.position = position
        self.parent_transform = parent_transform
        self.scale = scale
    
    def on_collision(self):
        self.handler()
        
    @abstractmethod
    def try_collision(self,collider):
        pass

    @abstractmethod
    def draw_debug(self):
        pass
    
    
class BoxCollider(Collider):
    def __init__(self,collision_handler,parent_transform,position,scale):
        Collider.__init__(self,collision_handler,parent_transform,position,scale)
        
    def try_collision(self,collider):
        if isinstance(collider,BoxCollider):
            return self.collision_with_box(collider)
        
    def collision_with_box(self,box):
        x,y,w,h = self.get_world_box()
        x2,y2,w2,h2 = box.get_world_box()
        left_one , right_one = ((x2,y2,w2,h2) , (x,y,w,h)) if x2 < x else ((x,y,w,h) , (x2,y2,w2,h2))
        down_one , up_one = ((x2,y2,w2,h2) , (x,y,w,h)) if y2 < y else ((x,y,w,h) , (x2,y2,w2,h2))
        if left_one[0] + left_one[2] > right_one[0] - right_one[2]:
            if down_one[1] + down_one[3] > up_one[1] - up_one[3]:
                return True
        return False
        
    def get_world_box(self):
        x = self.position.x + self.parent_transform.get_position().x
        y = self.position.y + self.parent_transform.get_position().y
        w = self.scale.x * self.parent_transform.get_scale().x / 2.0
        h = self.scale.y * self.parent_transform.get_scale().y / 2.0
        
        return x,y,w,h

    def draw_debug(self, screen):
        x, y, w, h = self.get_world_box()
        top_left_x = x - w
        top_left_y = y - h 

        draw.rect(screen, (0, 255, 0), Rect((top_left_x, top_left_y), (w * 2, 1)))
        draw.rect(screen, (0, 255, 0), Rect((top_left_x, top_left_y + h * 2), (w * 2, 1)))

        draw.rect(screen, (0, 255, 0), Rect((top_left_x, top_left_y), (1, h * 2)))
        draw.rect(screen, (0, 255, 0), Rect((top_left_x + w * 2, top_left_y), (1, h * 2)))

if __name__ == '__main__':
    from pygame import display, event, KEYDOWN, KEYUP, K_z, K_q, K_s, K_d, K_LSHIFT
    from time import clock
    from data_manager import DataManager, SpriteSheetInfos
    from animation import Animation, Animator
    from monobehaviour import MonoBehaviour
    from transform import Transform
    
    # ====== TEST =========================================================
    t1 = Transform(Vector(0.0,0.0),0.0,Vector(1.0,1.0))
    t2 = Transform(Vector(1.0,1.0),0.0,Vector(1.0,1.0))
    b1 = BoxCollider(None,t1,Vector(0.0,0.0),Vector(1,1))
    b2 = BoxCollider(None,t2,Vector(0.0,0.0),Vector(0.99999,0.99999))
    b3 = BoxCollider(None,t2,Vector(0.0,0.0),Vector(1.000001,1.0000001))
    print(b1.try_collision(b2))
    print(b1.try_collision(b3))
    print(b2.try_collision(b3))
    # =====================================================================

    class Player(MonoBehaviour):
        def __init__(self, data_manager):
            self.start(data_manager)

        def start(self, data_manager):
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
            speed = 1
            a_down = Animation(spriteSheet, [(i, 0) for i in range(6)], duration, speed, loop = True)
            a_right = Animation(spriteSheet, [(i, 1) for i in range(6)], duration, speed, loop = True)
            a_up = Animation(spriteSheet, [(i, 2) for i in range(6)], duration, speed, loop = True)
            a_left = Animation(spriteSheet, [(i, 3) for i in range(6)], duration, speed, loop = True)

            self.animator.add_animation('DOWN', a_down)
            self.animator.add_animation('RIGHT', a_right)
            self.animator.add_animation('UP', a_up)
            self.animator.add_animation('LEFT', a_left)

            self.animator.set_animation('DOWN')

        def update(self, dt):
            self.animator.update(dt)

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
    speed = 1

    fixed_bot = Player(data)
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
        events = event.get()
        for e in events:
            if e.type == KEYDOWN:
                if e.key == K_z:
                    player.animator.set_animation('UP')
                    player.animator.current_animation.set_speed(speed)
                    player.velocity = Vector(0.0, -1.0)
                elif e.key == K_s:
                    player.animator.set_animation('DOWN')
                    player.animator.current_animation.set_speed(speed)
                    player.velocity = Vector(0.0, 1.0)
                elif e.key == K_q:
                    player.animator.set_animation('LEFT')
                    player.animator.current_animation.set_speed(speed)
                    player.velocity = Vector(-1.0, 0.0)
                elif e.key == K_d:
                    player.animator.set_animation('RIGHT')
                    player.animator.current_animation.set_speed(speed)
                    player.velocity = Vector(1.0, 0.0)
                elif e.key == K_LSHIFT:
                    speed = 1.5
                    player.animator.current_animation.set_speed(speed)
                    player.speed *= player.speed_factor
            if e.type == KEYUP:
                if e.key == K_LSHIFT:
                    speed = 1
                    player.animator.current_animation.set_speed(speed)
                    player.speed /= player.speed_factor

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

            player.test_collision(fixed_bot.collider)
            print fixed_bot.collider.position

        # ===== Draw =====
        player.draw(screen)
        fixed_bot.draw(screen)

        player.collider.draw_debug(screen)
        fixed_bot.collider.draw_debug(screen)

        # ====================================================================
        display.flip()