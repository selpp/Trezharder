import tensorflow as tf
import numpy as np
import utils

class Memo(object):
	def __init__(self, s, a, r, s_):
		self.s = s
		self.a = a
		self.r = r
		self.s_ = s_

class DeepQModel(object):
	def __init__(
		self,
		width,
		height,
		channels = 3,
		n_actions = 4,
		learning_rate = 0.01,
		reward_decay = 0.9,
		replace_target_iteration = 300,
		memory_size = 500,
		batch_size = 32,
		output_graph = False
	):
		self.n_actions = n_actions
		self.width = width
		self.height = height
		self.channels = channels
		self.n_features = width * height * channels
		self.learning_rate = learning_rate
		self.gamma = reward_decay
		self.replace_target_iteration = replace_target_iteration
		self.memory_size = memory_size
		self.batch_size = batch_size

		self.global_step = 0
		# [s, a, r, s_]
		self.memory = []

		self.build_net()
		t_params = tf.get_collection('target_net_params')
		e_params = tf.get_collection('eval_net_params')
		self.replace_target_op = [tf.assign(t, e) for t, e in zip(t_params, e_params)]

		self.sess = tf.Session()	

		if output_graph:
			tf.summary.FileWriter('logs/', self.ses.graph)

		self.sess.run(tf.global_variables_initializer())
		self.cost_historic = []	

	def build_net(self):
		self.s = tf.placeholder(tf.float32, [None, self.width, self.height, self.channels], name = 's')
		self.q_target = tf.placeholder(tf.float32, [None, self.n_actions], name = 'Q_target')
		self.q_eval = self.forward(self.s, self.n_actions, 'eval_net')

		with tf.variable_scope('loss'):
			self.loss = tf.reduce_mean(tf.squared_difference(self.q_target, self.q_eval))
		with tf.variable_scope('train'):
			self.train_op = tf.train.RMSPropOptimizer(self.learning_rate).minimize(self.loss)

		self.s_ = tf.placeholder(tf.float32, [None, self.width, self.height, self.channels], name = 's_')
		self.q_next = self.forward(self.s_, self.n_actions, 'target_net')

	def forward(self, x, n_actions, scope):
	    with tf.variable_scope(scope):
	        x = utils.conv('conv1', x, 32, kernel_size=[8,8], stride=[1,4,4,1], is_pretrain=False)   
	        x = utils.conv('conv2', x, 64, kernel_size=[4,4], stride=[1,2,2,1], is_pretrain=False)
	        x = utils.conv('conv3', x, 64, kernel_size=[3,3], stride=[1,1,1,1], is_pretrain=False)    
	        x = utils.FC_layer('fc1', x, out_nodes=512)        
	        x = utils.FC_layer('fc3', x, out_nodes=n_actions)
	        return x

	def store_transition(self, s, a, r, s_):
		if not hasattr(self, 'memory_counter'):
			self.memory_counter = 0

		transition = Memo(s, a, r, s_)
		index = self.memory_counter % self.memory_size
		self.memory.append(transition)

		self.memory_counter += 1

	def choose_action(self, observation):
		observation = observation[np.newaxis, :]
		actions_value = self.sess.run(self.q_eval, feed_dict = {self.s: observation})
		
		p = np.random.uniform()
		total = np.sum(actions_value)
		actions_value_part = [val/total if total != 0 else 0 for val in actions_value[0]]
		cumsum = np.cumsum(np.array(actions_value_part))
		action_index = 0
		for i in range(cumsum.shape[0]):
			if p < cumsum[i]:
				action_index = i
				break 
		
		return [0 if i != action_index else 1 for i in range(self.n_actions)]

	def learn(self):
		if self.learn_step_counter % self.replace_target_iter == 0:
			self.sess.run(self.replace_target_op)
			print('\nTarget params replaced\n')

		#if self.memory_counter > self.memory_size:
		#	sample_index = np.random.choice(self.memory_size, size = self.batch_size)
		#else:
		#	sample_index = np.random.choice(self.memory_counter, size = self.batch_size)
		sample_index = np.random.choice( np.min(self.memory_size,  self.memory_counter), size = self.batch_size)

		batch_memory = []
		for index in sample_index:
			if index < len(self.memory):
				batch_memory.append(self.memory[index]) 

		q_next, q_eval = self.sess.run(
			[self.q_next, self.q_eval],
			feed_dict = {
				self.s_: np.array([memo.s for memo in batch_memory]),
				self.s: np.array([memo.s_ for memo in batch_memory])
			})

		q_target = q_eval.copy()

		batch_index = np.arange(self.batch_size, dtype = np.int32)
		eval_action_index = np.array([memo.a for memo in batch_memory]).astype(int)
		reward = np.array([memo.r for memo in batch_memory])

		q_target[batch_index, eval_action_index] = reward + self.gamma * np.max(q_next, axis = 1) 

		_, self.cost = self.sess.run([self.train_op, self.loss],
			                         feed_dict = {self.s: np.array([memo.s for memo in batch_memory]), self.q_target: q_target})
		self.cost_historic.append(self.cost)

		self.learn_step_counter += 1

	def plot_cost(self):
		import matplotlib.pyplot as plt
		plt.plot(np.arange(len(self.cost_historic)), self.cost_historic)
		plt.ylabel('Cost')
		plt.xlabel('Training steps')
		plt.show()

if __name__ == '__main__':
	DQN = DeepQModel(80, 60)