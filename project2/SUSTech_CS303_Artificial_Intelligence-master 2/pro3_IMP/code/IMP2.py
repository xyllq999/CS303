import argparse
import time
import numpy as np
import random
import sys, os, signal
import threading
from multiprocessing import Pool
from submodule import IC, LT, CELF, utils

def IMP():
    result = []
    global pool
    global seed
    cursor = int(10000/INFO['node'])+1
    precision = [1,10,20,50,80,100,200,300,500,800]
    for i  in range(10):
        if precision[i] <= cursor:
            result.append(pool.apply_async(CELF.CELF,
                    args=(graph, SEED_SET_SIZE, DIFFUSION_MODEL, precision[i],)))
    c = 0
    while 1:
        for res in result:
            if res.get():
                new_c = utils.count(graph, res.get(), 200, DIFFUSION_MODEL)
                if new_c > c:
                    seed = res.get()
                    c = new_c
                else:
                    end()

def output():
    for s in seed:
        print(s+1)

def end():
    output()
    global pool
    pool.terminate()
    pool.close()
    pool.join()  
    os._exit(0) 

def time_checker():
    while 1:
        if time.time()-start > TERMINATION-5:
            # print(time.time()-start)
            end()

# parse args
parser = argparse.ArgumentParser()
parser.add_argument('-i', help="Absolute path of the social network file.")
parser.add_argument('-k', type=int, help="Predefined size of the seed set.")
parser.add_argument('-m', help="Diffusion model, can only be IC or LT.")
parser.add_argument('-t', type=int, help="Time budget, the range is [60, 120].")
args = parser.parse_args()

NETWORK_FILE_PATH = args.i
SEED_SET_SIZE = args.k
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

seed = set()
pool = Pool(processes=8)
# manage time
start = time.time()
t1 = threading.Thread(target=time_checker, name='TimeChecker')
t2 = threading.Thread(target=IMP, name='IMP')
t1.start()
t2.start()
t2.join()
t1.join()




