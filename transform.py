# -*- coding: utf-8 -*-
from vector import Vector
from loging import debug

class Transform:
    '''
    Class Summary
    
    Attributes :
        local_position : A Vector representing the position
        local_euler_angle : A float representing the angle
        local_scale : A Vector representing the scale
        parent : A Transform representing the parent Transform useful to compute the world coord
    '''
    
    def __init__(self,local_position,local_euler_angle,local_scale,parent=None):
        self.local_position = local_position
        self.local_euler_angle = local_euler_angle
        self.local_scale = local_scale
        self.parent = parent
        self.got_updated = False
        self.update_global_state()
        debug('WARNING : TRANSFORM GLOBAL STATE HAVEN\'T BEEN DEVELOP YET #NOFEATURE !!!',3)
        debug('PARENT SHOULD ALWAYS BE NONE',3)
        
    def update_global_state(self):
        if self.got_updated:
            return
        if self.parent is not None:
            self.parent.update_local_state()
        self.position = self.local_position
        self.euler_angle = self.local_euler_angle
        self.scale = self.local_scale
        self.got_updated = True
    
    def move(self,movement):
        self.local_position += movement
        self.got_updated = False
        
    def rotate(self,angle):
        self.local_euler_angle += angle
        self.local_euler_angle %= 360.0
        self.got_updated = False
        
    def get_position(self):
        self.update_global_state()
        return self.position
        
    def get_euler_angle(self):
        self.update_global_state()
        return self.euler_angle
        
    def get_scale(self):
        self.update_global_state()
        return self.scale
    
    def __str__(self):
        self.update_global_state()
        string = 'Position : ' + str(self.position)
        string += '\nAngle : ' + str(self.euler_angle)
        string += '\nScale : ' + str(self.scale)
        return string

if __name__ == '__main__':
    t = Transform(Vector(10,5),0.0,Vector(5,3))
    print(t)
    t.move(Vector(3,4))
    t.rotate(-10.0)
    print(t)
