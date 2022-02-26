import numpy as np
from edges import Edge
from graphs import Graph
from dijkstra import Dijkstra
from random import randint
import time

start = time.time()



# def read_map(file_name):
info = np.zeros(7)
f = open('./CARP_samples/gdb1.dat')
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
td = 0

for i in range(9, REQUIRED_EDGES + NON_REQUIRED_EDGES + 9):
    G.add_edge(Edge(int(lines[i].strip().split()[0]),
                    int(lines[i].strip().split()[1]),
                    int(lines[i].strip().split()[2]),
                    int(lines[i].strip().split()[3])))
    td += int(lines[i].strip().split()[3])

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


def initialization():
    INIT_R = []
    INIT_COST = []
    INIT_LOAD = []

    for i in range(1):
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
                if not task:
                    break
                for u in task:
                    if load + G[u[0]][u[1]].demand <= CAPACITY:
                        if shortestPath[current][u[0]] < d:
                            d = shortestPath[current][u[0]]
                            current_task = u
                        elif shortestPath[current][u[0]] == d:
                            d = shortestPath[current][u[0]]
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


def initialization1():
    INIT_R = []
    INIT_COST = []
    INIT_LOAD = []

    for i in range(1):
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




INIT_R, INIT_COST, INIT_LOAD = initialization()
INIT_R1, INIT_COST1, INIT_LOAD1 = initialization1()
INIT_R2, INIT_COST2, INIT_LOAD2, COST_GRAPH, alpha = initialization_v3(1)
print(INIT_COST)
print(INIT_LOAD)
print(INIT_R)
print(len(INIT_COST))
print(sum(INIT_COST))
print(sum(INIT_LOAD))

print(len(INIT_COST1))
print(INIT_COST1)
print(INIT_LOAD1)
print(sum(INIT_COST1))
print(sum(INIT_LOAD1))

print(INIT_COST2)
print(INIT_LOAD2)
#print(INIT_R)
print(len(INIT_COST2))
print(sum(INIT_COST2))
print(sum(INIT_LOAD2))

initial = time.time() - initial
run_time = time.time() - start
print(initial)
print(run_time)



