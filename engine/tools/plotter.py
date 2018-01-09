import matplotlib.pyplot as plt
import numpy as np
import engine.deep_learning.config as conf

from matplotlib.gridspec import GridSpec

# ========== Plotter ==========
class Plotter(object):
    def __init__(self):
        self.q_eval_max = []
        self.q_eval_avg = []
        self.q_eval_min = []
        self.reward = []
        self.epsilon = []
        self.loss = []
        self.score = []
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

        self.loss_ax = plt.subplot(self.gs[2, 0])
        self.loss_ax.plot(self.steps, self.loss, color = 'red')
        self.loss_ax.set_ylabel('Loss')

        self.score_ax = plt.subplot(self.gs[2, 1])
        self.score_ax.plot(self.steps, self.score, color = 'purple')
        self.score_ax.set_ylabel('Score')

        self.gs.tight_layout(self.fig, h_pad=0.5)

        with open(conf.PLOTTER_SUMMARY, 'w') as myfile:
            myfile.write('q_max;q_avg;q_min;r;e;l;s;t\n')

    def add(self, q_max, q_avg, q_min, r, e, l, s, t):
        if self.size > conf.PLOTTER_LIMIT:
            self.q_eval_max.pop(0)
            self.q_eval_avg.pop(0)
            self.q_eval_min.pop(0)
            self.reward.pop(0)
            self.epsilon.pop(0)
            self.loss.pop(0)
            self.score.pop(0)
            self.steps.pop(0)

        self.size += 1
        self.q_eval_max.append(q_max)
        self.q_eval_avg.append(q_avg)
        self.q_eval_min.append(q_min)
        self.reward.append(r)
        self.epsilon.append(e)
        self.loss.append(l)
        self.score.append(s)
        self.steps.append(t)

        with open(conf.PLOTTER_SUMMARY, 'a') as myfile:
            string = '{0};{1};{2};{3};{4};{5};{6};{7}\n'
            string = string.format(str(q_max), str(q_avg), str(q_min), str(r), str(e), str(l), str(s), str(t))
            myfile.write(string)

    def clear_axis(self):
        self.total_reward_ax.cla()
        self.q_eval_ax.cla()
        self.epsilon_ax.cla()
        self.loss_ax.cla()
        self.score_ax.cla()

    def observe(self):
        min_steps, max_steps = min(self.steps), max(self.steps)

        self.clear_axis()

        self.total_reward_ax.plot(self.steps, self.get_mean_list(self.reward), color = 'orange')
        self.total_reward_ax.set_xlim(min_steps, max_steps)
        self.total_reward_ax.set_ylim(min(self.reward) - 2, max(self.reward) + 2)
        self.total_reward_ax.set_ylabel('Total Reward')

        self.q_eval_ax.plot(self.steps, self.get_mean_list(self.q_eval_max), color = 'blue')
        self.q_eval_ax.plot(self.steps, self.get_mean_list(self.q_eval_avg), color = 'cyan')
        self.q_eval_ax.plot(self.steps, self.get_mean_list(self.q_eval_min), color = 'grey')
        self.q_eval_ax.set_xlim(min_steps, max_steps)
        min_q, max_q = min(min(self.q_eval_max), min(self.q_eval_avg), min(self.q_eval_min)), max(max(self.q_eval_max), max(self.q_eval_avg), max(self.q_eval_min))
        self.q_eval_ax.set_ylim(min_q, max_q)
        self.q_eval_ax.set_ylabel('Qeval')

        self.epsilon_ax.plot(self.steps, self.epsilon, color = 'magenta')
        self.epsilon_ax.set_xlim(min_steps, max_steps)
        self.epsilon_ax.set_ylim(0, 1)
        self.epsilon_ax.set_ylabel('Epsilon')

        self.loss_ax.plot(self.steps, self.get_mean_list(self.loss), color = 'red')
        self.loss_ax.set_xlim(min_steps, max_steps)
        self.loss_ax.set_ylim(0, max(self.loss))
        self.loss_ax.set_ylabel('Loss')

        self.score_ax.plot(self.steps, self.get_mean_list(self.score), color = 'purple')
        self.score_ax.set_xlim(min_steps, max_steps)
        self.score_ax.set_ylim(0, max(self.score))
        self.score_ax.set_ylabel('Score')

        plt.draw()
        plt.pause(0.001)

    def get_mean_list(self, l):
        n = conf.PLOTTER_MEAN
        res = [l[i] if i <= n or i >= len(l) - n else self.get_mean(l, i, n) for i in xrange(len(l))]
        return res

    def get_mean(self, l, index, n):
        mean = np.mean(np.array([l[index + i] for i in xrange(-n, n)]))
        return mean
