import argparse
import time
import numpy as np
from submodule import dijkstra
from submodule import path_scanning

TERMINATION = 0
RANDOM_SEED = 0
FILE_PATH = ""

INFO = {}
graph = np.zeros((0,0))

# parse args
parser = argparse.ArgumentParser()
parser.add_argument('file')
parser.add_argument('-t', type=int)
parser.add_argument('-s', type=int)
args = parser.parse_args()
try:
    TERMINATION = args.t
    RANDOM_SEED = args.s
    FILE_PATH = args.file
except ValueError:
    print("ValueError:")
    print("args have to be int")

# read file
with open(FILE_PATH, 'r') as f:
    lines = f.readlines()
    INFO[lines[0].split()[0]] = lines[0].split()[-1]
    for l in lines[1:8]:
        l = l.split(":")
        INFO[l[0].strip()] = int(l[-1])
    gra_cost = np.zeros((INFO['VERTICES'],INFO['VERTICES']),dtype=int)
    gra_demand = np.zeros((INFO['VERTICES'],INFO['VERTICES']), dtype=int)
    for l in lines[9:len(lines)-1]:
        l = list(map(int, l.split()))
        # cost, there is no edge if cost = 0
        gra_cost[l[0]-1, l[1]-1] = l[2]
        gra_cost[l[1]-1, l[0]-1] = l[2]
        # demand, some edges' demand = 0
        gra_demand[l[0]-1, l[1]-1] = l[3]
        gra_demand[l[1]-1, l[0]-1] = l[3]

dis = np.zeros((INFO['VERTICES'],INFO['VERTICES']),dtype=int)
previous = np.zeros((INFO['VERTICES'],INFO['VERTICES']),dtype=int)
for i in range(INFO['VERTICES']):
    dis[i], previous[i] = dijkstra.dijkstra(gra_cost, i)
    
R, q = path_scanning.initial(gra_cost, gra_demand, INFO['DEPOT']-1, INFO['CAPACITY'], dis, RANDOM_SEED)
print("s",end=' ')
string = str(R).replace(" ", "").replace("[[","[").replace("]]","]")\
                .replace("[", "0,").replace("]",",0")
print(string)
print("q", q)
# count time
# start = int(time.time())
# while True:
#     pass
#     run_time = (int(time.time())-start)
#     if run_time >= TERMINATION:
#         break
