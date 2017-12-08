from abc import ABCMeta, abstractmethod
from input_manager import InputManager
import random as rnd


class PlayerCommand(object):
    __metaclass__ = ABCMeta
     
    def __init__(self):
        self.prev_left = False
        self.prev_right = False
        self.prev_down = False
        self.prev_up = False
        self.prev_A = False
        self.prev_B = False
        
        self.left = False
        self.right = False
        self.down = False
        self.up = False
        self.A = False
        self.B = False
          
    def update_command(self):
        self.prev_left = self.left
        self.prev_right = self.right
        self.prev_up = self.up
        self.prev_down = self.up
        self.prev_A = self.A
        self.prev_B = self.B
        self.get_new_command()
        
    @abstractmethod    
    def get_new_command(self):
        pass
        
    
class HumanPlayerCommand(PlayerCommand):
    def __init__(self):
        PlayerCommand.__init__(self)
        self.input_manager = InputManager.get_instance()
        
    def get_new_command(self):
        self.up = self.input_manager.is_key_pressed('UP')
        self.down = self.input_manager.is_key_pressed('DOWN')
        self.left = self.input_manager.is_key_pressed('LEFT')
        self.right = self.input_manager.is_key_pressed('RIGHT')
        
class BotPlayerCommand(PlayerCommand):
    __metaclass__ = ABCMeta
    
    def __init__(self):
        PlayerCommand.__init__(self)
        
    @abstractmethod
    def get_new_command(self):
        pass
                  
    def vector_to_command(self,vector):
        self.up = vector[0]
        self.down = vector[1]
        self.left = vector[2]
        self.right = vector[3]
        self.A = vector[4]
        self.B = vector[5]
    
class RandomPlayerCommand(PlayerCommand):
    def __init__(self):
        PlayerCommand.__init__(self)
        
    def get_new_command(self):
        vector = [rnd.randint(0,1) for i in range(5)]
        self.vector_to_command(vector)