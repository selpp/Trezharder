from monobehaviour import MonoBehaviour
from model_1 import DeepQModel
from game_engine import GameEngine
from bot import Bot
from reward_calculator import RewardCalculator
from game_engine import GameEngineTools

class BotBehaviour(MonoBehaviour):
	step = 0
	def start(self):
		self.model = GameEngineTools.instance.model
		self.model.load()
		self.bot = self.gameobject.get_mono(Bot)
		self.old_action = [0 for i in range(len(self.bot.action_vector))]
		self.rc = self.gameobject.get_mono(RewardCalculator)
		self.prev = None
		self.action_repeat = 16

	def update(self, dt):
		pass

	def fixed_update(self, fixed_update):
		GameEngineTools.pause()
		GameEngineTools.update_current_screen_ai()
		curr = GameEngineTools.get_current_screen_ai()
		if BotBehaviour.step % self.action_repeat == 0:
			self.bot.action_vector = self.model.choose_action(curr, is_loaded = True)
		'''if self.prev is not None:
			self.model.store_transition(self.prev, self.old_action.index(1), self.rc.r, curr)
			if BotBehaviour.step > self.model.memory_size:
				self.model.learn()'''
		self.print_action(self.bot.action_vector)
		'''print('reward: ' + str(self.rc.r))
		print('epsilon: ' + str(self.model.e_greedy))
		print('step: ' + str(BotBehaviour.step))
		print('full: ' + str((self.model.memory_counter >= self.model.memory_size)))'''
		print('\n')
		self.old_action = self.bot.action_vector
		self.prev = curr
		GameEngineTools.restart()
		BotBehaviour.step += 1

	def draw(self, screen):
		pass

	def draw_ai(self, screen):
		pass
	
	def z_buff(self, z_index, z_buffer):
		pass

	def print_action(self, action):
		plain = u'\u2588'
		block = u'\u2591'

		left = plain if action[0] == 1 else block
		right = plain if action[1] == 1 else block
		up = plain if action[2] == 1 else block
		down = plain if action[3] == 1 else block
		shift = plain if action[4] == 1 else block
		explode = plain if action[5] == 1 else block

		print('')
		print('    ' + up)
		print('  ' + left + '   ' + right + '  ' + shift  + ' ' + explode)
		print('    ' + down)
		print('')