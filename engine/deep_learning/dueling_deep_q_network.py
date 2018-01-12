import tensorflow as tf
import numpy as np
import engine.deep_learning.config as conf
import engine.deep_learning.utils as utils

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
            self.conv_in = self.image_in
            for conv in conf.CNN:
                self.conv_in = utils.conv2D(self.conv_in, conv.channels, conv.kernel, conv.stride, conv.scope)

    def _final_q_values(self, h_size):
        with tf.variable_scope('FinalQValues'):
            self.flat_conv = utils.flatten(self.conv_in, 'FlatConv')

            self.advantage_hidden = utils.dense(self.flat_conv, h_size, 'AdvantageHidden')
            self.value_hidden = utils.dense(self.flat_conv, h_size, 'ValueHidden')

            self.advantage = utils.dense(self.advantage_hidden, conf.ACTIONS, 'Advantage', activation_fn = None)
            self.value = utils.dense(self.value_hidden, 1, 'Value', activation_fn = None)

            advantage_mean = tf.reduce_mean(self.advantage, reduction_indices = 1, keep_dims = True)
            sub_mean = tf.subtract(self.advantage, advantage_mean)
            self.q_out = self.value + sub_mean
            self.predict = tf.argmax(self.q_out, dimension = 1)

    def _clip_error(self, e):
        try:
            return tf.select(tf.abs(e) < 1.0, 0.5 * tf.square(e), tf.abs(e) - 0.5)
        except:
            return tf.where(tf.abs(e) < 1.0, 0.5 * tf.square(e), tf.abs(e) - 0.5)

    def _loss(self):
        with tf.variable_scope('Loss'):
            self.q_target = tf.placeholder(name = 'QTarget', shape = [None], dtype = tf.float32)
            self.actions = tf.placeholder(name = 'Action', shape = [None], dtype = tf.int32)
            self.action_onehot = tf.one_hot(self.actions, conf.ACTIONS, 1.0, 0.0, dtype = tf.float32)
            self.q = tf.reduce_sum(tf.multiply(self.q_out, self.action_onehot), reduction_indices = 1, name = 'QActed')
            self.delta = self.q_target - self.q
            self.clipped_error = self._clip_error(self.delta)
            self.loss = tf.reduce_mean(self.clipped_error, name = 'Loss')

        self.trainer = tf.train.RMSPropOptimizer(conf.LEARNING_RATE, momentum = conf.MOMENTUM, epsilon = conf.RMS_EPSILON) #tf.train.AdamOptimizer(conf.LEARNING_RATE)
        self.update = self.trainer.minimize(self.loss)
