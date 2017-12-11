from player_command import BotPlayerCommand
from game_engine import GameEngineTools

class DeepPlayerCommand(BotPlayerCommand):
    step = 0
    def __init__(self,reward_calculator):
        BotPlayerCommand.__init__(self)
        self.rc = reward_calculator
        self.model = GameEngineTools.instance.model
        #self.model.load()
        self.old_action = [0 for i in range(len(self.cmd))]
        self.prev = None
        self.action_repeat = 16
        self.action_vector = None
        self.has_played = False

    def get_new_command(self):
        GameEngineTools.pause()
        GameEngineTools.update_current_screen_ai()
        curr = GameEngineTools.get_current_screen_ai()

        if DeepPlayerCommand.step % self.action_repeat == 0 or not self.has_played:
            self.action_vector = self.model.choose_action(curr, is_loaded = False)
            self.vector_to_command(self.action_vector)
        if self.has_played:
            self.model.store_transition(self.prev, self.old_action.index(1), self.rc.r, curr)
            if DeepPlayerCommand.step > self.model.memory_size:
                self.model.learn()
            
        self.print_action()
        self.print_model_data()
        self.old_action = self.action_vector
        self.prev = curr
        self.has_played = True
        GameEngineTools.restart()
        DeepPlayerCommand.step += 1

    def print_model_data(self):
        print('reward: ' + str(self.rc.r))
        print('epsilon: ' + str(self.model.e_greedy))
        print('step: ' + str(DeepPlayerCommand.step))
        print('full: ' + str((self.model.memory_counter >= self.model.memory_size)))
        print('\n')

    def print_action(self):
        plain = u'\u2588'
        block = u'\u2591'

        left = plain if self.left else block
        right = plain if self.right == 1 else block
        up = plain if self.up == 1 else block
        down = plain if self.down == 1 else block
        shift = plain if self.A == 1 else block
        explode = plain if self.B == 1 else block

        print('')
        print('    ' + up)
        print('  ' + left + '   ' + right + '  ' + shift  + ' ' + explode)
        print('    ' + down)
        print('')