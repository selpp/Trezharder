from monobehaviour import MonoBehaviour
from model_1 import DeepQModel
from game_engine import GameEngine
from bot import Bot
from reward_calculator import RewardCalculator
from game_engine import GameEngineTools

class BotBehaviour(MonoBehaviour):
    def start(self):
        width, height = GameEngineTools.get_screen_size()
        self.model = GameEngineTools.instance.model
        self.bot = self.gameobject.get_mono(Bot)
        self.old_action = [0 for i in range(len(self.bot.action_vector))]
        self.rc = self.gameobject.get_mono(RewardCalculator)
        self.prev = None

    def update(self, dt):
        pass

    def fixed_update(self, fixed_update):
        GameEngineTools.pause()
        curr = GameEngineTools.screen_to_array()
        self.bot.action_vector = self.model.choose_action(curr)
        if self.prev is not None:
            self.model.store_transition(self.prev, self.old_action, self.rc.r, curr)
            self.model.learn()
        self.old_action = self.bot.action_vector
        self.prev = curr
        print('Action: ' + str(self.bot.action_vector) + ' ,Reward: ' + str(self.rc.r))
        GameEngineTools.restart()

    def draw(self, screen):
        pass
    
    def z_buff(self, z_index, z_buffer):
        pass