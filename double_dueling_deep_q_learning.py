import tensorflow as tf
import tensorflow.contrib.slim as slim
import numpy as np
import random

# ========== Params =============
SUMMARY_STEP = 30
SUMMARY_PATH = 'logs/'

SAVE_STEP = 1000
SAVE_PATH = 'checkpoints/'

ACTIONS = 6
WIDTH = 64
HEIGHT = 64
CHANNELS = 3
H_SIZE = 512

LEARNING_RATE = 25e-5
BATCH = 32

EPISODE_START = 1e4#2e5
E_GREEDY = 1.0
REWARD_DECAY = 0.99
EXPLORATION = 1e4#1e6

REPLACE_TARGET = 300
TAU = 1e-3
MEMORY_SIZE = int(1e4)#int(2e5)

UPDATE_FREQUENCY = 8

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
        self.buffer_size = 0
        self.buffer = []

    def store(self, memo):
        if self.buffer_size < self.size:
            self.buffer_size += 1
            self.buffer.append(memo)
        else:
            index = random.randint(0, self.size - 1)
            self.buffer[index] = memo

    def sample(self, size):
        sample_size = min(self.size, self.buffer_size)
        sample_indexes = np.random.choice(
            sample_size,
            size = min(sample_size, size)
        )
        sample = [self.buffer[i] for i in sample_indexes]

        s = np.array([memo.s for memo in sample])
        a = np.array([memo.a for memo in sample])
        r = np.array([memo.r for memo in sample])
        s_ = np.array([memo.s_ for memo in sample])

        return s, a, r, s_

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
        self.is_ai = False

        with tf.variable_scope('DDDQN'):
            self.main_qn = DQN(H_SIZE, 'MainDQN')
            self.target_qn = DQN(H_SIZE, 'TargetDQN')

            self.trainables = tf.trainable_variables()
            self.target_replace = self._replace(
                self.trainables,
                TAU
            )

            self.memory = Memory(MEMORY_SIZE)

            self.e = E_GREEDY
            self.e_factor = (E_GREEDY - 0.1) / EXPLORATION

            self.init = tf.global_variables_initializer()
            self.saver = tf.train.Saver()
            self.sess = tf.Session()
            self.summary_writer = tf.summary.FileWriter(
                SUMMARY_PATH,
                self.sess.graph
            )

            self.global_step = 0

        self.sess.run(self.init)
        if load:
            ckpt = tf.train.get_checkpoint_state(SAVE_PATH)
            self.saver.restor(
                self.sess,
                ckpt.model_checkpoint_path
            )

    def _replace(self, trainables, tau):
        total_vars = len(trainables)
        op_holder = []
        for idx, var in enumerate(trainables[0:total_vars//2]):
            val = trainables[idx + total_vars//2].value()
            assign_val = (var.value() * tau) + ((1 - tau) * val)
            element = trainables[idx + total_vars//2].assign((assign_val))
            op_holder.append(element)
        return op_holder

    def _update_target(self, target_replace, sess):
        for op in target_replace:
            sess.run(op)

    def store(self, s, a, r, s_):
        memo = Memo(s, a, r, s_)
        self.memory.store(memo)

    def choose_action(self, image_input):
        if np.random.rand(1) < self.e or self.global_step < EPISODE_START:
            a = np.random.randint(0, ACTIONS)
            self.is_ai = False
        else:
            a = self.sess.run(
                self.main_qn.predict,
                feed_dict = {
                    self.main_qn.image_in: [image_input]
                }
            )[0]
            self.is_ai = True

        return a

    def training_step(self):
        self.global_step += 1
        if self.global_step > EPISODE_START:
            self.e = self.e - self.e_factor if self.e > 0.1 else self.e

            if self.global_step % UPDATE_FREQUENCY == 0 and self.global_step != 0:
                batch_s, batch_a, batch_r, batch_s_ = self.memory.sample(BATCH)

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

                double_q = q2[range(BATCH), q1]
                target_q = batch_r + (REWARD_DECAY * double_q)

                _ = self.sess.run(
                    self.main_qn.update,
                    feed_dict = {
                        self.main_qn.image_in: batch_s,
                        self.main_qn.q_target: target_q,
                        self.main_qn.actions: batch_a
                    }
                )

                self._update_target(self.target_replace, self.sess)

            if self.global_step % SAVE_STEP == 0 and self.global_step != 0:
                self.saver.save(
                    self.sess,
                    SAVE_PATH + 'model-' + str(self.global_step) + '.ckpt'
                )
