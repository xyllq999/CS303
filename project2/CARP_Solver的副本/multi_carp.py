import multiprocessing as mp
import time
import sys
import numpy as np


class Worker(mp.Process):
    def __init__(self, inQ, outQ, random_seed):
        super(Worker, self).__init__(target=self.start)
        self.inQ = inQ
        self.outQ = outQ
        np.random.seed(random_seed)  # 如果子进程的任务是有随机性的，一定要给每个子进程不同的随机数种子，否则就在重复相同的结果了

    def run(self):
        while True:
            task = self.inQ.get()  # 取出任务， 如果队列为空， 这一步会阻塞直到队列有元素
            x, y = task  # 解析任务
            sum, product = sum_and_product(x, y)  # 执行任务
            self.outQ.put((sum, product))  # 返回结果


def create_worker(num):
    '''
    创建子进程备用
    :param num: 多线程数量
    '''
    for i in range(num):
        worker.append(Worker(mp.Queue(), mp.Queue(), np.random.randint(0, 10 ** 9)))
        worker[i].start()


def finish_worker():
    '''
    关闭所有子线程
    '''
    for w in worker:
        w.terminate()


def sum_and_product(x, y):
    '''
    计算两个数的和与积
    '''
    return x + y, x * y


def s_format(s):
    s_print = []
    for p in s:
        s_print.append(0)
        s_print.extend(p)
        s_print.append(0)
    return s_print


if __name__ == '__main__':
    print("多进程示例")
    np.random.seed(3)
    worker = []
    worker_num = 8
    create_worker(worker_num)
    Task = [np.random.randint(0, 10, 2) for i in range(16)]  # 生成16个随机任务， 每个任务是2个整数， 需要计算两数之和与积
    print('Task', Task)
    for i, t in enumerate(Task):
        worker[i % worker_num].inQ.put(t)  # 根据编号取模， 将任务平均分配到子进程上
    result = []
    for i, t in enumerate(Task):
        result.append(worker[i % worker_num].outQ.get())  # 用同样的规则取回结果， 如果任务尚未完成，此处会阻塞等待子进程完成任务
    print('result', result)
    finish_worker()
