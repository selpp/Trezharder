from abc import ABCMeta, abstractmethod

class Spawner:
    __metaclass__ = ABCMeta
    def __init__(self):
        pass

    @abstractmethod
    def spawn(self,spawn_number,map):
        pass

    
                
