import tensorflow as tf
import numpy as np
import engine.tools.plotter as plot
import engine.deep_learning.memory as mem
import engine.deep_learning.dueling_deep_q_network as net
import engine.deep_learning.config as conf
import random
import sys

# Double Dueling Deep QNetwork
class DDDQN(object):
    def __init__(self, load = False):
        title = 'learning_rate: {0} BURN_IN: {1} exploration: {2} memory_size: {3}'
        title = title.format(str(conf.LEARNING_RATE), str(conf.BURN_IN), str(conf.EXPLORATION), str(conf.MEMORY_SIZE))
        sys.stdout.write('\x1b]2;' + title + '\x07')

        with tf.variable_scope('DDDQN'):
            self.main_qn = net.DDQN(conf.H_SIZE, 'MainDQN')
            self.target_qn = net.DDQN(conf.H_SIZE, 'TargetDQN')

            with tf.variable_scope('Replace'):
                t_params = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, 'TargetDQN')
                e_params = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, 'MainDQN')
                self.replace_target_op = [tf.assign(t, e) for t, e in zip(t_params, e_params)]

            self.init = tf.global_variables_initializer()
            self.saver = tf.train.Saver()
            self.sess = tf.Session()
            self.summary_writer = tf.summary.FileWriter(
                conf.SUMMARY_PATH,
                self.sess.graph
            )

        self.is_ai = False
        self.plotter = plot.Plotter()

        self.memory = mem.Memory(conf.MEMORY_SIZE)
        self.temp_memory = mem.Memory(conf.MEMORY_SIZE)

        self.e = conf.E_GREEDY
        self.e_factor = (conf.E_GREEDY - conf.E_GREEDY_MIN) / conf.EXPLORATION

        self.global_step = 0
        self.episode = 0
        self.episode_trained = False
        self.total_reward = 0
        self.last_total_reward = 0
        self.score = 0
        self.last_score = 0

        self.sess.run(self.init)
        self.sess.run(self.replace_target_op)
        if load:
            ckpt = tf.train.get_checkpoint_state(conf.SAVE_PATH)
            self.saver.restore(self.sess, ckpt.model_checkpoint_path)

    def store(self, s, a, r, s_):
        memo = mem.Memo(self.preprocess(s), a, r, self.preprocess(s_))
        self.temp_memory.store(memo)

    def switch_networks(self):
        temp = self.main_qn
        self.main_qn = self.target_qn
        self.target_qn = temp

    def preprocess(self, input):
        return (np.array(input) -128.0) / 255.0

    def choose_action(self, image_input):
        if np.random.rand(1) < self.e or self.global_step < conf.BURN_IN:
            a = np.random.randint(0, conf.ACTIONS)
            self.is_ai = False
        else:
            a = self.sess.run(self.main_qn.predict, feed_dict = {self.main_qn.image_in: self.preprocess([image_input])})[0]
            self.is_ai = True
        return a

    def update_training_variables(self):
        self.last_total_reward = self.total_reward
        self.last_score = self.score
        self.episode += 1

        if (not conf.HAPPY_REPLAY) or self.last_score >= conf.SCORE_MIN:
            for memo in self.temp_memory.buffer:
                self.memory.store(memo)
                self.temp_memory.reset()

        self.total_reward = 0
        self.score = 0
        self.episode_trained = False

    def training_step(self):
        self.global_step += 1

        if self.episode > conf.BURN_IN:

            if not self.episode_trained and (self.episode - conf.BURN_IN) % conf.TRAINING_FREQUENCY == 0:
                self.episode_trained = True
                self.e = self.e - self.e_factor if self.e > conf.E_GREEDY_MIN else conf.E_GREEDY_MIN

                # if np.random.uniform() < 0.5:
                    # self.switch_networks()

                batch_s, batch_a, batch_r, batch_s_ = self.memory.batch(conf.BATCH)
                size = batch_s.shape[0]

                q1 = self.sess.run(self.main_qn.predict, feed_dict = {self.main_qn.image_in: batch_s_})
                q2 = self.sess.run(self.target_qn.q_out, feed_dict = {self.target_qn.image_in: batch_s_})
                double_q = q2[range(size), q1]
                target_q = batch_r + (conf.REWARD_DECAY * double_q)

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
                self.plotter.add(np.max(double_q), np.mean(double_q), np.min(double_q), self.last_total_reward, self.e, loss, self.last_score, self.episode)
                self.plotter.observe()

            # Update the second network wieghts
            if self.episode % conf.TARGET_UPDATE_FREQUENCE:
                self.sess.run(self.replace_target_op)

        if self.global_step % conf.SAVE_STEP == 0 and self.global_step != 0:
            self.saver.save(
                self.sess,
                conf.SAVE_PATH + 'model-' + str(self.global_step) + '.ckpt'
            )
