import argparse
import time
import numpy as np
import random
import sys, os, signal
from submodule import IC, LT, CELF, utils

def output():
    for s in seed:
        print(s+1)

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

DIFFUSION_MODEL = utils.model_adapter(DIFFUSION_MODEL)
precision = min(int(10000/INFO['node'])+1,100)

seed = CELF.CELF(graph, SEED_SET_SIZE, DIFFUSION_MODEL, precision)

output()
# print("ISE:",utils.count(graph,seed,100,DIFFUSION_MODEL))


