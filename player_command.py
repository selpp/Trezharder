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
    
    def just_pressed(self,prev,curr):
        return not prev and curr
    
    def just_released(self,prev,curr):
        return prev and not curr
        
    
class HumanPlayerCommand(PlayerCommand):
    def __init__(self):
        PlayerCommand.__init__(self)
        self.input_manager = InputManager.get_instance()
        
    def get_new_command(self):
        self.up = self.input_manager.is_key_pressed('UP')
        self.down = self.input_manager.is_key_pressed('DOWN')
        self.left = self.input_manager.is_key_pressed('LEFT')
        self.right = self.input_manager.is_key_pressed('RIGHT')
        self.B = self.input_manager.is_key_pressed('FIRE1')
        self.A = self.input_manager.is_key_pressed('LSHIFT')
        
class BotPlayerCommand(PlayerCommand):
    __metaclass__ = ABCMeta
    
    def __init__(self):
        PlayerCommand.__init__(self)
        
    @abstractmethod
    def get_new_command(self):
        pass
                  
    def vector_to_command(self,vector):
        self.up = vector[0] == 1
        self.down = vector[1] == 1
        self.left = vector[2] == 1
        self.right = vector[3] == 1
        self.A = vector[4] == 1
        self.B = vector[5] == 1
    
class RandomPlayerCommand(BotPlayerCommand):
    def __init__(self):
        PlayerCommand.__init__(self)
        self.cmd = [rnd.randint(0,1) for i in range(6)]
        
    def get_new_command(self):
        if rnd.randint(0,20) > 18:
            self.cmd = [rnd.randint(0,1) for i in range(6)]
        self.vector_to_command(self.cmd)