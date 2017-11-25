# -*- coding: utf-8 -*-
from abc import ABCMeta , abstractmethod
from transform import Transform
from Vector import Vector

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

if __name__ == '__main__':
    t1 = Transform(Vector(0.0,0.0),0.0,Vector(1.0,1.0))
    t2 = Transform(Vector(1.0,1.0),0.0,Vector(1.0,1.0))
    b1 = BoxCollider(None,t1,Vector(0.0,0.0),Vector(1,1))
    b2 = BoxCollider(None,t2,Vector(0.0,0.0),Vector(0.99999,0.99999))
    b3 = BoxCollider(None,t2,Vector(0.0,0.0),Vector(1.000001,1.0000001))
    print(b1.try_collision(b2))
    print(b1.try_collision(b3))
    print(b2.try_collision(b3))