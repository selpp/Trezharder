import numpy as np

from player_command import BotPlayerCommand
from game_engine import GameEngineTools
from input_manager import InputManager
from data_manager import DataManager
from double_dueling_deep_q_learning import MEMORY_SIZE, ACTIONS, WIDTH, HEIGHT, UPDATE_FREQUENCY

class DeepPlayerCommand(BotPlayerCommand):
    def __init__(self,reward_calculator):
        BotPlayerCommand.__init__(self)
        self.rc = reward_calculator
        self.model = GameEngineTools.instance.model
        self.old_action = [0 if i != 0 else 1 for i in range(len(self.cmd))]
        self.prev = None
        self.action_vector = None
        self.has_played = False

    def get_new_command(self):
        GameEngineTools.pause()

        channels = len(DataManager.get_instance().feature_maps)
        curr = np.zeros((WIDTH, HEIGHT, channels))
        i = 0
        for id, _ in DataManager.get_instance().feature_maps.iteritems():
            GameEngineTools.update_feature_map(id)
            feature_map = np.array(GameEngineTools.get_current_feature_map(id))
            curr[:, :, i] = feature_map
            i += 1
        curr = np.array(curr)


        if self.model.global_step % UPDATE_FREQUENCY == 0:
            action_index = self.model.choose_action(curr)
            self.action_vector = [0 if i != action_index else 1 for i in range(ACTIONS)]
        else:
            self.action_vector = self.old_action
        self.vector_to_command(self.action_vector)
        if self.has_played:
            self.model.store(self.prev, self.old_action.index(1), self.rc.r, curr)
        self.model.training_step()

        print('==================== AI ======================')
        self.print_action()
        self.print_model_data()
        print('==============================================\n')

        self.old_action = self.action_vector
        self.prev = curr
        self.has_played = True

        GameEngineTools.restart()

    def print_model_data(self):
        plain = u'\u2588'
        block = u'\u2591'

        full = plain if self.model.memory.buffer_size >= MEMORY_SIZE else block

        print('Reward: ' + str(self.rc.r))
        print('Epsilon: ' + str(self.model.e))
        print('Step: ' + str(self.model.global_step))
        print('Memory full: ' + full)

    def print_action(self):
        plain = u'\u2588'
        block = u'\u2591'

        left = plain if self.left else block
        right = plain if self.right == 1 else block
        up = plain if self.up == 1 else block
        down = plain if self.down == 1 else block
        shift = plain if self.A == 1 else block
        explode = plain if self.B == 1 else block
        ai = plain if self.model.is_ai else block

        print('')
        print('    ' + up)
        print('  ' + left + '   ' + right + '  ' + shift  + ' ' + explode)
        print('    ' + down)
        print('')
        print('AI action: ' + ai)
