import tensorflow as tf
import tensorflow.contrib.slim as slim
import numpy as np
import random
import matplotlib.pyplot as plt
import sys

from matplotlib.gridspec import GridSpec

# ========== Params =============
SUMMARY_STEP = 30
SUMMARY_PATH = 'logs/'

SAVE_STEP = 1e3
SAVE_PATH = 'checkpoints/'

ACTIONS = 6
WIDTH = 64
HEIGHT = 64
IMAGE_BUFFER_SIZE = 4
CHANNELS = IMAGE_BUFFER_SIZE#3
H_SIZE = 512

LEARNING_RATE = 1e-6
BATCH = 32

EPISODE_START = 100
E_GREEDY = 1.0
E_GREEDY_MIN = 0.05
REWARD_DECAY = 0.99
EXPLORATION = 1000

MEMORY_SIZE = 50000

UPDATE_FREQUENCY = 4

TRAINING_FREQUENCY = 1
TARGET_UPDATE_FREQUENCE = 100

# ========== Plotter ==========
class Plotter(object):
    def __init__(self):
        self.q_eval_max = []
        self.q_eval_avg = []
        self.q_eval_min = []
        self.reward = []
        self.epsilon = []
        self.loss = []
        self.steps = []
        self.size = 0

        plt.ion()
        self.fig = plt.figure('DashBoard')
        self.fig.suptitle('Values through Episodes')

        self.gs = GridSpec(3, 3)

        self.total_reward_ax = plt.subplot(self.gs[0, :])
        self.total_reward_ax.plot(self.steps, self.reward, color = 'orange')
        self.total_reward_ax.set_ylabel('Total Reward')

        self.q_eval_ax = plt.subplot(self.gs[1, :])
        self.q_eval_ax.plot(self.steps, self.q_eval_max, color = 'blue')
        self.q_eval_ax.plot(self.steps, self.q_eval_avg, color = 'cyan')
        self.q_eval_ax.plot(self.steps, self.q_eval_min, color = 'grey')
        self.q_eval_ax.set_ylabel('Qeval')

        self.epsilon_ax = plt.subplot(self.gs[2, -1])
        self.epsilon_ax.plot(self.steps, self.epsilon, color = 'magenta')
        self.epsilon_ax.set_ylabel('Epsilon')

        self.loss_ax = plt.subplot(self.gs[2, :-1])
        self.loss_ax.plot(self.steps, self.loss, color = 'red')
        self.loss_ax.set_ylabel('Loss')

        self.gs.tight_layout(self.fig, h_pad=0.5)

    def add(self, q_max, q_avg, q_min, r, e, l, t):
        self.size += 1
        self.q_eval_max.append(q_max)
        self.q_eval_avg.append(q_avg)
        self.q_eval_min.append(q_min)
        self.reward.append(r)
        self.epsilon.append(e)
        self.loss.append(l)
        self.steps.append(t)

    def observe(self):
        min_steps, max_steps = min(self.steps), max(self.steps)

        self.total_reward_ax.plot(self.steps, self.reward, color = 'orange')
        self.total_reward_ax.set_xlim(min_steps, max_steps)
        self.total_reward_ax.set_ylim(min(self.reward) - 2, max(self.reward) + 2)

        self.q_eval_ax.plot(self.steps, self.q_eval_max, color = 'blue')
        self.q_eval_ax.plot(self.steps, self.q_eval_avg, color = 'cyan')
        self.q_eval_ax.plot(self.steps, self.q_eval_min, color = 'grey')
        self.q_eval_ax.set_xlim(min_steps, max_steps)
        min_q, max_q = min(min(self.q_eval_max), min(self.q_eval_avg), min(self.q_eval_min)), max(max(self.q_eval_max), max(self.q_eval_avg), max(self.q_eval_min))
        self.q_eval_ax.set_ylim(min_q, max_q)

        self.epsilon_ax.plot(self.steps, self.epsilon, color = 'magenta')
        self.epsilon_ax.set_xlim(min_steps, max_steps)
        self.epsilon_ax.set_ylim(0, 1)

        self.loss_ax.plot(self.steps, self.loss, color = 'red')
        self.loss_ax.set_xlim(min_steps, max_steps)
        self.loss_ax.set_ylim(0, max(self.loss))

        plt.draw()
        plt.pause(0.001)

