import argparse
import time
import numpy as np
import random
import sys
from submodule import IC, LT, utils

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

DIFFUSION_MODEL = utils.model_adapter(DIFFUSION_MODEL)
print(utils.count(graph, seed, min(int(500000/INFO['node']),1000), DIFFUSION_MODEL))

