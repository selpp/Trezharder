# -*- coding: utf-8 -*-
from physics_manager import PhysicsManager
from vector import Vector

class Rigidbody:
    def __init__(self,transform,collider):
        self.transform = transform
        self.collider = collider
        self.force = Vector(0.0,0.0)
        self.velocity = Vector(0.0,0.0)
        self.acceleration = Vector(0.0,0.0)
        self.last_movement = Vector(0.0,0.0)
        
    def add_force(self,force):
        self.force += force
        
    def set_velocity(self,new_velocity):
        self.velocity = new_velocity
        
    def update(self,delta_time):
        movement = self.velocity * delta_time
        if movement.magnitude() > 0.0001:
            self.transform.move(movement)
            self.last_movement = movement
            PhysicsManager.get_instance().add_moved_rigidbody(self)
        '''
        last_acceleration = self.acceleration
        movement = velocity * delta_time + (last_acceleration  * 0.5 * delta_time * delta_time)
        self.transform.move(movement)
        self.acceleration *= gamma #
        avg_acceleration = ( last_acceleration + new_acceleration ) / 2
        velocity += avg_acceleration * time_step
        '''
            
    def cancel_movement(self,other_collider):
        self.transform.move(self.last_movement * -1)
        
    def get_collider(self):
        return self.collider
        