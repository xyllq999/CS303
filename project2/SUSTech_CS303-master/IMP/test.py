from invgraph import Graph
from graph import pGraph
import random
import multiprocessing as mp
import time
import getopt
import sys
import math
import ISE
from array import array


class Worker(mp.Process):
    def __init__(self, outQ, theta):
        super(Worker, self).__init__(target=self.start)
        self.outQ = outQ
        self.R = []
        self.theta = theta
        self.count = 0

    def run(self):
        while self.count < self.theta:
            v = random.randint(1, node_num)
            rr = generate_rr(v)
            self.R.append(rr)
            self.count += 1
        self.outQ.put(self.R)


def create_worker(num, task_num):
    """
        create processes
        :param num: process number
        :param task_num: the number of tasks assigned to each worker
    """
    global worker
    for i in range(num):
        # print(i)
        worker.append(Worker(mp.Queue(), task_num))
        worker[i].start()


def finish_worker():
    """
    关闭所有子进程
    :return:
    """
    for w in worker:
        w.terminate()


def sampling(epsoid, l):
    global graph, seed_size, worker
    R = []
    LB = 1
    n = node_num
    k = seed_size
    epsoid_p = epsoid * math.sqrt(2)
    for i in range(0, int(math.log2(n))):
        s = time.time()
        x = n/(math.pow(2, i))
        lambda_p = ((2+2*epsoid_p/3)*(logcnk(n, k) + l*math.log(n) + math.log(math.log2(n)))*n)/pow(epsoid_p, 2)
        theta = lambda_p/x
        # print(theta)
        # while len(R) <= theta:
        #     v = random.randint(1, n)
        #     rr = generate_rr(v)
        #     R.append(rr)
        worker_num = 8
        create_worker(worker_num, (theta-len(R))/8)
        for w in worker:
            R_list = w.outQ.get()
            R += R_list
        # finish_worker()
        worker = []
        end = time.time()
        # print('time to find rr', end - s)
        start = time.time()
        Si = node_selection(R, k)
        end = time.time()
        # print('node selection time', end - start)
        if n*F(R, Si) >= (1+epsoid_p)*x:
            LB = n*F(R, Si)/(1+epsoid_p)
            break
    alpha = math.sqrt(l*math.log(n) + math.log(2))
    beta = math.sqrt((1-1/math.e)*(logcnk(n, k)+l*math.log(n)+math.log(2)))
    lambda_aster = 2*n*pow(((1-1/math.e)*alpha + beta), 2)*pow(epsoid, -2)
    theta = lambda_aster / LB
    start = time.time()
    while len(R) <= theta:
        v = random.randint(1, n)
        rr = generate_rr(v)
        R.append(rr)
    end = time.time()
    # print(end - start)
    return R


def generate_rr(v):
    global model
    if model == 'IC':
        return generate_rr_ic(v)
    elif model == 'LT':
        return generate_rr_lt(v)

'''
def node_selection(R, k):
    Sk = set()
    rr_flag = {}
    max_point = -1
    for i in range(0, k):
        rr_degree = dict()
        for rr in R:
            t_rr = tuple(rr)
            if t_rr not in rr_flag:
                rr_flag[t_rr] = 1
            if max_point in rr:
                rr_flag[t_rr] = 0
            if not rr_flag[t_rr]:
                continue
            for rr_node in rr:
                if rr_node not in rr_degree:
                    rr_degree[rr_node] = 1
                else:
                    rr_degree[rr_node] += 1
        max_point = -1
        max_degree = 0
        for j in range(1, node_num + 1):
            if j in rr_degree and rr_degree[j] > max_degree:
                max_point = j
                max_degree = rr_degree[j]
        if max_point != -1:
            Sk.add(max_point)
            rr_degree[max_point] = 0
    return Sk
'''


def node_selection(R, k):
    Sk = set()
    # rr_flag = [1 for ii in range(0, 10000)]
    # rr_flag = array('b', (1 for i in range(10**6)))
    rr_flag = {}
    max_point = -1
    for i in range(0, k):
        rr_degree = [0 for ii in range(0, node_num+1)]
        for j in range(0, len(R)):
            rr = R[j]
            if j not in rr_flag:
                rr_flag[j] = 1
            if max_point in rr:
                rr_flag[j] = 0
            if not rr_flag[j]:
                continue
            for rr_node in rr:
                rr_degree[rr_node] += 1
        max_point = rr_degree.index(max(rr_degree))
        Sk.add(max_point)
    return Sk


