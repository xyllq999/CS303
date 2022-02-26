import numpy as np
from edges import Edge
from graphs import Graph
from dijkstra import Dijkstra
from random import randint
import time
import re
from multiprocessing import Pool
import random
import copy
start = time.time()

f = open('./C01.dat')
lines = f.readlines()

VERTICES = int(lines[2].strip().split()[-1])
DEPOT = 1
REQUIRED_EDGES = int(lines[3].strip().split()[-1])
NON_REQUIRED_EDGES = int(lines[4].strip().split()[-1])
VEHICLES = int(lines[5].strip().split()[-1])
CAPACITY = int(lines[6].strip().split()[-1])
TOTAL_COST_OF_REQUIRED_EDGES = int(lines[8].strip().split()[-1])
f.close()

G = Graph(n=VERTICES, directed=False)
td = 0

for i in range(10, REQUIRED_EDGES + 10):
    _ = re.split('[( , ) coste demanda \r\n]', lines[i])
    _ = filter(lambda x: x != '', _)
    td += int(_[3])
    G.add_edge(Edge(int(_[0]), int(_[1]), int(_[2]), int(_[3])))
for i in range(11 + REQUIRED_EDGES, 11 + REQUIRED_EDGES + NON_REQUIRED_EDGES):
    _ = re.split('[( , ) coste \r\n]', lines[i])
    _ = filter(lambda x: x != '', _)
    G.add_edge(Edge(int(_[0]), int(_[1]), int(_[2])))

'''
# def read_map(file_name):
info = np.zeros(7)
f = open('./CARP_samples/egl-s1-A.dat')
lines = f.readlines()

# Read map info to numpy array info

for i in range(1, 8):
    info[i-1] = lines[i].strip().split()[-1]
f.close()
info = info.astype(int)
info = info.tolist()
print(info)

VERTICES = info[0]
DEPOT = info[1]
REQUIRED_EDGES = info[2]
NON_REQUIRED_EDGES = info[3]
VEHICLES = info[4]
CAPACITY = info[5]
TOTAL_COST_OF_REQUIRED_EDGES = info[6]
# Build the graph
G = Graph(n=VERTICES, directed=False)

for i in range(9, REQUIRED_EDGES + NON_REQUIRED_EDGES + 9):
    G.add_edge(Edge(int(lines[i].strip().split()[0]),
                    int(lines[i].strip().split()[1]),
                    int(lines[i].strip().split()[2]),
                    int(lines[i].strip().split()[3])))
'''

# Initialize a shortest path matrix
shortestPath = np.zeros((VERTICES + 1, VERTICES + 1))
shortestPath = np.int_(shortestPath)
for i in range(1, VERTICES+1):
    algorithm = Dijkstra(G)
    algorithm.run(i)
    for j in range(i, VERTICES+1):
        shortestPath[i][j] = algorithm.distance[j]
shortestPath = np.maximum(shortestPath, shortestPath.transpose())
shortestPath = shortestPath.tolist()

initial = time.time()



def initialization_v1():
    INIT_R = []
    INIT_COST = []
    INIT_LOAD = []
    avg_demand = td / REQUIRED_EDGES

    for i in range(100):
        # Tasks and inverse tasks
        free = list([e.source, e.target] for e in G.iteredges() if e.demand != 0)
        free_inv = list([e.target, e.source] for e in G.iteredges() if e.demand != 0)
        task = free + free_inv
        R = []
        COST = []
        LOAD = []
        while True:
            route = []
            load = 0
            cost = 0
            current = DEPOT
            while True:
                d = np.inf
                for u in task:
                    if shortestPath[current][u[0]] < d:
                        if load + G[u[0]][u[1]].demand <= CAPACITY:
                            d = shortestPath[current][u[0]]
                            current_task = u
                    elif shortestPath[current][u[0]] == d:
                        if load + G[u[0]][u[1]].demand <= CAPACITY:
                            rand = randint(0, 1)
                            if rand == 0:
                                current_task = u
                if d != np.inf:
                    route.append(current_task)
                    task.remove(current_task)
                    task.remove(current_task[::-1])
                    load += G[current_task[0]][current_task[1]].demand
                    cost += G[current_task[0]][current_task[1]].cost + d
                    current = current_task[1]
                if not task or d == np.inf:
                    break
            cost += shortestPath[current][DEPOT]
            R.append(route)
            LOAD.append(load)
            COST.append(cost)
            if not task:
                break
        if sum(INIT_COST) == 0 or sum(COST) <= sum(INIT_COST):
            INIT_R = R
            INIT_COST = COST
            INIT_LOAD = LOAD

    return INIT_R, INIT_COST, INIT_LOAD


