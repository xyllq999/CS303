import numpy as np
import random

# This program is to estimate the influence,
# and output the value of the estimated influence spread.

# When a node 𝑢 gets activated, initially or by another node,
# it has a single chance to activate each inactive i 𝑣 
# with the probability proportional to the edge weight 𝑤(𝑢, 𝑣).
# Afterwards, the activated nodes remain its active state 
# but they have no contribution in later activations.

def IC(graph, seed):
    activated = seed.copy()
    activity = seed.copy()
    while activity:
        new_activity = set()
        for node in activity:
            neighbors = np.nonzero(graph[node])[0]
            for i in neighbors:
                if graph[node,i] > random.random()\
                   and i not in activated:
                    activated.add(i)
                    new_activity.add(i)
        activity = new_activity.copy()
    count = len(activated)   
    return count