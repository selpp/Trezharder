import numpy as np
import engine.deep_learning.config as conf

from copy import deepcopy
from engine.core.inputs.player_command import BotPlayerCommand
from engine.core.game_engine import GameEngineTools
from engine.core.inputs.input_manager import InputManager
from engine.core.data_manager import DataManager

class ImageBuffer(object):
    def __init__(self, size, full = False):
        self.size = size * len(DataManager.get_instance().feature_maps)
        self.buffer = []
        self.full = full

    def append(self, image):
        if len(self.buffer) < self.size:
            self.buffer.append(image)
        else:
            if not self.full:
                self.full = True
            for i in range(self.size - 1, 1, -1):
                self.buffer[i - 1] = self.buffer[i]
            self.buffer[-1] = image

    def get_frames(self):
        if not self.full:
            return None

        frames = np.zeros((conf.WIDTH, conf.HEIGHT, self.size))
        i = 0
        for feature_map in self.buffer:
            frames[:, :, i] = feature_map
            i += 1

        return frames

class DeepPlayerCommand(BotPlayerCommand):
    def __init__(self,reward_calculator):
        BotPlayerCommand.__init__(self)
        self.rc = reward_calculator
        self.old_action = [0 if i != 0 else 1 for i in range(len(self.cmd))]
        self.action_vector = None
        self.prev_frames = ImageBuffer(conf.IMAGE_BUFFER_SIZE)# None
        self.old_reward = None
        # self.has_played = False

    def get_current_frames(self):
        curr_frames = self.prev_frames
        for id, _ in DataManager.get_instance().feature_maps.iteritems():
            GameEngineTools.update_feature_map(id)
            feature_map = np.array(GameEngineTools.get_current_feature_map(id))
            curr_frames.append(feature_map)

        return curr_frames

    def get_action(self, curr_frames):
        if GameEngineTools.instance.model.global_step % conf.UPDATE_FREQUENCY == 0 and self.prev_frames.full:
            action_index = GameEngineTools.instance.model.choose_action(curr_frames.get_frames())
            action_vector = [0 if i != action_index else 1 for i in range(conf.ACTIONS)]
        else:
            action_vector = self.old_action
        return action_vector

    def get_reward(self):
        reward = self.rc.r
        preprocessed_reward = GameEngineTools.instance.model.preprocess_reward(reward)
        GameEngineTools.instance.model.total_reward += preprocessed_reward
        if reward > 0:
            GameEngineTools.instance.model.score += preprocessed_reward
        GameEngineTools.instance.model.actual_reward = preprocessed_reward
        return preprocessed_reward

    def store_and_train(self, curr_frames):
        if self.prev_frames.full:
            GameEngineTools.instance.model.store(self.prev_frames.get_frames(), self.old_action.index(1), self.old_reward, curr_frames.get_frames())
            GameEngineTools.instance.model.training_step()

    def get_new_command(self):
        GameEngineTools.pause()

        # Get current frames
        curr_frames = self.get_current_frames()

        # Choose action
        self.action_vector = self.get_action(curr_frames)
        self.vector_to_command(self.action_vector)

        # Observe reward
        reward = self.get_reward()

        # Store Experience and Train
        self.store_and_train(curr_frames)

        # Update Values
        self.old_action = self.action_vector
        self.old_reward = reward
        self.prev_frames = deepcopy(curr_frames)
        # self.has_played = True

        GameEngineTools.restart()

        # Debug
        self.print_console_infos()

    def print_console_infos(self):
        print('==================== AI ======================')
        self.print_action()
        self.print_model_data()
        print('==============================================\n')

    def print_model_data(self):
        plain = u'\u2588'
        block = u'\u2591'

        full = plain if len(GameEngineTools.instance.model.memory) >= conf.MEMORY_SIZE else block

        print('Step: ' + str(GameEngineTools.instance.model.global_step))
        print('Episode: ' + str(GameEngineTools.instance.model.episode))
        print('Reward: ' + str(self.rc.r))
        print('TotalReward: ' + str(GameEngineTools.instance.model.total_reward))
        print('Score: ' + str(GameEngineTools.instance.model.score))
        print('Memory size: ' + str(len(GameEngineTools.instance.model.memory)))
        print('Memory full: ' + full)
        #print('Double_Q: ' + str(conf.Q_CHEAT))

    def print_action(self):
        plain = u'\u2588'
        block = u'\u2591'

        left = plain if self.left else block
        right = plain if self.right == 1 else block
        up = plain if self.up == 1 else block
        down = plain if self.down == 1 else block
        shift = plain if self.A == 1 else block
        explode = plain if self.B == 1 else block
        ai = plain if GameEngineTools.instance.model.is_ai else block

        print('')
        print('    ' + up)
        print('  ' + left + '   ' + right + '  ' + shift  + ' ' + explode)
        print('    ' + down)
        print('')
        print('AI action: ' + ai)
