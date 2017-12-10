from monobehaviour import MonoBehaviour
from bot import Bot

class RewardCalculator(MonoBehaviour):
    def start(self):
        self.r = 0
        self.reward_end = False
        self.collision = False
        self.dist = 300.0

    def update(self, dt):
        pass

    def fixed_update(self, fixed_dt):
        if self.reward_end:
            return
        bot = self.gameobject.get_mono(Bot)
        if bot.explode:
            self.r = 1
            self.reward_end = True
        else:
            for ennemy in bot.ennemies:
                if ennemy is None or ennemy is self.gameobject or not ennemy.is_alive:
                    continue
            dist = (self.transform.get_position() - ennemy.transform.get_position()).magnitude()
            self.r = -0.01 if dist > self.dist else (1 - (dist / self.dist)) / 5.0
            if self.collision:
                self.r = -0.1
                self.collision = False 

        if bot.action_vector[-2] == 1:
            self.r = -0.1

    def on_collision(self,collider):
        self.collision = True

    def draw():
        pass
    
    def z_buff(self, z_index, z_buffer):
         pass