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

# ===================================================
# EXAMPLE: Player movement without state machine just for testing purpose

if __name__ == '__main__':
	from time import clock

	class Player(MonoBehaviour):
		def __init__(self):
			self.start()
			self.timer = 0

		def start(self):
			self.x = 0
			self.y = 0
			self.vel_x = 0
			self.vel_y = 0

		def update(self, dt):
			self.timer += dt
			self.vel_x, self.vel_y = 1, 1

		def fixed_update(self, fixed_dt):
			self.x += self.vel_x * fixed_dt
			self.y += self.vel_y * fixed_dt

		def draw(self):
			print '(' + str(self.x) + ', ' + str(self.y) + ')'

	current_time = clock()
	dt = 0

	current_fixed_time = clock()
	fixed_dt = 0

	player = Player()

	while True:
		dt = clock() - current_time
		current_time += dt

		player.update(dt)

		if (current_time / 0.2) - int(current_time / 0.2) > 0:
			fixed_dt = clock() - current_fixed_time
			current_fixed_time += fixed_dt

			player.fixed_update(fixed_dt)

		player.draw()
