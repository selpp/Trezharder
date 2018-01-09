# -*- coding: utf-8 -*-
from vector import Vector
from transform import Transform

class Gameobject(object):
    def __init__(self,name='',rigidbody=None,tag=''):
        self.is_active = True
        self.is_alive = True
        self.name = name
        self.transform = Transform(Vector(0,0),0.0,Vector(1.0,1.0),tag=tag)
        self.rigidbody = rigidbody
        self.monobehaviours = []
        self.new_monobehaviours = []
        if self.rigidbody is not None:
            self.rigidbody.bind_gameobject(self)
        self.transform.gameobject = self
            
    def set_triggers(self,triggers):
        if self.rigidbody is None:
            if self.transform.parent is not None:
                self.transform.parent.gameobject.set_colliders(triggers)
        else:
            self.rigidbody.add_triggers(triggers)
        
    def add_mono(self,monobehaviours):
        for mono in monobehaviours:
            mono.bind_gameobject(self)
            self.new_monobehaviours.append(mono)
        
    def get_mono(self,type_mono):
        for mono in (self.monobehaviours + self.new_monobehaviours):
            if isinstance(mono,type_mono):
                return mono
        return None
        
    def pop_mono(self,mono):
        self.monobehaviours.remove(mono)

    def update(self,dt):
        if not self.is_active:
            return
        for mono in self.monobehaviours:
            mono.update(dt)
    
    def fixed_update(self,fdt):
        if not self.is_active:
            return
        for mono in self.monobehaviours:
            mono.fixed_update(fdt)
            
        if self.rigidbody is not None:
            self.rigidbody.fixed_update(fdt)
            
        while len(self.new_monobehaviours) > 0:
            new_mono = self.new_monobehaviours.pop()
            self.monobehaviours.append(new_mono)
            new_mono.start()
            
    def on_collision(self,collider):
        for mono in self.monobehaviours:
            mono.on_collision(collider)
            
    def set_child(self,gameobject):
        gameobject.transform.parent = self.transform
        
    def z_buff(self,z_buff):
        for mono in self.monobehaviours:
            mono.z_buff(mono.z_index,z_buff)
    
    def draw(self,screen):
        if not self.is_active:
            return
        for mono in self.monobehaviours:
            mono.draw(screen)
    