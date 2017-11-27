# -*- coding: utf-8 -*-
from Queue import Queue

class PhysicsManager(object):
    
    def __init__(self):
        self.colliders = []
        self.moved_rigidbody = Queue()
        
    instance = None
        
    @staticmethod
    def get_instance():
        if not PhysicsManager.instance:
            PhysicsManager.instance = PhysicsManager()
        return PhysicsManager.instance

    def add_collider(self,collider):
        self.colliders.append(collider)
        
    def add_moved_rigidbody(self,rigidbody):
        self.moved_rigidbody.put(rigidbody)
        
    def update_collision(self):
        #print('in')
        #print(self.moved_rigidbody.empty())
        while not self.moved_rigidbody.empty():
            rb = self.moved_rigidbody.get()
            this_collider = rb.get_collider()
            for collider in self.colliders:
                if collider != this_collider and this_collider.try_collision(collider):
                    rb.cancel_movement(collider)