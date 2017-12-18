from reward import Reward
from player import Player

class RewardLoot(Reward):
	def start(self):
		self.r = 0
		self.reward_end = False
		self.collision = False
		self.player = self.gameobject.get_mono(Player)

	def update(self, dt):
		pass

	def fixed_update(self, fixed_dt):
		self.r = -0.1
		if self.reward_end:
			return

		if self.player.murderer:
			self.r = 1
			self.reward_end = True
		elif self.collision:
			self.r = -1
			self.collision = False
			return

		if self.player.command.A == 1:
			self.r = -0.4

	def on_collision(self,collider):
		self.collision = True

	def draw():
		pass

	def z_buff(self, z_index, z_buffer):
		 pass
