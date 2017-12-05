# -*- coding: utf-8 -*-
from Queue import Queue

class PhysicsManager(object):
    
    def __init__(self):
        self.colliders = []
        self.moved_rigidbody = Queue()
        self.trigger_collision = []
        self.non_collide_tag = {'player' : ['player']}
        
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
        while not self.moved_rigidbody.empty():
            rb = self.moved_rigidbody.get()
            these_colliders = rb.get_triggers()[:]
            these_colliders.append(rb.get_collider())
            for this_collider in these_colliders:
                for collider in self.colliders:
                    if collider != this_collider and this_collider.try_collision(collider):
                        if collider.is_trigger_activate() or this_collider.is_trigger_activate():
                                self.add_trigger(this_collider,collider)
                        else:
                            if collider.get_transform().tag in self.non_collide_tag:
                                if this_collider.get_transform().tag in self.non_collide_tag[collider.get_transform().tag]:
                                    continue
                            rb.cancel_movement(collider)
                            
        self.trigger_update()
                        
    def trigger_update(self):
        for current_collision in self.trigger_collision:
            if not current_collision[0].try_collision(current_collision[1]):
                self.trigger_collision.remove(current_collision)
                current_collision[0].set_on_collision(False)
                current_collision[1].set_on_collision(False)
    
    def add_trigger(self,collider1,collider2):
        for current_collision in self.trigger_collision:
            if ((collider1 in current_collision) and (collider2 in current_collision)):
                return
        self.trigger_collision.append([collider1,collider2])
        collider1.set_on_collision(True)
        collider2.set_on_collision(True)