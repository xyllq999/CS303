import random
import sys
from . import IC
from . import LT

def count(graph, seed, k, model):
    count = 0
    if model == 1:
        for i in range(k):
            count += IC.IC(graph, seed)
    else:
        for i in range(k):
            count += LT.LT(graph, seed)
    count /= k
    # print("ISE:", count)
    return count

def model_adapter(DIFFUSION_MODEL):
    if DIFFUSION_MODEL == 'IC':
        DIFFUSION_MODEL = 1
    elif DIFFUSION_MODEL == 'LT':
        DIFFUSION_MODEL = 0
    else:
        print("Diffusion model, can only be IC or LT.")
        exit(0)
    return DIFFUSION_MODEL