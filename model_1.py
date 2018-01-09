import tensorflow as tf
import numpy as np
import utils
import random
import matplotlib.pyplot as plt
import pickle

SUMMARY_STEP = 30
SUMMARY = 'logs/'

SAVE_STEP = 5000
CHECKPOINT = 'checkpoints/model.ckpt'
MEMORY = 'checkpoints/memory.save'

class SaveInfos(object):
    def __init__(self, learn_step_counter, memory_counter, prev_action_vector, memory, e_greedy):
        self.learn_step_counter = learn_step_counter
        self.memory_counter = memory_counter
        self.prev_action_vector = prev_action_vector
        self.memory = memory
        self.e_greedy = e_greedy

class Memo(object):
    def __init__(self, s, a, r, s_):
        self.s = s
        self.a = a
        self.r = r
        self.s_ = s_

    def __str__(self):
        msg = ''
        msg += str(self.s) + '\n'
        msg += str(self.a) + '\n'
        msg += str(self.r) + '\n'
        msg += str(self.s_) + '\n'
        return msg

class DeepQModel(object):
    def __init__(
        self,
        width,
        height,
        channels = 1,
        n_actions = 6,
        learning_rate = 25e-5,
        e_greedy = 1.0,
        reward_decay = 0.99,
        explo_it = 2e5,
        momentum = 0.05,
        replace_target_iteration = 300,
        memory_size = int(1e5),
        batch_size = 32
    ):
        self.n_actions = n_actions
        self.width = width
        self.height = height
        self.channels = channels
        self.n_features = width * height * channels

        self.learning_rate = learning_rate
        self.momentum = momentum
        self.batch_size = batch_size
        self.learn_step_counter = 0

        self.gamma = reward_decay
        self.replace_target_iteration = replace_target_iteration
        self.memory_size = memory_size

        self.explo_it = explo_it
        self.e_greedy_factor = (e_greedy - 0.1) / self.explo_it
        self.e_greedy_start = e_greedy
        self.observable_e_greedy = e_greedy

        self.memory_counter = 0
        i_ = random.randint(0, self.n_actions - 1)
        self.prev_action_vector = [0 if i_ != i else 1 for i in range(self.n_actions)]
        self.memory = []

        self.is_ai = False

        self.estimated_reward = 0

        self.build_net()

        t_params = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, 'target_net')
        e_params = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, 'eval_net')
        with tf.variable_scope('replacement'):
            self.replace_target_op = [tf.assign(t, e) for t, e in zip(t_params, e_params)]

        self.sess = tf.Session()
        self.summary_writer = tf.summary.FileWriter(SUMMARY, self.sess.graph)
        self.sess.run(tf.global_variables_initializer())
        self.saver = tf.train.Saver()

    def build_net(self):
        # Placeholders
        self.s = tf.placeholder(tf.float32, [None, self.width, self.height, self.channels], name = 's')
        self.s_ = tf.placeholder(tf.float32, [None, self.width, self.height, self.channels], name = 's_')
        self.r = tf.placeholder(tf.float32, [None, ], name = 'r')
        self.a = tf.placeholder(tf.int32, [None, ], name = 'a')

        # Evaluations
        with tf.variable_scope('eval_net'):
            self.q_eval = self.forward(self.s, self.n_actions)
        with tf.variable_scope('target_net'):
            self.q_next = self.forward(self.s_, self.n_actions)

        # Loss and train
        with tf.variable_scope('q_target'):
            reduce_max = tf.reduce_max(self.q_next, axis = 1, name = 'Qmax_s_')
            self.estimated_reward = reduce_max[0]
            tf.summary.scalar('estimated_reward', self.estimated_reward)
            q_target = self.r + self.gamma * reduce_max
            self.q_target = tf.stop_gradient(q_target)
        with tf.variable_scope('q_eval'):
            a_indices = tf.stack([tf.range(tf.shape(self.a)[0], dtype=tf.int32), self.a], axis=1)
            self.q_eval_wrt_a = tf.gather_nd(params=self.q_eval, indices=a_indices)
        with tf.variable_scope('loss'):
            self.loss = tf.reduce_mean(tf.squared_difference(self.q_target, self.q_eval_wrt_a, name='error'))
            tf.summary.scalar('loss', self.loss)
        with tf.variable_scope('train'):
            self.train_op = tf.train.RMSPropOptimizer(self.learning_rate,momentum=self.momentum).minimize(self.loss)

        # epsilon greedy
        with tf.variable_scope('epsilon_greedy'):
            self.e_greedy = tf.Variable(self.e_greedy_start, name = 'e_greedy')
            self.e_greedy_decay = tf.assign(self.e_greedy, tf.where(tf.less_equal(self.e_greedy, 0.1), 0.1, self.e_greedy - self.e_greedy_factor))
            tf.summary.scalar('e_greedy', self.e_greedy)

        tf.summary.scalar('learning_rate', self.learning_rate)

        self.summary_op = tf.summary.merge_all()

    def forward(self, x, n_actions):
        x = utils.conv('conv1', x, 32, kernel_size=[8,8], stride=[1,4,4,1], is_pretrain=False)
        x = utils.conv('conv2', x, 64, kernel_size=[4,4], stride=[1,2,2,1], is_pretrain=False)
        x = utils.conv('conv3', x, 64, kernel_size=[3,3], stride=[1,1,1,1], is_pretrain=False)
        x = utils.FC_layer('fc1', x, out_nodes = 512)
        x = utils.FC_layer('fc3', x, out_nodes = n_actions, activation_func = None)
        return x

    def store_transition(self, s, a, r, s_):
        if len(s.shape) < 3:
            transition = Memo(self.preprocess_frame(s)[:,:,np.newaxis], a, r, self.preprocess_frame(s_)[:,:,np.newaxis])
        else:
            transition = Memo(self.preprocess_frame(s), a, r, self.preprocess_frame(s_))

        if self.memory_counter < self.memory_size:
            self.memory.append(transition)
        else:
            index = random.randint(0, self.memory_size - 1)
            self.memory[index] = transition

        self.memory_counter += 1

    def _choose_monte_carlo(self,frame):
        from time import sleep

        if len(frame.shape) < 3:
            observation = frame[:,:,np.newaxis][np.newaxis,:]
        else:
            observation = frame[np.newaxis,:]

        action_vector = self.sess.run(self.q_eval, feed_dict = {self.s: observation})[0]
        total = np.sum(action_vector)
        proba_vector = action_vector / total
        print(proba_vector)
        sleep(1)
        cum_sum = 0
        selection = np.random.uniform()
        for i,action in enumerate(action_vector):
            cum_sum += action
            if selection <= cum_sum:
                return [0 if t != i else 1 for t in range(self.n_actions)]
        return [0 if t != self.n_actions - 1 else 1 for t in range(self.n_actions)]

    def preprocess_frame(self,frame):
        return (frame  / 255.0 - 0.5) * 2.0

    def _choose_ai(self, frame):
        self.is_ai = True
        if len(frame.shape) < 3:
            observation = frame[:,:,np.newaxis][np.newaxis,:]
        else:
            observation = frame[np.newaxis,:]

        action_vector = self.sess.run(self.q_eval, feed_dict = {self.s: observation})
        action_vector = action_vector[0]

        action_index = np.argmax(action_vector)
        action_vector = [0 if i != action_index else 1 for i in range(self.n_actions)]

        return action_vector

    def _choose_random(self):
        self.is_ai = False
        action_index = random.randint(0, self.n_actions - 1)
        action_vector = [0 if i != action_index else 1 for i in range(self.n_actions)]

        return action_vector

    def choose_action(self, frame, is_loaded = False):
        p = np.random.uniform()
        frame = self.preprocess_frame(frame)
        e_greedy = self.sess.run(self.e_greedy)
        action_vector = self._choose_random() if (not is_loaded and p < 0.05) or (p < e_greedy) else self._choose_ai(frame)
        return action_vector

    def load(self):
        self.saver.restore(self.sess, CHECKPOINT)
        '''with open(MEMORY, 'r') as file:
            save_infos = pickle.load(file)
            self.learn_step_counter = save_infos.learn_step_counter
            self.memory_counter = save_infos.memory_counter
            self.prev_action_vector = save_infos.prev_action_vector
            self.memory = save_infos.memory
            self.e_greedy = save_infos.e_greedy'''

    def save(self):
        self.saver.save(self.sess, CHECKPOINT)
        '''with open(MEMORY, 'w') as file:
            save_infos = SaveInfos(self.learn_step_counter, self.memory_counter, self.prev_action_vector, self.memory, self.e_greedy)
            pickle.dump(save_infos, file)'''

    def learn(self):
        if self.learn_step_counter % self.replace_target_iteration == 0 and self.learn_step_counter != 0:
            self.sess.run(self.replace_target_op)

        min_mem = min(self.memory_size,  self.memory_counter)
        sample_index = np.random.choice( min_mem, size = min(self.batch_size, min_mem))
        batch_memory = [self.memory[index] for index in sample_index]

        states = np.array([memo.s for memo in batch_memory])
        actions = np.array([memo.a for memo in batch_memory])
        rewards = np.array([memo.r for memo in batch_memory])
        states_ = np.array([memo.s_ for memo in batch_memory])

        _, summary_str = self.sess.run(
            [self.train_op, self.summary_op],
            feed_dict = {
                self.s: states,
                self.a: actions,
                self.r: rewards,
                self.s_: states_,
        })
        _, e_greedy = self.sess.run([self.e_greedy_decay, self.e_greedy])
        self.observable_e_greedy = e_greedy

        self.learn_step_counter += 1

        if self.learn_step_counter % SUMMARY_STEP == 0 and self.learn_step_counter > 0:
            self.summary_writer.add_summary(summary_str, self.learn_step_counter)
        if self.learn_step_counter % SAVE_STEP == 0 and self.learn_step_counter > 0:
            self.save()

if __name__ == '__main__':
    DQN = DeepQModel(80, 60)
