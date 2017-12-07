from mono_behaviour import MonoBehaviour
from model_1 import DeepQModel
from game_engine import GameEngine
from bot import Bot

class BotBehaviour(MonoBehaviour):
    def start(self):
        self.r = 0
        self.model =  DeepQModel(width = 800, height = 600)
        self.bot = self.gameobject.get_mono(Bot)
        self.old_action = [0 for i in range(len(self.bot.action_vector))]

    def update(self, dt):
        pass

    def fixed_update(self, fixed_update):
        prev = GameEngine.previous_frame
        curr = GameEngine.current_frame
        self.bot.action_vector = self.model.choose_action(prev)
        self.model.store_transition(prev, self.old_action, self.r, curr)
        self.old_action = self.bot.action_vector
        self.model.learn()

    def draw(self, screen):
        pass