import numpy as np
import sys

def extract_min(dis, S):
    for i in S:
        dis[i] = sys.maxsize
    return np.argmin(dis)

def dijkstra(cost, start_point):
    dis = np.ones(len(cost), dtype=int) * sys.maxsize
    # previous vertex
    previous = np.zeros(len(cost), dtype=int)
    dis[start_point] = 0
    previous[start_point] = start_point
    # set of all vertices
    S = set()
    Q = set(range(len(cost)))
    u = start_point
    while True:
        S.add(u)
        Q.remove(u)
        if not Q:
            break
        for i in Q:
            if cost[i,u] != 0 and cost[i,u]+dis[u] < dis[i]:
                dis[i] = cost[i,u]+dis[u]
                previous[i] = u
        k = extract_min(dis.copy(), S)
        previous[k] = u
        u = k
    return dis, previous

        