# ========== Memo =============
class Memo(object):
    def __init__(self, s, a, r, s_):
        self.s = s
        self.a = a
        self.r = r
        self.s_ = s_

# ========== Memory ===========
class Memory(object):
    def __init__(self, size):
        self.size = size
        self.counter = 0
        self.buffer = []

    def store(self, memo):
        if len(self.buffer) <= self.size:
            self.buffer.append(memo)
        else:
            index = self.counter % self.size
            self.buffer[index] = memo

    def batch(self, size):
        sample_size = min(size, len(self.buffer))
        sample = random.sample(self.buffer, sample_size)

        s = np.array([element.s for element in sample])
        a = np.array([element.a for element in sample])
        r = np.array([element.r for element in sample])
        s_ = np.array([element.s_ for element in sample])

        return s, a, r, s_

    def __len__(self):
        return len(self.buffer)

# Deep QNetwork
class DQN(object):
    def __init__(self, h_size, name):
        with tf.variable_scope(name):
            self.image_in = tf.placeholder(
                name = 'ImageInput',
                shape = [None, WIDTH, HEIGHT, CHANNELS],
                dtype = tf.float32
            )
            self._conv_net(h_size)
            self._final_q_values(h_size)
            self._loss()

    def _conv_net(self, h_size):
        with tf.variable_scope('ConvNet'):
            self.conv_1 = slim.conv2d(
                inputs = self.image_in,
                num_outputs = 32,
                kernel_size = [8, 8],
                stride = [4, 4],
                padding = 'VALID',
                scope = 'Conv1'
            )
            self.conv_2 = slim.conv2d(
                inputs = self.conv_1,
                num_outputs = 64,
                kernel_size = [4, 4],
                stride = [2, 2],
                padding = 'VALID',
                scope = 'Conv2'
            )
            self.conv_3 = slim.conv2d(
                inputs = self.conv_2,
                num_outputs = 64,
                kernel_size = [3, 3],
                stride = [1, 1],
                padding = 'VALID',
                scope = 'Conv3'
            )
            self.conv_4 = slim.conv2d(
                inputs = self.conv_3,
                num_outputs = h_size,
                kernel_size = [4, 4],
                stride = [1, 1],
                padding = 'VALID',
                scope = 'Conv4'
            )

    def _final_q_values(self, h_size):
        with tf.variable_scope('FinalQValues'):
            self.advantage_conv, self.value_conv = tf.split(
                self.conv_4,
                2,
                3
            )
            self.advantage_flat = slim.flatten(self.advantage_conv)
            self.value_flat = slim.flatten(self.value_conv)
            xavier = tf.contrib.layers.xavier_initializer()
            self.advantage_w = tf.Variable(
                xavier([h_size // 2, ACTIONS]),
                name = 'AdvantageW'
            )
            self.value_w = tf.Variable(
                xavier([h_size // 2, 1]),
                name = 'ValueW'
            )
            self.advantage = tf.matmul(
                self.advantage_flat,
                self.advantage_w,
                name = 'Advantage'
            )
            self.value = tf.matmul(
                self.value_flat,
                self.value_w,
                name = 'Value'
            )
            sub_mean = tf.subtract(
                self.advantage,
                tf.reduce_mean(
                    self.advantage,
                    axis = 1,
                    keep_dims = True
                )
            )
            self.q_out = self.value + sub_mean
            self.predict = tf.argmax(self.q_out, 1)

    def _loss(self):
        with tf.variable_scope('Loss'):
            self.q_target = tf.placeholder(
                name = 'QTarget',
                shape = [None],
                dtype = tf.float32
            )
            self.actions = tf.placeholder(
                name = 'Action',
                shape = [None],
                dtype = tf.int32
            )
            self.action_onehot = tf.one_hot(
                self.actions,
                ACTIONS,
                dtype = tf.float32
            )
            self.q = tf.reduce_sum(
                tf.multiply(
                    self.q_out,
                    self.action_onehot
                ),
                axis = 1
            )
            self.td_error = tf.square(
                self.q_target - self.q,
                name = 'TDError'
            )
            self.loss = tf.reduce_mean(
                self.td_error,
                name = 'Loss'
            )

        self.trainer = tf.train.AdamOptimizer(LEARNING_RATE)
        self.update = self.trainer.minimize(self.loss)

# Double Dueling Deep QNetwork
class DDDQN(object):
    def __init__(self, load = False):
        title = 'learn_rate: ' + str(LEARNING_RATE)
        title += ' | ep_start: ' + str(EPISODE_START)
        title += ' | explo: ' + str(EXPLORATION)
        title += ' | mem_size: ' + str(MEMORY_SIZE)
        sys.stdout.write('\x1b]2;' + title + '\x07')
        self.is_ai = False
        self.plotter = Plotter()

        with tf.variable_scope('DDDQN'):
            self.main_qn = DQN(H_SIZE, 'MainDQN')
            self.target_qn = DQN(H_SIZE, 'TargetDQN')

            with tf.variable_scope('Replace'):
                t_params = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, 'TargetDQN')
                e_params = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, 'MainDQN')
                self.replace_target_op = [tf.assign(t, e) for t, e in zip(t_params, e_params)]

            self.memory = Memory(MEMORY_SIZE)

            self.e = E_GREEDY
            self.e_factor = (E_GREEDY - E_GREEDY_MIN) / EXPLORATION

            self.init = tf.global_variables_initializer()
            self.saver = tf.train.Saver()
            self.sess = tf.Session()
            self.summary_writer = tf.summary.FileWriter(
                SUMMARY_PATH,
                self.sess.graph
            )

            self.global_step = 0
            self.episode = 0
            self.episode_trained = False
            self.total_reward = 0
            self.last_total_reward = 0

        self.sess.run(self.init)
        if load:
            ckpt = tf.train.get_checkpoint_state(SAVE_PATH)
            self.saver.restor(
                self.sess,
                ckpt.model_checkpoint_path
            )

    def store(self, s, a, r, s_):
        memo = Memo(self.preprocess(s), a, r, self.preprocess(s_))
        self.memory.store(memo)

    def switch_networks(self):
        temp = self.main_qn
        self.main_qn = self.target_qn
        self.target_qn = temp

    def preprocess(self, input):
        return np.array(input) / 255.0

    def choose_action(self, image_input):
        if np.random.rand(1) < self.e or self.global_step < EPISODE_START:
            a = np.random.randint(0, ACTIONS)
            self.is_ai = False
        else:
            a = self.sess.run(
                self.main_qn.predict,
                feed_dict = {
                    self.main_qn.image_in: self.preprocess([image_input])
                }
            )[0]
            self.is_ai = True

        return a

    def update_training_variables(self):
        self.episode += 1
        self.last_total_reward = self.total_reward
        self.total_reward = 0
        self.episode_trained = False

    def training_step(self):
        self.global_step += 1

        if self.episode > EPISODE_START:

            if not self.episode_trained and (self.episode - EPISODE_START) % TRAINING_FREQUENCY == 0:
                self.episode_trained = True
                self.e = self.e - self.e_factor if self.e > E_GREEDY_MIN else E_GREEDY_MIN

                # if np.random.uniform() < 0.5:
                    # self.switch_networks()

                batch_s, batch_a, batch_r, batch_s_ = self.memory.batch(BATCH)
                size = batch_s.shape[0]

                q1 = self.sess.run(
                    self.main_qn.predict,
                    feed_dict = {
                        self.main_qn.image_in: batch_s_
                    }
                )
                q2 = self.sess.run(
                    self.target_qn.q_out,
                    feed_dict = {
                        self.target_qn.image_in: batch_s_
                    }
                )

                double_q = q2[range(size), q1]
                target_q = batch_r + (REWARD_DECAY * double_q)

                _, loss = self.sess.run(
                    [self.main_qn.update, self.main_qn.loss],
                    feed_dict = {
                        self.main_qn.image_in: batch_s,
                        self.main_qn.q_target: target_q,
                        self.main_qn.actions: batch_a
                    }
                )

                print('Episode: ' + str(self.episode) + ' Loss: ' + str(loss) + ' Qvalue: ' + str(np.mean(double_q)))

                # Update Eval Graph
                self.plotter.add(np.max(double_q), np.mean(double_q), np.min(double_q), self.last_total_reward, self.e, loss, self.episode)
                self.plotter.observe()

            # Update the second network wieghts
            if self.episode % TARGET_UPDATE_FREQUENCE and self.episode != 0:
                self.sess.run(self.replace_target_op)

        if self.global_step % SAVE_STEP == 0 and self.global_step != 0:
            self.saver.save(
                self.sess,
                SAVE_PATH + 'model-' + str(self.global_step) + '.ckpt'
            )
