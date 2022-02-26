import numpy as np
import sys
import random

def initial(cost, demand, depot, capacity, dis, seed):
    R = 0
    q = sys.maxsize
    for i in range(7):
        tmp_R, tmp_q = initial_method(cost, demand, depot, capacity, dis, seed, i)
        print(i, tmp_q)
        if tmp_q < q:
            R = tmp_R
            q = tmp_q
    return R,q

def initial_method(cost, demand, depot, capacity, dis, seed, method):
    q = 0
    random.seed(seed)
    # print(demand)
    free = np.where(demand != 0)
    free = list(zip(free[0],free[1]))
    R = []
    temp = []
    t = depot
    c = capacity
    candidates = set()
    while free:
        candidates.clear()
        for f in free:
            if demand[f[0],f[1]] <= c:
                candidates.add(f)
        if c<=0 or not candidates:
            # back to depot
            R.append(temp)
            q += dis[t, depot]
            t = depot
            c = capacity
            temp = []
            continue
        min_dis = sys.maxsize
        coor = (0,0)
        for can in candidates:
            if dis[t,can[0]] < min_dis:
                coor = can
                min_dis = dis[t,coor[0]]
            elif dis[t,can[0]] == min_dis and method != 0:
                # random
                if (method == 1 and random.randrange(2))\
                or (method == 2 and dis[can[1],depot]>dis[coor[1],depot])\
                or (method == 3 and dis[can[1],depot]<dis[coor[1],depot])\
                or (method == 4 and demand[can[0],can[1]]/cost[can[0],can[1]] > demand[coor[0],coor[1]]/cost[coor[0],coor[1]])\
                or (method == 5 and demand[can[0],can[1]]/cost[can[0],can[1]] < demand[coor[0],coor[1]]/cost[coor[0],coor[1]]):
                    coor = can
                elif method == 6:
                    # rule 5
                    if c < capacity/2 and dis[can[1],depot]>dis[coor[1],depot]:
                        coor = can
                    elif dis[can[1],depot]<dis[coor[1],depot]:
                        coor = can
        temp.append((coor[0]+1,coor[1]+1))
        c -= demand[coor[0],coor[1]]
        free.remove(coor)
        free.remove((coor[1],coor[0]))
        q += dis[t,coor[0]]+cost[coor[0],coor[1]]
        t = coor[1]
    R.append(temp)
    q += dis[t, depot]
    # for round in R:
    #     t = depot
    #     for point in round:
    #         q += dis[t, point[0]-1] + cost[point[0]-1,point[1]-1]
    #         t = point[1]-1
    #     q += dis[round[-1][1]-1, depot]
    return R,q


