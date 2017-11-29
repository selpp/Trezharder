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

# ===================================================
# EXAMPLE: Swtich using FSM

if __name__ == '__main__':
	from time import clock

	class SwitchOn(State):
		def __init__(self):
			State.__init__(self)

		def enter(self):
			print 'I Enter ' + str(self)

		def update(self, dt):
			State.update(self, dt)
			if self.timer > 5:
				self.does_exit = True

		def exit(self):
			print 'I Exit ' + str(self)
			return SwitchOff()

		def __str__(self):
			return 'State: Switch On'

	class SwitchOff(State):
		def __init__(self):
			State.__init__(self)

		def enter(self):
			print 'I Enter ' + str(self)

		def update(self, dt):
			State.update(self, dt)
			if self.timer > 2:
				self.does_exit = True

		def exit(self):
			print 'I Exit ' + str(self)
			return SwitchOn()

		def __str__(self):
			return 'State: Switch Off'

	class SwitchFSM(FSM):
		def __init__(self):
			FSM.__init__(self)

		def update(self, dt):
			FSM.update(self, dt)

	switch = SwitchFSM()
	switch.state = SwitchOff()

	current_time = clock()
	dt = 0

	while True:
		dt = clock() - current_time
		current_time += dt

		switch.update(dt)
