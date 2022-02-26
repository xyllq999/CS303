import sys
import random
import time


def sample(p):
    return p > random.uniform(0.0, 1.0)


def ic_process():
    activity_set = seed_set
    count = len(activity_set)
    active = [False for i in range(V + 1)]
    for _ in activity_set:
        active[_] = True
    while not len(activity_set) == 0:
        new_activity_set = []
        for seed in activity_set:
            for neighbor in adj_graph[seed]:
                if not active[neighbor[0]] and sample(neighbor[1]):
                    new_activity_set.append(neighbor[0])
                    active[neighbor[0]] = True
        count = count + len(new_activity_set)
        activity_set = new_activity_set
    return count


def lt_process():
    activity_set = seed_set
    thres = [0.0 for i in range(V + 1)]
    active = [False for i in range(V + 1)]
    for i in range(1, V + 1):
        thres[i] = random.uniform(0.0, 1.0)
        if thres[i] == 0.0 and len(rev_adj_graph[i]) != 0:
            activity_set.append(i)
    for _ in activity_set:
        active[_] = True
    count = len(activity_set)
    while not len(activity_set) == 0:
        new_activity_set = []
        for seed in activity_set:
            for neighbor in adj_graph[seed]:
                if not active[neighbor[0]]:
                    w_total = 0.0
                    for rev_neighbor in rev_adj_graph[neighbor[0]]:
                        if active[rev_neighbor[0]]:
                            w_total += rev_neighbor[1]
                    if w_total >= thres[neighbor[0]]:
                        active[neighbor[0]] = True
                        new_activity_set.append(neighbor[0])
        count = count + len(new_activity_set)
        activity_set = new_activity_set
    return count


if __name__ == '__main__':
    start_time = time.time()
    social_network = str(sys.argv[2])
    seed_set_file = str(sys.argv[4])
    diffusion_model = str(sys.argv[6])
    time_budget = int(sys.argv[8])
    V = E = 0
    adj_graph = None
    rev_adj_graph = None
    seed_set = []
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
    # print(adj_graph)
    with open(seed_set_file) as file:
        for line in file.readlines():
            line = line.rstrip()
            seed_set.append(int(line))
    # print(seed_set)
    if diffusion_model == 'IC':
        total_num = 0
        for i in range(10000):
            total_num += ic_process()
        print(total_num / 10000)
    else:
        total_num = 0
        for i in range(10000):
            total_num += lt_process()
        print(total_num / 10000)
    # print(time.time() - start_time)
