# Input Manager
from pygame import KEYDOWN, KEYUP, K_z, K_q, K_s, K_d, K_SPACE, K_LSHIFT

# ===================================================
# INPUTMANAGER

class InputManager(object):
	def __init__(self):
		self.key_booleans = {
			'UP': [False, K_z], 
			'DOWN': [False, K_s], 
			'LEFT': [False, K_q], 
			'RIGHT': [False, K_d],
			'FIRE1': [False, K_SPACE],
			'LSHIFT': [False, K_LSHIFT]
		}

		self.events = None
	
	instance = None

	@staticmethod
	def get_instance():
		if InputManager.instance is None:
			InputManager.instance = InputManager()
		return InputManager.instance

	def is_key_pressed(self, key):
		if key in self.key_booleans:
			return self.key_booleans[key][0]
		return False

	def is_key_down(self, key):
		if key in self.key_booleans:
			for e in self.events:
				if e.type == KEYDOWN:
					if e.key == self.key_booleans[key][1]:
						return True
		return False

	def is_key_up(self, key):
		if key in self.key_booleans:
			for e in self.events:
				if e.type == KEYUP:
					if e.key == self.key_booleans[key][1]:
						return True
		return False

	def update(self, events):
		self.events = events

		for e in events:
			if e.type == KEYDOWN:
				for key, value in self.key_booleans.iteritems():
					if e.key == value[1]:
						self.key_booleans[key][0] = True
			if e.type == KEYUP:
				for key, value in self.key_booleans.iteritems():
					if e.key == value[1]:
						self.key_booleans[key][0] = False