import multiprocessing as mp
import time
import sys
import numpy as np
import random
import os


class Worker(mp.Process):
    def __init__(self, outQ, diffusion_model, random_seed, seed_set, V, E, adj_graph, rev_adj_graph):
        super(Worker, self).__init__(target=self.start)
        self.outQ = outQ
        random.seed(random_seed)
        self.diffusion_model = diffusion_model
        self.seed_set = seed_set
        self.V = V
        self.E = E
        self.adj_graph = adj_graph
        self.rev_adj_graph = rev_adj_graph

    def ic_process(self):
        total_num = 0
        for i in range(1250):
            activity_set = self.seed_set
            count = len(activity_set)
            active = [False for i in range(self.V + 1)]
            for _ in activity_set:
                active[_] = True
            while not len(activity_set) == 0:
                new_activity_set = []
                for seed in activity_set:
                    for neighbor in self.adj_graph[seed]:
                        if not active[neighbor[0]] and sample(neighbor[1]):
                            new_activity_set.append(neighbor[0])
                            active[neighbor[0]] = True
                count = count + len(new_activity_set)
                activity_set = new_activity_set
            total_num += count
        return total_num

    def lt_process(self):
        total_num = 0
        for i in range(1250):
            activity_set = self.seed_set
            thres = [0.0 for i in range(self.V + 1)]
            active = [False for i in range(self.V + 1)]
            for i in range(1, self.V + 1):
                thres[i] = random.uniform(0.0, 1.0)
                if thres[i] == 0.0 and len(self.rev_adj_graph[i]) != 0:
                    activity_set.append(i)
            for _ in activity_set:
                active[_] = True
            count = len(activity_set)
            while not len(activity_set) == 0:
                new_activity_set = []
                for seed in activity_set:
                    for neighbor in self.adj_graph[seed]:
                        if not active[neighbor[0]]:
                            w_total = 0.0
                            for rev_neighbor in self.rev_adj_graph[neighbor[0]]:
                                if active[rev_neighbor[0]]:
                                    w_total += rev_neighbor[1]
                            if w_total >= thres[neighbor[0]]:
                                active[neighbor[0]] = True
                                new_activity_set.append(neighbor[0])
                count = count + len(new_activity_set)
                activity_set = new_activity_set
            total_num += count
        return total_num

    def run(self):
        # print(time.time())
        total_num = 0
        if self.diffusion_model == 'IC':
            total_num = self.ic_process()
        else:
            total_num += self.lt_process()
        self.outQ.put(total_num)  # 返回结果


def create_worker(num):
    for i in range(num):
        worker.append(Worker(mp.Queue(), diffusion_model, np.random.randint(0, 10 ** 9), seed_set, V, E, adj_graph,
                             rev_adj_graph))
        worker[i].start()


def finish_worker():
    for w in worker:
        w.terminate()


def sample(p):
    return p > random.uniform(0.0, 1.0)


if __name__ == '__main__':
    start_time = time.time()
    social_network = str(sys.argv[2])
    seed_set_file = str(sys.argv[4])
    diffusion_model = str(sys.argv[6])
    time_budget = int(sys.argv[8])
    seed_set = []
    V = E = 0
    adj_graph = None
    rev_adj_graph = None

    with open(social_network) as file:
        for line in file:
            line = line.rstrip()
            if len(line.split(' ')) == 2:
                V = int(line.split(' ')[0])
                E = int(line.split(' ')[1])
                adj_graph = [[] for _ in range(V + 1)]
                rev_adj_graph = [[] for _ in range(V + 1)]
            else:
                start_v = int(line.split(' ')[0])
                end_v = int(line.split(' ')[1])
                prob = float(line.split(' ')[2])
                adj_graph[start_v].append((end_v, prob))
                rev_adj_graph[end_v].append((start_v, prob))
    with open(seed_set_file) as file:
        for line in file.readlines():
            line = line.rstrip()
            seed_set.append(int(line))

    worker = []
    worker_num = 8
    create_worker(worker_num)
    real_total_num = 0
    for i in range(worker_num):
        real_total_num += worker[i].outQ.get()  # 用同样的规则取回结果， 如果任务尚未完成，此处会阻塞等待子进程完成任务
    print(real_total_num / 10000)

    print(time.time() - start_time)

    sys.stdout.flush()
    os._exit(0)
