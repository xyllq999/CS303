import multiprocessing as mp
import time
from Initialization import INF, Pre_work
import sys
import numpy as np
from tabu import Tabu_Search
import random
import copy


class Worker(mp.Process):
    def __init__(self, outQ, timelimit, random_seed):
        super(Worker, self).__init__(target=self.start)
        self.outQ = outQ
        random.seed(random_seed)  # 如果子进程的任务是有随机性的，一定要给每个子进程不同的随机数种子，否则就在重复相同的结果了
        self.tabu = None
        self.timelimit = timelimit

    def run(self):
        self.tabu = Tabu_Search(pre_work)
        solution, cost = self.tabu.search(self.timelimit)
        self.outQ.put((solution, cost))  # 返回结果


def create_worker(num, pw, timelimit):
    '''
    创建子进程备用
    :param num: 多线程数量
    '''
    for i in range(num):
        worker.append(Worker(mp.Queue(), timelimit, np.random.randint(0, 10 ** 9)))
        worker[i].start()


def finish_worker():
    '''
    关闭所有子线程
    '''
    for w in worker:
        w.terminate()


if __name__ == '__main__':
    start_time = time.time()
    filename = sys.argv[1]
    seed = int(sys.argv[5])
    random.seed(seed)
    np.random.seed(seed)
    timelimit = int(sys.argv[3])
    worker = []
    worker_num = 8
    pre_work = Pre_work(filename)
    create_worker(worker_num, pre_work, timelimit)
    best_solution = None
    best_cost = INF
    for i in range(worker_num):
        solution, cost = worker[i].outQ.get()  # 用同样的规则取回结果， 如果任务尚未完成，此处会阻塞等待子进程完成任务
        if cost < best_cost:
            best_solution = copy.deepcopy(solution)
            best_cost = cost
    print('s ', end='')
    print(best_solution)
    print('q ', end='')
    print(best_cost)
    finish_worker()
    # print(time.time() - start_time)
