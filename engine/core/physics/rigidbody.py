# -*- coding: utf-8 -*-
from engine.core.physics.physics_manager import PhysicsManager
from engine.core.maths.vector import Vector
from engine.core.monobehaviour import MonoBehaviour

class Rigidbody(MonoBehaviour):
    def __init__(self):
        self.transform = None
        self.gameobject = None
        self.collider = None
        self.triggers = []
        self.force = Vector(0.0,0.0)
        self.velocity = Vector(0.0,0.0)
        self.acceleration = Vector(0.0,0.0)
        self.last_movement = Vector(0.0,0.0)

    def start(self):
        pass

    def add_force(self,force):
        self.force += force

    def set_velocity(self,new_velocity):
        self.velocity = new_velocity

    def update(self,delta_time):
        pass

    def add_triggers(self,triggers):
        for trigger in self.triggers:
            self.triggers.append(trigger)

    def set_collider(self,collider):
        self.collider = collider

    def fixed_update(self,delta_time):
        movement = self.velocity * delta_time
        if movement.magnitude() > 0.0001:
            self.transform.move(movement)
            self.last_movement = movement
            if self.collider is not None:
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
        self.transform.move(Vector(-self.last_movement.x , 0.0))
        if self.collider.try_collision(other_collider):
            self.transform.move(Vector(self.last_movement.x , -self.last_movement.y))
            if self.collider.try_collision(other_collider):
                self.transform.move(Vector(-self.last_movement.x , 0.0))
        self.gameobject.on_collision(other_collider)


    def get_collider(self):
        return self.collider

    def get_triggers(self):
        return self.triggers

    def draw(self,screen):
        pass
