from reward import Reward
from player import Player

class RewardCoward(Reward):
	def start(self):
		self.r = 0
		self.reward_end = False
		self.collision = False
		self.dist = 150.0
		self.player = self.gameobject.get_mono(Player)

	def update(self, dt):
		pass

	def fixed_update(self, fixed_dt):
		self.r = 0
		if self.reward_end:
			return
		if self.player.rip:
			self.r = -1
			self.reward_end = True
		else:
			for ennemy in self.player.ennemies:
				if ennemy is None or ennemy is self.gameobject or not ennemy.is_alive:
					continue
				dist = (self.transform.get_position() - ennemy.transform.get_position()).magnitude()
				self.r += -0.1 if dist < self.dist else 0.1 

		if self.player.command.B and not self.player.murderer:
			self.r = -0.1
		if self.player.command.A:
			self.r = -0.1


	def z_buff(self, z_index, z_buffer):
		 pass
