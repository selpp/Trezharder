from monobehaviour import MonoBehaviour
from bot import Bot

class RewardCalculator(MonoBehaviour):
	def start(self):
		self.r = 0
		self.reward_end = False

	def update(self, dt):
		pass

	def fixed_update(self, fixed_dt):
		self.r = 0
		if self.reward_end:
		    return
		if self.gameobject.get_mono(Bot).explode:
			self.r = 1
			self.reward_end = True

	def draw():
		pass
    
	def z_buff(self, z_index, z_buffer):
         pass