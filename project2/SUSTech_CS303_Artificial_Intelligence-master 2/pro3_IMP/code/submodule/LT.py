import numpy as np
import random

# At the beginning, each node 𝑣 selects a random threshold 𝜃𝑣
# uniformly at random in range [0,1].
# If round 𝑡 ≥ 1, an inactive node 𝑣 becomes activated
# if for all activated is u, ∑𝑤(𝑢, 𝑣) ≥ 𝜃𝑣.

def LT(graph,seed):
    activated = seed.copy()
    threshold = {}
    for node in range(len(graph)):
        threshold[node] = random.random()
        if threshold[node] == 0:
            activated.add(node)
    activity = activated.copy()
    while activity:
        new_activity = set()
        for node in activity:
            neighbors = np.nonzero(graph[node])[0]
            for i in neighbors:
                if i not in activated:
                    source_neighbors = np.nonzero(graph[:,i])[0]
                    weight = 0
                    for n in source_neighbors:
                        if n in activated:
                            weight += graph[n, i]
                    if weight > threshold[i]:
                        activated.add(i)
                        new_activity.add(i)
        activity = new_activity.copy()
    count = len(activated)    
    return count