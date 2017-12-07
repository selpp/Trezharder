# Mono Behaviour
from abc import ABCMeta, abstractmethod
# ===================================================
# MONOBEHAVIOUR

class MonoBehaviour(object):
	__metaclass__ = ABCMeta
     
	def __init__(self,z_index=0):
         self.z_index = z_index
         
	def bind_gameobject(self,gameobject):
         self.gameobject = gameobject
         self.transform = gameobject.transform
         
	@abstractmethod
	def start(self):
		pass

	@abstractmethod
	def update(self, dt):
		pass

	@abstractmethod
	def fixed_update(self, fixed_dt):
		pass

	@abstractmethod
	def draw():
		pass