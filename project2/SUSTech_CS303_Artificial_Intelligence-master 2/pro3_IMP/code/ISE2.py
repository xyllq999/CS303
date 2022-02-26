import argparse
import time
import numpy as np
import random
import threading
import sys
from submodule import IC, LT, utils
from multiprocessing import Pool

def ISE():
    global result
    global pool
    global seed
    global ct
    precision = [10,50,100,500,1000,5000,10000]
    dobber = 200000/INFO['node']
    for i  in range(7):
        if i < dobber:
            result.append(pool.apply_async(utils.count,
                    args=(graph, seed, precision[i], DIFFUSION_MODEL,)))
    while 1:
        for res in result:
            if res.get():
                new_ct = res.get()
                if abs(new_ct - ct) < INFO['node']/100:
                    end()
                    return
                else:
                    ct = new_ct

def time_checker():
    while 1:
        if time.time()-start > TERMINATION-5:
            # print(time.time()-start)
            end()
            return

def output():
    print(ct)

def end():
    global result
    global pool
    pool.terminate()
    pool.close()
    pool.join() 
    sys.stdout.flush()

start = time.time()

# parse args
parser = argparse.ArgumentParser()
parser.add_argument('-i', help="Absolute path of the social network file.")
parser.add_argument('-s', help="Absolute path of the seed set file.")
parser.add_argument('-m', help="Diffusion model, can only be IC or LT.")
parser.add_argument('-t', type=int, help="Time budget, the range is [60, 120].")
args = parser.parse_args()

NETWORK_FILE_PATH = args.i
SEED_SET_PATH = args.s
DIFFUSION_MODEL = args.m
TERMINATION = args.t
INFO = {}

# read file
with open(NETWORK_FILE_PATH, 'r') as f:
    lines = f.readlines()
    info = lines[0].split()
    INFO['node'] = int(info[0])
    INFO['edge'] = int(info[1])
    graph = np.zeros((INFO['node'],INFO['node']))
    for l in lines[1:]:
        l = l.split()
        graph[int(l[0])-1, int(l[1])-1] = float(l[2])

with open(SEED_SET_PATH, 'r') as f:
    lines = f.readlines()
    seed = set()
    for l in lines:
        seed.add(int(l)-1)
    INFO['seed'] = seed

ct = 0
result = []
pool = Pool(processes=4)
# manage time
start = time.time()
t1 = threading.Thread(target=time_checker, name='TimeChecker')
t2 = threading.Thread(target=ISE, name='ISE')
t1.start()
t2.start()
t2.join()
t1.join()
output()