def F(R, Si):
    matched_count = 0
    for rr in R:
        for s in Si:
            if s in rr:
                matched_count += 1
    return matched_count/len(R)

'''
def generate_rr_ic(node):
    # calculate reverse reachable set using IC model
    activity_set = list()
    active_nodes = list()
    activity_set.append(node)
    active_nodes.append(node)
    while activity_set:
        new_activity_set = list()
        for seed in activity_set:
            for _node, weight in graph.get_neighbors(seed):
                if _node not in active_nodes:
                    if random.random() < weight:
                        active_nodes.append(_node)
                        new_activity_set.append(_node)
        activity_set = new_activity_set
    return active_nodes
'''


def generate_rr_ic(node):
    # calculate reverse reachable set using IC model
    activity_set = set()
    activity_set.add(node)
    active_nodes = set()
    active_nodes.add(node)
    converged = False
    while not converged:
        new_activity_set = set()
        for seed in activity_set:
            for _node in set(graph.get_neighbors_keys(seed)) - active_nodes:
                weight = graph.network[seed][_node]
                if random.random() < weight:
                    active_nodes.add(_node)
                    new_activity_set.add(_node)
        activity_set = new_activity_set
        if not activity_set:
            converged = True
        active_nodes |= activity_set
    return active_nodes


def generate_rr_lt(node):
    # calculate reverse reachable set using LT model
    activity_set = list()
    activity_nodes = list()
    activity_set.append(node)
    activity_nodes.append(node)
    while activity_set:
        new_activity_set = list()
        for seed in activity_set:
            neighbors = graph.get_neighbors(seed)
            if len(neighbors) == 0:
                continue
            candidate = random.sample(neighbors, 1)[0][0]
            # print(candidate)
            if candidate not in activity_nodes:
                activity_nodes.append(candidate)
                new_activity_set.append(candidate)
        activity_set = new_activity_set
    return activity_nodes


def imm(epsoid, l):
    n = node_num
    k = seed_size
    l = l*(1+ math.log(2)/math.log(n))
    R = sampling(epsoid, l)
    Sk = node_selection(R, k)
    return Sk


def logcnk(n, k):
    res = 0
    for i in range(n-k+1, n+1):
        res += math.log(i)
    for i in range(1, k+1):
        res -= math.log(i)
    return res


def read_file(network):
    """
    read network file into a graph and read seed file into a list
    :param network: the file path of network
    """
    global node_num, edge_num, graph, seeds, pGraph
    data_lines = open(network, 'r').readlines()
    node_num = int(data_lines[0].split()[0])
    edge_num = int(data_lines[0].split()[1])

    for data_line in data_lines[1:]:
        start, end, weight = data_line.split()
        graph.add_edge(int(start), int(end), float(weight))
        pGraph.add_edge(int(start), int(end), float(weight))


if __name__ == "__main__":
    """
        define global variables:
        node_num: total number of nodes in the network
        edge_num: total number of edges in the network
        graph: represents the network
        seeds: the list of seeds
    """
    node_num = 0
    edge_num = 0
    graph = Graph()
    pGraph = pGraph()
    model = 'IC'
    """
    command line parameters
    """
    start = time.time()
    network_path = "test_data/NetHEPT.txt"
    model = 'IC'
    seed_size = 0
    termination = 10
    # start = time.time()
    opts, args = getopt.getopt(sys.argv[1:], 'i:k:m:t:')
    for opt, val in opts:
        if opt == '-i':
            network_path = val
        elif opt == '-k':
            seed_size = int(val)
        elif opt == '-m':
            model = val
        elif opt == '-t':
            termination = int(val)

    read_file(network_path)
    worker = []
    if node_num < 63:
        epsoid = 0.1
    else:
        epsoid = 0.1
    # print(epsoid)
    l = 1
    seeds = imm(epsoid, l)
    # print(seeds)

    for seed in seeds:
        print(seed)

    end = time.time()
    # print(end - start)

    # res = ISE.calculate_influence(seeds, model, pGraph)
    #
    # print(res)


