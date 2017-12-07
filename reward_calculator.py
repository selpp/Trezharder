from mono_behaviour import MonoBehaviour
from bot import Bot

class RewardCalculator(MonoBehaviour):
	def start(self):
		self.r = 0

	def update(self, dt):
		pass

	def fixed_update(self, fixed_dt):
		if self.gameobject.get_mono(Bot).explode:
			self.r = 1
		self.r = 0

	def draw():
		pass