from player_command import BotPlayerCommand
from game_engine import GameEngineTools
from input_manager import InputManager
from data_manager import DataManager

class DeepPlayerCommand(BotPlayerCommand):
    step = 0

    def __init__(self,reward_calculator):
        BotPlayerCommand.__init__(self)
        self.rc = reward_calculator
        self.model = GameEngineTools.instance.model
        #self.model.load()
        self.old_action = [0 for i in range(len(self.cmd))]
        self.prev = None
        self.action_repeat = 8
        self.action_vector = None
        self.has_played = False

    def get_new_command(self):
        GameEngineTools.pause()

        curr = None
        for id, _ in DataManager.get_instance().feature_maps.iteritems():
            GameEngineTools.update_feature_map(id)
            curr = GameEngineTools.get_current_feature_map(id)

        if DeepPlayerCommand.step % self.action_repeat == 0 or not self.has_played:
            self.action_vector = self.model.choose_action(curr, is_loaded = False)
            self.vector_to_command(self.action_vector)
        if self.has_played:
            self.model.store_transition(self.prev, self.old_action.index(1), self.rc.r, curr)
            if DeepPlayerCommand.step > self.model.memory_size:
                self.model.learn()

        print('==================== AI ======================')
        self.print_action()
        self.print_model_data()
        print('==============================================\n')

        self.old_action = self.action_vector
        self.prev = curr
        self.has_played = True

        GameEngineTools.restart()
        DeepPlayerCommand.step += 1

    def print_model_data(self):
        plain = u'\u2588'
        block = u'\u2591'

        full = plain if self.model.memory_counter >= self.model.memory_size else block

        print('Reward: ' + str(self.rc.r))
        print('Epsilon: ' + str(self.model.observable_e_greedy))
        print('Step: ' + str(DeepPlayerCommand.step))
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