def initialization_v2():
    INIT_R = []
    INIT_COST = []
    INIT_LOAD = []
    avg_demand = td / REQUIRED_EDGES

    for i in range(1000):
        # Tasks and inverse tasks
        free = list([e.source, e.target] for e in G.iteredges() if e.demand != 0)
        free_inv = list([e.target, e.source] for e in G.iteredges() if e.demand != 0)
        task = free + free_inv
        R = []
        COST = []
        LOAD = []
        alpha = 1
        while True:
            route = []
            load = 0
            cost = 0
            current = DEPOT
            while True:
                d = np.inf
                candidate = np.inf
                candidates = []
                flag = False
                for u in task:
                    if shortestPath[current][u[0]] < candidate:
                        candidate = shortestPath[current][u[0]]
                        candidates = [u]
                    elif shortestPath[current][u[0]] == candidate:
                        candidates.append(u)
                for u in candidates:
                    if load + G[u[0]][u[1]].demand > CAPACITY:
                        flag = False
                    else:
                        flag = True
                        break
                if flag:
                    for u in task:
                        if shortestPath[current][u[0]] < d:
                            if load + G[u[0]][u[1]].demand <= CAPACITY:
                                d = shortestPath[current][u[0]]
                                current_task = u
                        elif shortestPath[current][u[0]] == d:
                            if load + G[u[0]][u[1]].demand <= CAPACITY:
                                rand = randint(0, 1)
                                if rand == 0:
                                    current_task = u
                    if d != np.inf:
                        route.append(current_task)
                        task.remove(current_task)
                        task.remove(current_task[::-1])
                        load += G[current_task[0]][current_task[1]].demand
                        cost += G[current_task[0]][current_task[1]].cost + d
                        current = current_task[1]
                    if not task or d == np.inf:
                        break
                else:
                    break
            cost += shortestPath[current][DEPOT]
            R.append(route)
            LOAD.append(load)
            COST.append(cost)
            if not task:
                break
        if sum(INIT_COST) == 0 or sum(COST) <= sum(INIT_COST):
            INIT_R = R
            INIT_COST = COST
            INIT_LOAD = LOAD

    return INIT_R, INIT_COST, INIT_LOAD


