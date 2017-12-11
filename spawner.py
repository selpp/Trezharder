from abc import ABCMeta, abstractmethod

class Spawner:
	__metaclass__ = ABCMeta
	def __init__(self,n,map):
		self.spawn(n,map)

	@abstractmethod
	def spawn(self,n,map):
		pass

