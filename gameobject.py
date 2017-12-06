# -*- coding: utf-8 -*-
from vector import Vector
from transform import Transform

class Gameobject(object):
    def __init__(self,rigidbody=None,monobehaviours=[],tag=''):
        self.is_active = True
        self.transform = Transform(Vector(0,0),0.0,Vector(1.0,1.0),tag=tag)
        self.rigidbody = rigidbody
        self.monobehaviours = []
        if self.rigidbody is not None:
            self.rigidbody.bind_gameobject(self)
        #self.transform.gameobject = self
        self.new_monobehaviours = monobehaviours
            
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
            
    def start(self):
        for mono in self.monobehaviours:
            mono.start()
        
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
            new_mono.start()
            self.monobehaviours.append(new_mono)
            
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
    