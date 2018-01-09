import tensorflow as tf
import tensorflow.contrib.slim as slim
import numpy as np
import config as conf

# Deep QNetwork
class DDQN(object):
    def __init__(self, h_size, name):
        with tf.variable_scope(name):
            self.image_in = tf.placeholder(
                name = 'ImageInput',
                shape = [None, conf.WIDTH, conf.HEIGHT, conf.CHANNELS],
                dtype = tf.float32
            )
            self._conv_net(h_size)
            self._final_q_values(h_size)
            self._loss()

    def _conv_net(self, h_size):
        with tf.variable_scope('ConvNet'):
            self.conv_1 = slim.conv2d(self.image_in, 32, [8, 8], stride = [4, 4], scope = 'Conv1')
            self.conv_2 = slim.conv2d(self.conv_1, 64, [4, 4], stride = [2, 2], scope = 'Conv2')
            self.conv_3 = slim.conv2d(self.conv_2, 64, [3, 3], stride = [1, 1], scope = 'Conv3')
            self.conv_4 = slim.conv2d(self.conv_3, h_size, [4, 4], stride = [1, 1], scope = 'Conv4')

    def _final_q_values(self, h_size):
        with tf.variable_scope('FinalQValues'):
            xavier = tf.contrib.layers.xavier_initializer()

            self.advantage_conv, self.value_conv = tf.split(self.conv_4, 2, 3)
            self.advantage_flat = slim.flatten(self.advantage_conv, scope = 'AdvantageFlat')
            self.value_flat = slim.flatten(self.value_conv, scope = 'ValueFlat')

            self.advantage = slim.fully_connected(self.advantage_flat, conf.ACTIONS, activation_fn = None, scope = 'Advantage')
            self.value = slim.fully_connected(self.value_flat, 1, activation_fn = None, scope = 'Value')

            advantage_mean = tf.reduce_mean(self.advantage, axis = 1, keep_dims = True)
            sub_mean = tf.subtract(self.advantage, advantage_mean)
            self.q_out = self.value + sub_mean
            self.predict = tf.argmax(self.q_out, 1)

    def _loss(self):
        with tf.variable_scope('Loss'):
            self.q_target = tf.placeholder(name = 'QTarget', shape = [None], dtype = tf.float32)
            self.actions = tf.placeholder(name = 'Action', shape = [None], dtype = tf.int32)
            self.action_onehot = tf.one_hot(self.actions, conf.ACTIONS, dtype = tf.float32)
            self.q = tf.reduce_sum(tf.multiply(self.q_out, self.action_onehot), axis = 1)
            self.td_error = tf.square(self.q_target - self.q, name = 'TDError')
            self.loss_uncliped = tf.reduce_mean(self.td_error, name = 'LossUncliped')
            self.loss = tf.clip_by_value(self.loss_uncliped, -1, 1, name = 'Loss')

        self.trainer = tf.train.RMSPropOptimizer(conf.LEARNING_RATE, momentum = conf.MOMENTUM)#tf.train.AdamOptimizer(conf.LEARNING_RATE)
        self.update = self.trainer.minimize(self.loss)
