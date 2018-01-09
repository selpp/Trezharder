import numpy as np
import random

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

    def reset(self):
        self.counter = 0
        self.buffer = []

    def __len__(self):
        return len(self.buffer)
