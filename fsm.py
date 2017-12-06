# Finite State Machine
from abc import ABCMeta, abstractmethod

# ===================================================
# STATE

class State(object):
	__metaclass__ = ABCMeta

	def __init__(self):
		self.does_exit = False
		self.timer = 0
		self.enter()

	def enter(self):
		pass

	def update(self, dt):
		self.timer += dt
		pass

	def exit(self):
		pass

	def __str__(self):
		return 'State: Base Class'

# ===================================================
# FSM

class FSM(object):
	__metaclass__ = ABCMeta

	def __init__(self):
		self.state = None

	def update(self, dt):
		if self.state.does_exit:
			self.state = self.state.exit()
		else:
			self.state.update(dt)