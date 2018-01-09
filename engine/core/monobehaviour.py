# Mono Behaviour
from abc import ABCMeta, abstractmethod
# ===================================================
# MONOBEHAVIOUR

class MonoBehaviour(object):
	__metaclass__ = ABCMeta
     
	def __init__(self,z_index=0):
         self.gameobject = None 
         self.z_index = z_index
         
	def bind_gameobject(self,gameobject):
         self.gameobject = gameobject
         self.transform = gameobject.transform
         
	@abstractmethod
	def start(self):
		pass

	def update(self, dt):
		pass

	def fixed_update(self, fixed_dt):
		pass

	def draw():
		pass

	def draw_ai():
		pass

	def on_collision(self,collider):
	    pass

	def z_buff(self, z_index, z_buffer):
		pass