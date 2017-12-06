# Mono Behaviour
from abc import ABCMeta, abstractmethod
from transform import Transform
from vector import Vector
# ===================================================
# MONOBEHAVIOUR

class MonoBehaviour(object):
	__metaclass__ = ABCMeta
     
	def __init__(self,z_index=0):
         self.z_index = z_index
         self.transform = Transform(Vector(0.0, 0.0), 0.0, Vector(1, 1))
         
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