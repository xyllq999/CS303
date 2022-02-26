import numpy as np
import random
import time

class GD(object):
    def __init__(self, x, y, learning_rate=0.01, precision=5, max_random_sample=800):
        self.x = np.c_[np.ones((x.shape[0])), x]
        self.y = y
        # self.epochs = epochs
        self.precision = precision
        self.max_random_sample = max_random_sample
        self.learning_rate = learning_rate
        self.w = np.random.uniform(size=np.shape(self.x)[1],)

    def get_loss(self, x, y):
        loss = max(0, 1 - y * np.dot(x, self.w))
        return loss

    def cal_sgd(self, x, y, w):
        if y * np.dot(x, w) < 1:
            w = w - self.learning_rate * (-y * x)
        else:
            w = w
        return w

    def train(self, t):
        start = time.time()
        # for epoch in range(self.epochs):
        loss = 10
        epoch = 0
        while loss > self.precision:
            if (time.time() - start) > (t - 2):
                return
            epoch += 1
            randomize = np.arange(len(self.x))
            np.random.shuffle(randomize)
            x = self.x[randomize]
            y = self.y[randomize]
            loss = 0
            m = len(x)
            while m > self.max_random_sample:
                m = int(m/2)
            for xi, yi in zip(x, y):
                loss += self.get_loss(xi, yi)
                self.w = self.cal_sgd(xi, yi, self.w)
            # print('epoch: {0} loss: {1}'.format(epoch, loss))
    
    def predict(self, x):
        x_test = np.c_[np.ones((x.shape[0])), x]
        return np.sign(np.dot(x_test, self.w))

