def initialization_v3(alpha):
    INIT_R = []
    INIT_COST = []
    INIT_LOAD = []
    COST_GRAPH = []
    avg_demand = td / REQUIRED_EDGES
    avg_cost_on_demand = TOTAL_COST_OF_REQUIRED_EDGES / REQUIRED_EDGES
    free = []
    free_inv = []
    for e in G.iteredges():
        if e.demand != 0:
            free.append([e.source, e.target])
            free_inv.append([e.target, e.source])
    #free = list([e.source, e.target] for e in G.iteredges() if e.demand != 0)
    #free_inv = [x[::-1] for x in free]
    all_task = free + free_inv
    for i in range(1):
        # Tasks and inverse tasks
        task = all_task[:]
        R = []
        COST = []
        LOAD = []
        while True:
            route = []
            load = 0
            cost = 0
            current = DEPOT
            while True:
                d = np.inf
                candidate = np.inf
                candidates = []
                flag = False
                for u in task:
                    if CAPACITY - load > alpha * avg_demand:
                        if shortestPath[current][u[0]] < candidate:
                            candidate = shortestPath[current][u[0]]
                            candidates = [u]
                        elif shortestPath[current][u[0]] == candidate:
                            candidates.append(u)
                    else:
                        if shortestPath[current][u[0]] + shortestPath[u[0]][u[1]] + shortestPath[u[1]][DEPOT] <= avg_cost_on_demand + shortestPath[u[0]][DEPOT]:
                            if shortestPath[current][u[0]] < candidate:
                                candidate = shortestPath[current][u[0]]
                                candidates = [u]
                            elif shortestPath[current][u[0]] == candidate:
                                candidates.append(u)
                if not candidates:
                    break
                for u in candidates:
                    if load + G[u[0]][u[1]].demand > CAPACITY:
                        flag = False
                    else:
                        flag = True
                        break
                if flag:
                    for u in task:
                        if shortestPath[current][u[0]] < d:
                            if load + G[u[0]][u[1]].demand <= CAPACITY:
                                d = shortestPath[current][u[0]]
                                current_task = u
                        elif shortestPath[current][u[0]] == d:
                            if load + G[u[0]][u[1]].demand <= CAPACITY:
                                rand = randint(0, 1)
                                if rand == 0:
                                    current_task = u
                    if d != np.inf:
                        route.append(current_task)
                        task.remove(current_task)
                        task.remove(current_task[::-1])
                        load += G[current_task[0]][current_task[1]].demand
                        cost += G[current_task[0]][current_task[1]].cost + d
                        current = current_task[1]
                    if not task or d == np.inf:
                        break
                else:
                    break
            cost += shortestPath[current][DEPOT]
            R.append(route)
            LOAD.append(load)
            COST.append(cost)
            if not task:
                break
        if sum(INIT_COST) == 0 or sum(COST) <= sum(INIT_COST):
            INIT_R = R
            INIT_COST = COST
            INIT_LOAD = LOAD
        COST_GRAPH.append(sum(INIT_COST))
    return INIT_R, INIT_COST, INIT_LOAD, COST_GRAPH, alpha


def copy_partition(routes):
    new_routes = []
    for route in routes:
        new_route = []
        for task in route:
            new_route.append(task)
        new_routes.append(new_route)
    return new_routes


def calculate_cost(routes):
    cost = 0
    last = DEPOT
    for route in routes:
        for task in route:
            cost += G[task[0]][task[1]].cost + shortestPath[last][task[0]]
            last = task[1]
        cost += shortestPath[last][DEPOT]
        last = DEPOT
    return cost


def feasible(routes):
    for route in routes:
        load = 0
        for task in route:
            load += G[task[0]][task[1]].demand
        if load > CAPACITY:
            return False
    return True


def neighborhood(routes):
    solution = copy.deepcopy(routes[:])
    choice_1 = single_insertion(solution)
    choice_2 = double_insertion(solution)
    #choice_3 = swap(solution)
    choice = random.randint(0, 1)
    if not choice_1:
        return routes
    if not choice_2:
        choice = 0
    remain = []
    for route in solution:
        current = CAPACITY
        for task in route:
            current -= G[task[0]][task[1]].demand
        remain.append(current)
    val_remain = []

    if choice == 0:
        which = random.randint(0, len(choice_1) - 1)
        allowed_values = list(range(0, len(choice_1)))
        allowed_values.remove(which)
        #allowed_choices = choice_1[:]
        #allowed_choices.pop(which)
        where = random.choice(allowed_values)
        ''''# calculate where
        for task in allowed_choices:
            val_remain.append(remain[task[0]])
        possibility = random.randint(0, 2)
        if possibility == 0:
            val_remain.pop(np.argmax(val_remain))
            where = remain.index(max(val_remain))
        else:
            where = remain.index(max(val_remain))
        where = remain.index(max(val_remain))'''
        temp = solution[choice_1[which][0]][choice_1[which][1]][:]
        solution[choice_1[which][0]].pop(choice_1[which][1])
        flip = random.randint(0, 1)
        if flip == 0:
            solution[choice_1[where][0]].insert(choice_1[where][1], temp)
        else:
            solution[choice_1[where][0]].insert(choice_1[where][1], temp[::-1])
        return solution
    elif choice == 1:
        which = random.randint(0, len(choice_2) - 1)
        allowed_values = list(range(0, len(choice_1)))
        where = random.choice(allowed_values)
        '''allowed_choices = choice_1[:]
        for task in allowed_choices:
            val_remain.append(remain[task[0]])
        possibility = random.randint(0, 2)
        if possibility == 0:
            val_remain.pop(np.argmax(val_remain))
            where = remain.index(max(val_remain))
        else:
            where = remain.index(max(val_remain))'''
        temp1 = solution[choice_2[which][0]][choice_2[which][1]][:]
        temp2 = solution[choice_2[which][0]][choice_2[which][1] + 1][:]
        del solution[choice_2[which][0]][choice_2[which][1]]
        del solution[choice_2[which][0]][choice_2[which][1]]
        flip = random.randint(0, 1)
        if flip == 0:
            solution[choice_1[where][0]].insert(choice_1[where][1], temp1)
            solution[choice_1[where][0]].insert(choice_1[where][1] + 1, temp2)
        else:
            solution[choice_1[where][0]].insert(choice_1[where][1], temp2[::-1])
            solution[choice_1[where][0]].insert(choice_1[where][1] + 1, temp1[::-1])
        return solution


