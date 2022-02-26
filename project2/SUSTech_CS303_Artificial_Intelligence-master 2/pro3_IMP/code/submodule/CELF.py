import numpy as np
import random
import sys
from . import IC
from . import LT


# Marginal influence
def influence(graph, current_seed, model, precision):
    infs = 0
    if model:
        for i in range(precision):
            infs += IC.IC(graph, current_seed)
    else:
        for i in range(precision):
            infs += LT.LT(graph, current_seed)
    infs = infs/precision
    return infs

def CELF(graph, size, model, precision):
    seed = set()
    queue = {}
    current_influence = 0
    # initial 
    for s in range(len(graph)):
        if np.any(graph[s]):
            queue[s] = sys.maxsize
    while size > 0:
        flag = (0, 0)
        i = 0
        new_queue = sorted(queue.items(), key=lambda d: d[1], reverse=True)
        while i < len(new_queue) and new_queue[i][1] > flag[1]:
            s = new_queue[i][0]
            seed.add(s)
            infs = influence(graph, seed, model, precision) - current_influence
            seed.remove(s)
            queue[s] = infs
            if infs > flag[1]:
                flag = (s, infs)
            i += 1
        seed.add(flag[0])
        current_influence = influence(graph, seed, model, precision)
        del queue[flag[0]]
        size -= 1
    return seed