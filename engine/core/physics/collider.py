# -*- coding: utf-8 -*-
from abc import ABCMeta , abstractmethod
from engine.core.maths.vector import Vector
from engine.core.physics.physics_manager import PhysicsManager
from engine.tools.debug_drawings import DebugDrawings

class Collider:
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self,parent_transform,position,gameobject,is_trigger = False):
        self.position = position
        self.parent_transform = parent_transform
        self.is_trigger = is_trigger
        self.is_on_collision = False
        self.gameobject = gameobject
        PhysicsManager.get_instance().add_collider(self)


    def get_tag(self):
        return self.parent_transform.tag

    '''
    def on_collision(self):
        self.gameobject.on_collision
    '''

    def is_trigger_activate(self):
        return self.is_trigger

    def set_on_collision(self,state):
        self.is_on_collision = state

    @abstractmethod
    def try_collision(self,collider):
        pass

    @abstractmethod
    def draw_debug(self):
        pass

class BoxCollider(Collider):
    def __init__(self,parent_transform,position,scale,gameobject,is_trigger = False):
        Collider.__init__(self,parent_transform,position,gameobject,is_trigger)
        self.scale = scale

    def try_collision(self,collider):
        if isinstance(collider,BoxCollider):
            return self.collision_with_box(collider)
        if isinstance(collider,CircleCollider):
            return self.collision_with_circle(collider)
        return False

    def collision_with_box(self,box):
        x,y,w,h = self.get_world_box()
        x2,y2,w2,h2 = box.get_world_box()
        left_one , right_one = ((x2,y2,w2,h2) , (x,y,w,h)) if x2 < x else ((x,y,w,h) , (x2,y2,w2,h2))
        down_one , up_one = ((x2,y2,w2,h2) , (x,y,w,h)) if y2 < y else ((x,y,w,h) , (x2,y2,w2,h2))
        if left_one[0] + left_one[2] > right_one[0] - right_one[2]:
            if down_one[1] + down_one[3] > up_one[1] - up_one[3]:
                return True
        return False

    def collision_with_circle(self,circle):
        xb,yb,w,h = self.get_world_box()
        xc,yc,r = circle.get_world_circle()

        box_proj = Vector(min(max(xc , xb - w),xb + w),min(max(yc , yb - h),yb + h))
        return (box_proj - Vector(xc,yc)).magnitude() < r

    def get_world_box(self):
        x = self.position.x + self.parent_transform.get_position().x
        y = self.position.y + self.parent_transform.get_position().y
        w = self.scale.x * self.parent_transform.get_scale().x / 2.0
        h = self.scale.y * self.parent_transform.get_scale().y / 2.0

        return x,y,w,h

    def draw_debug(self, screen):
        x, y, w, h = self.get_world_box()
        DebugDrawings.draw_rect(screen, Vector(x, y), w * 2, h * 2, (0, 255, 0))

class CircleCollider(Collider):
    def __init__(self,parent_transform,position,radius,gameobject,is_trigger = False):
        Collider.__init__(self,parent_transform,position,gameobject,is_trigger)
        self.radius = radius

    def try_collision(self,collider):
        if isinstance(collider,CircleCollider):
            return self.collision_with_circle(collider)
        if isinstance(collider,BoxCollider):
            return self.collision_with_box(collider)
        return False

    def collision_with_circle(self,circle):
        x , y , r = self.get_world_circle()
        x2 , y2 , r2 = circle.get_world_circle()
        return Vector(x - x2,y - y2).magnitude() < r + r2

    def collision_with_box(self,box):
        return box.collision_with_circle(self)

    def get_world_circle(self):
        x = self.position.x + self.parent_transform.get_position().x
        y = self.position.y + self.parent_transform.get_position().y
        r = self.radius * max(self.parent_transform.get_scale().x,self.parent_transform.get_scale().y)

        return x,y,r

    def draw_debug(self,screen):
        x , y , r = self.get_world_circle()
        DebugDrawings.draw_circle(screen,Vector(int(x),int(y)),int(r),(0,255,0))