def single_insertion(routes):
    candidates = []
    i = 0
    for route in routes:
        last = DEPOT
        j = 0
        for task in route:
            if j != len(route) - 1:
                if last != task[0] and task[1] != route[j + 1][0]:
                    candidates.append([i, j])
            else:
                if last != task[0] and task[1] != DEPOT:
                    candidates.append([i, j])
            last = task[1]
            j += 1
        i += 1
    return candidates


def double_insertion(routes):
    candidates = []
    i = 0
    for route in routes:
        last = DEPOT
        j = 0
        for task in route:
            if j < len(route) - 2:
                if last != task[0] and task[1] == route[j + 1][0] and route[j+1][1] != route[j+2][0]:
                    candidates.append([i, j])
            elif j == len(route) - 2:
                if last != task[0] and route[j+1][1] != DEPOT:
                    candidates.append([i, j])
            last = task[1]
            j += 1
        i += 1
    return candidates


def swap(routes):
    candidates = []
    return candidates


def TSA(solution, INIT_COST):
    '''
    f_s = calculate_cost(solution)
    best_solution = solution
    if feasible(solution):
        best_feasible_solution = solution
    else:
        fsbf = np.inf
    k = 0
    k_b = 0
    k_l = 8 * REQUIRED_EDGES
    k_bf = 0
    k_f = 0
    k_i = 0
    k_bt = 0
    tabu_list = []
    t = REQUIRED_EDGES / 2
    frequency_si = 1
    frequency_di = 5
    frequency_swap = 5
    p = 1
    '''
    neighborhood(solution)





'''
INIT_R, INIT_COST, INIT_LOAD = initialization_v1()
INIT_R1, INIT_COST1, INIT_LOAD1 = initialization_v2()
INIT_R2, INIT_COST2, INIT_LOAD2, COST_GRAPH2 = initialization_v2(1)
'''
results = Pool(4).map(initialization_v3, np.linspace(0.5, 2.9, num=4))
best_init_cost = np.inf
index = -1
for i in range(4):
    if best_init_cost > sum(results[i][1]):
        best_init_cost = sum(results[i][1])
        index = i
INIT_R = results[index][0]
INIT_COST = results[index][1]
INIT_LOAD = results[index][2]
COST_GRAPH = results[index][3]
alpha = results[index][4]
print(INIT_R)
print('INIT_COST: ' + str(INIT_COST))
print('INIT_LOAD: ' + str(INIT_LOAD))
print('CAR_NUM: ' + str(len(INIT_COST)))
print('INIT_COST: ' + str(sum(INIT_COST)))
print('INIT_LOAD: ' + str(sum(INIT_LOAD)))
print('alpha: ' + str(alpha))
print('COST_GRAPH: ' + str(COST_GRAPH))

OPT_COST = sum(INIT_COST)
OPT_R = INIT_R
for i in range(100000):
    solution = neighborhood(INIT_R)
    if calculate_cost(solution) < OPT_COST:
        if feasible(solution):
            OPT_R = solution
            OPT_COST = calculate_cost(solution)
            print(OPT_R)
            print(OPT_COST)


initial = time.time() - initial
run_time = time.time() - start
print(initial)
print(run_time)
