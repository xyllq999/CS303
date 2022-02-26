'''
Solver for CARP
'''
from collections import defaultdict
from itertools import tee, izip
import random
from random import shuffle
import copy
import os
from utils.digraph import DiGraph
from utils.graph import Graph
from multiprocessing import Process, Queue

MAX_ITERATION = 30
P_M = 0.1
PS_RANDOM = 10
PS = 1 + PS_RANDOM


class Solver(object):
    '''
    A solver class
    '''
    def __init__(self, graph, spec, seed, solution_receiver):
        self.solution_receiver = solution_receiver
        self.x_bsf = [None, float('inf')]
        self.gf = graph
        self.seed = seed
        self.capacity = int(spec['CAPACITY'])
        self.depot = int(spec['DEPOT'])
        if self.seed:
            random.seed(self.seed)

    def update_bsf(self, idv):
        '''
        get the new solution known to main process
        '''
        if self.x_bsf[1] > idv['fitness']:
            self.x_bsf = [idv['partition'], idv['fitness']]
            # print(idv['fitness'])
            self.solution_receiver.put(self.x_bsf)

    def main_iteration(self, P):
        '''
        iteration stop which can be restart
        '''
        n_iteration = 0
        while n_iteration < MAX_ITERATION:
            # print(n_iteration)
            if n_iteration > MAX_ITERATION*3/4:
                global P_M
                P_M = 0.4
            # step1: random select two parent
            idxa, idxb = random.sample(xrange(PS), 2)
            if P[idxa]['fitness'] < P[idxb]['fitness']:
                tmp, idxb = idxb, idxa
                idxa = tmp
            # step2: order crossover
            child = Solver.cxOrdered(
                P[idxa]['chromesome'], P[idxb]['chromesome'])
            child = random.choice(child)
            # step3: evaluation
            new_partition = self.chromesome_partition(child)
            quality = self.solution_verify(new_partition)
            new_idv = defaultdict(dict)
            new_idv['load'] = quality[0]
            new_idv['cost'] = quality[1]
            new_idv['fitness'] = quality[2]
            new_idv['partition'] = new_partition
            new_idv['chromesome'] = child
            # local search
            rnd = random.random()
            if rnd < P_M:
                new_idv = self.local_search(new_idv)
            # get better child
            # print("---------"+str(n_iteration))
            if new_idv['fitness'] < P[idxa]['fitness']:
                P[idxa] = new_idv
                self.update_bsf(new_idv)
                if child == P[idxb]['chromesome']:
                    self.mutation(P[idxa])
            n_iteration += 1
        return P

    def get_new_random_idv(self):
        idv = self.ps_to_idv(self.path_scanning())
        # idv = defaultdict(dict)
        # idv['partition'] = self.random_init()
        idv['partition'] = self.chromesome_partition(idv['chromesome'])
        quality = self.solution_verify(idv['partition'])
        idv['load'] = quality[0]
        idv['cost'] = quality[1]
        idv['fitness'] = quality[2]
        return idv

    def solve(self):
        '''
        Main entrance for the whole algorithm
        '''
        n_restart = 0
        # initilization
        init_solution2 = self.augment_merge()
        p_augment_merge = self.am_to_chromesome(init_solution2)

        P = defaultdict(dict)
        P[0]['chromesome'] = p_augment_merge
        P[0]['partition'] = self.chromesome_partition(p_augment_merge)
        p_augment_merge_quality = self.solution_verify(P[0]['partition'])
        P[0]['load'] = p_augment_merge_quality[0]
        P[0]['cost'] = p_augment_merge_quality[1]
        P[0]['fitness'] = p_augment_merge_quality[2]
        self.update_bsf(P[0])
        for x in range(1, 1 + PS_RANDOM):
            # idv = self.ps_to_idv(self.path_scanning())
            # #p = self.random_init()
            P[x] = self.get_new_random_idv()
            self.update_bsf(P[x])
        while True: 
            self.main_iteration(P)
            n_restart += 1
            P = defaultdict(dict)
            wanted = sorted(P.iteritems(), key= lambda k,v: v['fitness'], reverse=True)[0:int(PS/2)]
            for idx, idv in enumerate(wanted):
                P[idx] = idv
            for idx in range(len(wanted),PS):
                newinit = self.get_new_random_idv()
                P[idx] = newinit
            if n_restart > 5:
                P_M = 0.2
        return

    def local_search(self, idv):
        '''
        ::params: population individual
        ::output: new individual
        '''
        '''
        print('start local1')
        while True:
            result = self.method_two_opt(idv)
            if not result[0]:
                break
            idv = result[1]
            self.update_bsf(idv)
            # print("local1:", idv['fitness'])
        '''
        # print('start local2')
        while True:
            result = self.method_swap(idv)
            if not result[0]:
                break
            idv = result[1]
            self.update_bsf(idv)
            # print("local2:", idv['fitness'])
        # print('start local3')
        while True:
            result = self.method_move(idv)
            if not result[0]:
                break
            idv = result[1]
            self.update_bsf(idv)
            # print("local3:", idv['fitness'])
        # print('end local')
        return idv

    @staticmethod
    def copy_partition(route):
        '''
        pesudo-deepcopy for the route
        '''
        new_route = list()
        for trip in route:
            new_trip = list()
            for task in trip:
                new_trip.append(task)
            new_route.append(new_trip)
        return new_route

    def method_move(self, idv):
        '''
        move only one task
        '''
        route = idv['partition']
        count = 0
        for idx1, trip in enumerate(route):
            last_task = len(trip) - 1
            for idx2, task in enumerate(trip):
                if idx2 == 0:
                    prev_p = self.depot
                else:
                    prev_p = trip[idx2 - 1][1]
                if last_task == idx2:
                    next_p = self.depot
                else:
                    next_p = trip[idx2 + 1][0]
                cost01 = self.gf.get_shortest_path(prev_p, trip[idx2][0])[1]
                cost02 = self.gf.get_shortest_path(trip[idx2][1], next_p)[1]
                cost03 = self.gf.get_shortest_path(prev_p, next_p)[1]
                load_task = self.gf[task[0]][task[1]]['demand']
                save_cost1 = cost01 + cost02 - cost03
                tmp1 = Solver.copy_partition(route)
                del tmp1[idx1][idx2]
                for idx3, trip2 in enumerate(tmp1):
                    # judge load before insert
                    if idx3 != idx1 and idv['load'][idx3] + load_task > self.capacity:
                        continue
                    last_task2 = len(trip2)
                    for idx4 in range(len(trip2) + 1):
                        if idx4 == 0:
                            prev_p = self.depot
                        else:
                            prev_p = trip2[idx4 - 1][1]
                        if last_task2 == idx4:
                            next_p = self.depot
                        else:
                            next_p = trip2[idx4][0]
                        # nomal insert

                        cost1 = self.gf.get_shortest_path(prev_p, task[0])[1]
                        cost2 = self.gf.get_shortest_path(task[1], next_p)[1]
                        cost3 = self.gf.get_shortest_path(prev_p, next_p)[1]
                        save_cost2 = save_cost1 - (cost1 + cost2 - cost3)
                        if save_cost2 > 0:
                            tmp2 = Solver.copy_partition(tmp1)
                            tmp2[idx3].insert(idx4, task)
                            newfitness = idv['fitness'] - save_cost2
                            idv['partition'] = tmp2
                            idv['cost'][idx1] -= save_cost1
                            idv['cost'][idx3] += save_cost1 - save_cost2
                            idv['load'][idx1] -= load_task
                            idv['load'][idx3] += load_task
                            idv['fitness'] = newfitness
                            idv['chromesome'] = Solver.route_to_chromesome(
                                tmp2)
                            return (True, idv)

                        # inverse insert
                        cost1 = self.gf.get_shortest_path(prev_p, task[1])[1]
                        cost2 = self.gf.get_shortest_path(task[0], next_p)[1]
                        cost3 = self.gf.get_shortest_path(prev_p, next_p)[1]
                        save_cost2 = save_cost1 - (cost1 + cost2 - cost3)
                        if save_cost2 > 0:
                            tmp2 = Solver.copy_partition(tmp1)
                            tmp2[idx3].insert(idx4, task[::-1])
                            newfitness = idv['fitness'] - save_cost2
                            idv['partition'] = tmp2
                            idv['cost'][idx1] -= save_cost1 + \
                                self.gf[task[0]][task[1]]['cost']
                            idv['cost'][idx3] += save_cost1 - \
                                save_cost2 + self.gf[task[0]][task[1]]['cost']
                            idv['load'][idx1] -= load_task
                            idv['load'][idx3] += load_task
                            idv['fitness'] = newfitness
                            idv['chromesome'] = Solver.route_to_chromesome(
                                tmp2)
                            return (True, idv)
        return (False, None)

        '''
        swap two tasks
        need to add inverse insert
        '''
        route = idv['partition']
        count = 0
        total_time = 0
        for idx1, trip in enumerate(route):
            last_task = len(trip) - 1
            for idx2, task1 in enumerate(trip):
                load_task1 = self.gf[task1[0]][task1[1]]['demand']
                cost_task1 = self.gf[task1[0]][task1[1]]['cost']
                if idx2 == 0:
                    prev_p1 = self.depot
                else:
                    prev_p1 = trip[idx2 - 1][1]
                if last_task == idx2:
                    next_p1 = self.depot
                else:
                    next_p1 = trip[idx2 + 1][0]
                cost01 = self.gf.get_shortest_path(prev_p1, task1[0])[1]
                cost02 = self.gf.get_shortest_path(task1[1], next_p1)[1]
                scost1 = cost01 + cost02
                tmp1 = Solver.copy_partition(route)
                del tmp1[idx1][idx2]
                # find another task
                idx3 = idx1
                if idx2 + 2 <= last_task:
                    for offset, task2 in enumerate(trip[idx2 + 2:]):
                        continue
                        # only for that trip, skip the consecutive task
                        idx4 = idx2 + offset + 2
                        prev_p2 = trip[idx4 - 1][1]
                        if last_task == idx4:
                            next_p2 = self.depot
                        else:
                            next_p2 = trip[idx4 + 1][0]
                        # print(prev_p, task)
                        cost1 = self.gf.get_shortest_path(prev_p2, task2[0])[1]
                        cost2 = self.gf.get_shortest_path(task2[1], next_p2)[1]
                        scost2 = cost1 + cost2
                        cost11 = self.gf.get_shortest_path(
                            prev_p1, task2[0])[1]
                        cost12 = self.gf.get_shortest_path(
                            task2[1], next_p1)[1]
                        cost21 = self.gf.get_shortest_path(
                            prev_p2, task1[0])[1]
                        cost22 = self.gf.get_shortest_path(
                            task1[1], next_p2)[1]
                        final_save = scost1 + scost2 - cost11 - cost12 - cost21 - cost22
                        if final_save > 0:
                            tmp2 = Solver.copy_partition(tmp1)
                            tmp2[idx1].insert(idx2, task2)
                            del tmp2[idx3][idx4]
                            tmp2[idx3].insert(idx4, task1)
                            idv['fitness'] = idv['fitness'] - final_save
                            idv['partition'] = tmp2
                            idv['cost'][idx1] -= final_save
                            idv['chromesome'] = Solver.route_to_chromesome(
                                tmp2)
                            return (True, idv)

                for offset, trip2 in enumerate(tmp1[idx1 + 1:]):
                    idx3 = offset + idx1 + 1
                    last_task2 = len(trip2) - 1
                    for idx4, task2 in enumerate(trip2):
                        load_task2 = self.gf[task2[0]][task2[1]]['demand']
                        cost_task2 = self.gf[task2[0]][task2[1]]['cost']
                        if idv['load'][idx3] - load_task2 + load_task1 > self.capacity \
                                or idv['load'][idx1] - load_task1 + load_task2 > self.capacity:
                            continue
                        if idx4 == 0:
                            prev_p2 = self.depot
                        else:
                            prev_p2 = trip2[idx4 - 1][1]
                        if last_task2 == idx4:
                            next_p2 = self.depot
                        else:
                            next_p2 = trip2[idx4 + 1][0]

                        cost1 = self.gf.get_shortest_path(prev_p2, task2[0])[1]
                        cost2 = self.gf.get_shortest_path(task2[1], next_p2)[1]
                        scost2 = cost1 + cost2

                        # normal swap
                        cost11 = self.gf.get_shortest_path(
                            prev_p1, task2[0])[1]
                        cost12 = self.gf.get_shortest_path(
                            task2[1], next_p1)[1]
                        cost21 = self.gf.get_shortest_path(
                            prev_p2, task1[0])[1]
                        cost22 = self.gf.get_shortest_path(
                            task1[1], next_p2)[1]
                        final_save = scost1 + scost2 - cost11 - cost12 - cost21 - cost22

                        if final_save > 0:
                            tmp2 = Solver.copy_partition(tmp1)
                            tmp2[idx1].insert(idx2, task2)
                            del tmp2[idx3][idx4]
                            tmp2[idx3].insert(idx4, task1)
                            idv['fitness'] = idv['fitness'] - final_save
                            idv['partition'] = tmp2
                            idv['cost'][idx1] += cost_task2 + \
                                cost11 + cost12 - scost1
                            idv['cost'][idx3] += cost_task1 + \
                                cost21 + cost22 - scost2
                            idv['load'][idx1] += load_task2 - load_task1
                            idv['load'][idx3] += load_task1 - load_task2
                            idv['chromesome'] = Solver.route_to_chromesome(
                                tmp2)
                            return (True, idv)
                        # inverse first
                        cost31 = self.gf.get_shortest_path(
                            prev_p1, task2[1])[1]
                        cost32 = self.gf.get_shortest_path(
                            task2[0], next_p1)[1]
                        final_save = scost1 + scost2 - cost31 - cost32 - cost21 - cost22
                        if final_save > 0:
                            tmp2 = Solver.copy_partition(tmp1)
                            tmp2[idx1].insert(idx2, task2[::-1])
                            del tmp2[idx3][idx4]
                            tmp2[idx3].insert(idx4, task1)
                            idv['fitness'] = idv['fitness'] - final_save
                            idv['partition'] = tmp2
                            idv['cost'][idx1] += cost_task2 + \
                                cost31 + cost32 - scost1
                            idv['cost'][idx3] += cost_task1 + \
                                cost21 + cost22 - scost2
                            idv['load'][idx1] += load_task2 - load_task1
                            idv['load'][idx3] += load_task1 - load_task2
                            idv['chromesome'] = Solver.route_to_chromesome(
                                tmp2)
                            return (True, idv)
                        # inverse second
                        cost41 = self.gf.get_shortest_path(
                            prev_p2, task1[1])[1]
                        cost42 = self.gf.get_shortest_path(
                            task1[0], next_p2)[1]
                        final_save = scost1 + scost2 - cost11 - cost12 - cost41 - cost42
                        if final_save > 0:
                            tmp2 = Solver.copy_partition(tmp1)
                            tmp2[idx1].insert(idx2, task2)
                            del tmp2[idx3][idx4]
                            tmp2[idx3].insert(idx4, task1[::-1])
                            idv['fitness'] = idv['fitness'] - final_save
                            idv['partition'] = tmp2
                            idv['cost'][idx1] += cost_task2 + \
                                cost11 + cost12 - scost1
                            idv['cost'][idx3] += cost_task1 + \
                                cost41 + cost42 - scost2
                            idv['load'][idx1] += load_task2 - load_task1
                            idv['load'][idx3] += load_task1 - load_task2
                            idv['chromesome'] = Solver.route_to_chromesome(
                                tmp2)
                            return (True, idv)
                        # inverse both
                        cost41 = self.gf.get_shortest_path(
                            prev_p2, task1[1])[1]
                        cost42 = self.gf.get_shortest_path(
                            task1[0], next_p2)[1]
                        final_save = scost1 + scost2 - cost31 - cost32 - cost41 - cost42
                        if final_save > 0:
                            tmp2 = Solver.copy_partition(tmp1)
                            tmp2[idx1].insert(idx2, task2[::-1])
                            del tmp2[idx3][idx4]
                            tmp2[idx3].insert(idx4, task1[::-1])
                            idv['fitness'] = idv['fitness'] - final_save
                            idv['partition'] = tmp2
                            idv['cost'][idx1] += cost_task2 + \
                                cost31 + cost32 - scost1
                            idv['cost'][idx3] += cost_task1 + \
                                cost41 + cost42 - scost2
                            idv['load'][idx1] += load_task2 - load_task1
                            idv['load'][idx3] += load_task1 - load_task2
                            idv['chromesome'] = Solver.route_to_chromesome(
                                tmp2)
                            return (True, idv)

        return (False, None)

        '''
        two opt method
        u-v, x-y
        => u-y, v-x
        => u-x, v-y
        '''
        route = idv['partition']
        task_load = [0] * 4
        task_cost = [0] * 4
        for idx1, trip in enumerate(route):
            last_task = len(trip) - 2
            for idx2, pair1 in enumerate(Solver.pairwise(trip)):
                task_load[0] = self.gf[pair1[0][0]][pair1[0][1]]['demand']
                task_load[1] = self.gf[pair1[1][0]][pair1[1][1]]['demand']
                if idx2 == 0:
                    prev_p1 = self.depot
                else:
                    prev_p1 = trip[idx2 - 1][1]
                if last_task == idx2:
                    next_p1 = self.depot
                else:
                    next_p1 = trip[idx2 + 2][0]
                cost01 = self.gf.get_shortest_path(prev_p1, pair1[0][0])[1]
                cost02 = self.gf.get_shortest_path(pair1[1][1], next_p1)[1]
                cost03 = self.gf.get_shortest_path(pair1[0][1], pair1[1][0])[1]
                original_cost0 = cost01 + cost02 + cost03
                tmp1 = Solver.copy_partition(route)
                del tmp1[idx1][idx2]
                del tmp1[idx1][idx2]
                if idx2 < last_task - 5:
                    for offset, pair in enumerate(Solver.pairwise(trip[idx2 + 3:])):
                        idx3 = offset + idx1 + 1
                        last_task2 = last_task
                        pass
                for offset, trip2 in enumerate(tmp1[idx1 + 1:]):

                    idx3 = offset + idx1 + 1
                    last_task2 = len(trip2) - 2
                    for idx4, pair2 in enumerate(Solver.pairwise(trip2)):
                        task_load[2] = self.gf[pair2[0]
                                               [0]][pair2[0][1]]['demand']
                        task_load[3] = self.gf[pair2[1]
                                               [0]][pair2[1][1]]['demand']
                        if idv['load'][idx1] - task_load[1] + min(task_load[2], task_load[3]) > self.capacity or \
                                idv['load'][idx3] + task_load[1] - max(task_load[2], task_load[3]) > self.capacity:
                            continue
                        if idx4 == 0:
                            prev_p2 = self.depot
                        else:
                            prev_p2 = trip2[idx4 - 1][1]
                        if last_task2 == idx4:
                            next_p2 = self.depot
                        else:
                            next_p2 = trip2[idx4 + 2][0]

                        cost11 = self.gf.get_shortest_path(
                            prev_p2, pair2[0][0])[1]
                        cost12 = self.gf.get_shortest_path(
                            pair2[1][1], next_p2)[1]
                        cost13 = self.gf.get_shortest_path(
                            pair2[0][1], pair2[1][0])[1]
                        original_cost1 = cost11 + cost12 + cost13
                        original_cost_total = original_cost0 + original_cost1

                        diff_load = task_load[3] - task_load[1]
                        if idv['load'][idx1] + diff_load < self.capacity and \
                                idv['load'][idx3] - diff_load < self.capacity:
                            # u-v, x-y  => u-y, v-x
                            cost21 = cost01  # -u
                            cost22 = self.gf.get_shortest_path(
                                pair2[1][1], next_p1)[1]  # y-
                            cost23 = self.gf.get_shortest_path(
                                pair1[0][1], pair2[1][0])[1]  # u-y
                            newcost0 = cost21 + cost22 + cost23
                            cost31 = self.gf.get_shortest_path(
                                prev_p2, pair1[1][0])[1]  # -v
                            cost32 = self.gf.get_shortest_path(
                                pair2[0][1], next_p2)[1]  # x-
                            cost33 = self.gf.get_shortest_path(
                                pair1[1][1], pair2[0][0])[1]
                            newcost1 = cost31 + cost32 + cost33
                            newcost = newcost0 + newcost1
                            diff_cost = original_cost_total - newcost
                            if diff_cost > 0:
                                task_cost[1] = self.gf[pair1[1]
                                                       [0]][pair1[1][1]]['cost']
                                task_cost[3] = self.gf[pair2[1]
                                                       [0]][pair2[1][1]]['cost']
                                tmp2 = Solver.copy_partition(tmp1)
                                tmp2[idx1][idx2:idx2] = list(
                                    (pair1[0], pair2[1]))
                                del tmp2[idx3][idx4]
                                del tmp2[idx3][idx4]
                                tmp2[idx3][idx4:idx4] = list(
                                    (pair1[1], pair2[0]))
                                idv['partition'] = tmp2
                                idv['fitness'] = idv['fitness'] - (diff_cost)
                                idv['chromesome'] = Solver.route_to_chromesome(
                                    tmp2)
                                exchange_cost = task_cost[3] - task_cost[1]
                                idv['cost'][idx1] += newcost0 - \
                                    original_cost0 + exchange_cost
                                idv['cost'][idx3] += newcost1 - \
                                    original_cost1 - exchange_cost
                                exchange_load = task_load[3] - task_load[1]
                                # print(exchange_load)
                                idv['load'][idx1] += exchange_load
                                idv['load'][idx3] -= exchange_load
                                return (True, idv)
                        diff_load = task_load[2] - task_load[1]
                        if idv['load'][idx1] + diff_load < self.capacity and \
                                idv['load'][idx3] - diff_load < self.capacity:
                            # u-v, x-y  => u-x, v-y
                            cost21 = cost01  # -u
                            cost22 = self.gf.get_shortest_path(
                                pair2[0][1], next_p1)[1]  # x-
                            cost23 = self.gf.get_shortest_path(
                                pair1[0][1], pair2[0][0])[1]  # u-x
                            newcost0 = cost21 + cost22 + cost23
                            cost31 = self.gf.get_shortest_path(
                                prev_p2, pair1[1][0])[1]  # -v
                            cost32 = self.gf.get_shortest_path(
                                pair2[1][1], next_p2)[1]  # y-
                            cost33 = self.gf.get_shortest_path(
                                pair1[1][1], pair2[1][0])[1]  # v-y
                            newcost1 = cost31 + cost32 + cost33
                            newcost = newcost0 + newcost1
                            diff_cost = original_cost_total - newcost
                            if diff_cost > 0:
                                task_cost[1] = self.gf[pair1[1]
                                                       [0]][pair1[1][1]]['cost']
                                task_cost[2] = self.gf[pair2[0]
                                                       [0]][pair2[0][1]]['cost']
                                tmp2 = Solver.copy_partition(tmp1)
                                tmp2[idx1][idx2:idx2] = list(
                                    (pair1[0], pair2[0]))
                                del tmp2[idx3][idx4]
                                del tmp2[idx3][idx4]
                                tmp2[idx3][idx4:idx4] = list(
                                    (pair1[1], pair2[1]))
                                idv['partition'] = tmp2
                                idv['fitness'] = idv['fitness'] - (diff_cost)
                                idv['chromesome'] = Solver.route_to_chromesome(
                                    tmp2)
                                exchange_cost = task_cost[2] - task_cost[1]
                                idv['cost'][idx1] += newcost0 - \
                                    original_cost0 + exchange_cost
                                idv['cost'][idx3] += newcost1 - \
                                    original_cost1 - exchange_cost
                                exchange_load = task_load[2] - task_load[1]
                                idv['load'][idx1] += exchange_load
                                idv['load'][idx3] -= exchange_load
                                return (True, idv)
        return (False, None)

    def method_two_opt(self, idv):
        '''
        two opt method
        u-v, x-y
        => u-y, v-x
        => u-x, v-y
        '''
        route = idv['partition']
        task_load = [0] * 4
        task_cost = [0] * 4
        for idx1, trip in enumerate(route):
            last_task = len(trip) - 2
            for idx2, pair1 in enumerate(Solver.pairwise(trip)):
                task_load[0] = self.gf[pair1[0][0]][pair1[0][1]]['demand']
                task_load[1] = self.gf[pair1[1][0]][pair1[1][1]]['demand']
                if idx2 == 0:
                    prev_p1 = self.depot
                else:
                    prev_p1 = trip[idx2 - 1][1]
                if last_task == idx2:
                    next_p1 = self.depot
                else:
                    next_p1 = trip[idx2 + 2][0]
                cost01 = self.gf.get_shortest_path(prev_p1, pair1[0][0])[1]
                cost02 = self.gf.get_shortest_path(pair1[1][1], next_p1)[1]
                cost03 = self.gf.get_shortest_path(pair1[0][1], pair1[1][0])[1]
                original_cost0 = cost01 + cost02 + cost03
                tmp1 = Solver.copy_partition(route)
                del tmp1[idx1][idx2]
                del tmp1[idx1][idx2]
                if idx2 < last_task - 5:
                    idx3 = idx1
                    # for the opt-2 in the same trip
                    trip2 = trip
                    for offset, pair2 in enumerate(Solver.pairwise(trip2[idx2 + 3:])):
                        idx4 = offset + idx2 + 3
                        last_task2 = last_task
                        task_load[2] = self.gf[pair2[0]
                                               [0]][pair2[0][1]]['demand']
                        task_load[3] = self.gf[pair2[1]
                                               [0]][pair2[1][1]]['demand']
                        if idx4 == 0:
                            prev_p2 = self.depot
                        else:
                            prev_p2 = trip2[idx4 - 1][1]
                        if last_task2 == idx4:
                            next_p2 = self.depot
                        else:
                            next_p2 = trip2[idx4 + 2][0]

                        cost11 = self.gf.get_shortest_path(
                            prev_p2, pair2[0][0])[1]
                        cost12 = self.gf.get_shortest_path(
                            pair2[1][1], next_p2)[1]
                        cost13 = self.gf.get_shortest_path(
                            pair2[0][1], pair2[1][0])[1]
                        original_cost1 = cost11 + cost12 + cost13
                        original_cost_total = original_cost0 + original_cost1

                        diff_load = task_load[3] - task_load[1]
                        # u-v, x-y  => u-y, v-x
                        cost21 = cost01  # -u
                        cost22 = self.gf.get_shortest_path(
                            pair2[1][1], next_p1)[1]  # y-
                        cost23 = self.gf.get_shortest_path(
                            pair1[0][1], pair2[1][0])[1]  # u-y
                        newcost0 = cost21 + cost22 + cost23
                        cost31 = self.gf.get_shortest_path(
                            prev_p2, pair1[1][0])[1]  # -v
                        cost32 = self.gf.get_shortest_path(
                            pair2[0][1], next_p2)[1]  # x-
                        cost33 = self.gf.get_shortest_path(
                            pair1[1][1], pair2[0][0])[1]
                        newcost1 = cost31 + cost32 + cost33
                        newcost = newcost0 + newcost1
                        diff_cost = original_cost_total - newcost
                        if diff_cost > 0:
                            task_cost[1] = self.gf[pair1[1]
                                                   [0]][pair1[1][1]]['cost']
                            task_cost[3] = self.gf[pair2[1]
                                                   [0]][pair2[1][1]]['cost']
                            tmp2 = Solver.copy_partition(tmp1)
                            tmp2[idx1][idx2:idx2] = list(
                                (pair1[0], pair2[1]))
                            del tmp2[idx3][idx4]
                            del tmp2[idx3][idx4]
                            tmp2[idx3][idx4:idx4] = list(
                                (pair1[1], pair2[0]))
                            idv['partition'] = tmp2
                            idv['fitness'] = idv['fitness'] - (diff_cost)
                            idv['chromesome'] = Solver.route_to_chromesome(
                                tmp2)
                            exchange_cost = task_cost[3] - task_cost[1]
                            idv['cost'][idx1] += newcost0 - \
                                original_cost0 + exchange_cost
                            idv['cost'][idx3] += newcost1 - \
                                original_cost1 - exchange_cost
                            exchange_load = task_load[3] - task_load[1]
                            # print(exchange_load)
                            idv['load'][idx1] += exchange_load
                            idv['load'][idx3] -= exchange_load
                            return (True, idv)
                        diff_load = task_load[2] - task_load[1]
                        # u-v, x-y  => u-x, v-y
                        cost21 = cost01  # -u
                        cost22 = self.gf.get_shortest_path(
                            pair2[0][1], next_p1)[1]  # x-
                        cost23 = self.gf.get_shortest_path(
                            pair1[0][1], pair2[0][0])[1]  # u-x
                        newcost0 = cost21 + cost22 + cost23
                        cost31 = self.gf.get_shortest_path(
                            prev_p2, pair1[1][0])[1]  # -v
                        cost32 = self.gf.get_shortest_path(
                            pair2[1][1], next_p2)[1]  # y-
                        cost33 = self.gf.get_shortest_path(
                            pair1[1][1], pair2[1][0])[1]  # v-y
                        newcost1 = cost31 + cost32 + cost33
                        newcost = newcost0 + newcost1
                        diff_cost = original_cost_total - newcost
                        if diff_cost > 0:
                            task_cost[1] = self.gf[pair1[1]
                                                   [0]][pair1[1][1]]['cost']
                            task_cost[2] = self.gf[pair2[0]
                                                   [0]][pair2[0][1]]['cost']
                            tmp2 = Solver.copy_partition(tmp1)
                            tmp2[idx1][idx2:idx2] = list(
                                (pair1[0], pair2[0]))
                            del tmp2[idx3][idx4]
                            del tmp2[idx3][idx4]
                            tmp2[idx3][idx4:idx4] = list(
                                (pair1[1], pair2[1]))
                            idv['partition'] = tmp2
                            idv['fitness'] = idv['fitness'] - (diff_cost)
                            idv['chromesome'] = Solver.route_to_chromesome(
                                tmp2)
                            exchange_cost = task_cost[2] - task_cost[1]
                            idv['cost'][idx1] += newcost0 - \
                                original_cost0 + exchange_cost
                            idv['cost'][idx3] += newcost1 - \
                                original_cost1 - exchange_cost
                            exchange_load = task_load[2] - task_load[1]
                            idv['load'][idx1] += exchange_load
                            idv['load'][idx3] -= exchange_load
                            return (True, idv)
                # for two-opt not in the same trip
                for offset, trip2 in enumerate(tmp1[idx1 + 1:]):

                    idx3 = offset + idx1 + 1
                    last_task2 = len(trip2) - 2
                    for idx4, pair2 in enumerate(Solver.pairwise(trip2)):
                        task_load[2] = self.gf[pair2[0]
                                               [0]][pair2[0][1]]['demand']
                        task_load[3] = self.gf[pair2[1]
                                               [0]][pair2[1][1]]['demand']
                        if idv['load'][idx1] - task_load[1] + min(task_load[2], task_load[3]) > self.capacity or \
                                idv['load'][idx3] + task_load[1] - max(task_load[2], task_load[3]) > self.capacity:
                            continue
                        if idx4 == 0:
                            prev_p2 = self.depot
                        else:
                            prev_p2 = trip2[idx4 - 1][1]
                        if last_task2 == idx4:
                            next_p2 = self.depot
                        else:
                            next_p2 = trip2[idx4 + 2][0]

                        cost11 = self.gf.get_shortest_path(
                            prev_p2, pair2[0][0])[1]
                        cost12 = self.gf.get_shortest_path(
                            pair2[1][1], next_p2)[1]
                        cost13 = self.gf.get_shortest_path(
                            pair2[0][1], pair2[1][0])[1]
                        original_cost1 = cost11 + cost12 + cost13
                        original_cost_total = original_cost0 + original_cost1

                        diff_load = task_load[3] - task_load[1]
                        if idv['load'][idx1] + diff_load < self.capacity and \
                                idv['load'][idx3] - diff_load < self.capacity:
                            # u-v, x-y  => u-y, v-x
                            cost21 = cost01  # -u
                            cost22 = self.gf.get_shortest_path(
                                pair2[1][1], next_p1)[1]  # y-
                            cost23 = self.gf.get_shortest_path(
                                pair1[0][1], pair2[1][0])[1]  # u-y
                            newcost0 = cost21 + cost22 + cost23
                            cost31 = self.gf.get_shortest_path(
                                prev_p2, pair1[1][0])[1]  # -v
                            cost32 = self.gf.get_shortest_path(
                                pair2[0][1], next_p2)[1]  # x-
                            cost33 = self.gf.get_shortest_path(
                                pair1[1][1], pair2[0][0])[1]
                            newcost1 = cost31 + cost32 + cost33
                            newcost = newcost0 + newcost1
                            diff_cost = original_cost_total - newcost
                            if diff_cost > 0:
                                task_cost[1] = self.gf[pair1[1]
                                                       [0]][pair1[1][1]]['cost']
                                task_cost[3] = self.gf[pair2[1]
                                                       [0]][pair2[1][1]]['cost']
                                tmp2 = Solver.copy_partition(tmp1)
                                tmp2[idx1][idx2:idx2] = list(
                                    (pair1[0], pair2[1]))
                                del tmp2[idx3][idx4]
                                del tmp2[idx3][idx4]
                                tmp2[idx3][idx4:idx4] = list(
                                    (pair1[1], pair2[0]))
                                idv['partition'] = tmp2
                                idv['fitness'] = idv['fitness'] - (diff_cost)
                                idv['chromesome'] = Solver.route_to_chromesome(
                                    tmp2)
                                exchange_cost = task_cost[3] - task_cost[1]
                                idv['cost'][idx1] += newcost0 - \
                                    original_cost0 + exchange_cost
                                idv['cost'][idx3] += newcost1 - \
                                    original_cost1 - exchange_cost
                                exchange_load = task_load[3] - task_load[1]
                                # print(exchange_load)
                                idv['load'][idx1] += exchange_load
                                idv['load'][idx3] -= exchange_load
                                return (True, idv)
                        diff_load = task_load[2] - task_load[1]
                        if idv['load'][idx1] + diff_load < self.capacity and \
                                idv['load'][idx3] - diff_load < self.capacity:
                            # u-v, x-y  => u-x, v-y
                            cost21 = cost01  # -u
                            cost22 = self.gf.get_shortest_path(
                                pair2[0][1], next_p1)[1]  # x-
                            cost23 = self.gf.get_shortest_path(
                                pair1[0][1], pair2[0][0])[1]  # u-x
                            newcost0 = cost21 + cost22 + cost23
                            cost31 = self.gf.get_shortest_path(
                                prev_p2, pair1[1][0])[1]  # -v
                            cost32 = self.gf.get_shortest_path(
                                pair2[1][1], next_p2)[1]  # y-
                            cost33 = self.gf.get_shortest_path(
                                pair1[1][1], pair2[1][0])[1]  # v-y
                            newcost1 = cost31 + cost32 + cost33
                            newcost = newcost0 + newcost1
                            diff_cost = original_cost_total - newcost
                            if diff_cost > 0:
                                task_cost[1] = self.gf[pair1[1]
                                                       [0]][pair1[1][1]]['cost']
                                task_cost[2] = self.gf[pair2[0]
                                                       [0]][pair2[0][1]]['cost']
                                tmp2 = Solver.copy_partition(tmp1)
                                tmp2[idx1][idx2:idx2] = list(
                                    (pair1[0], pair2[0]))
                                del tmp2[idx3][idx4]
                                del tmp2[idx3][idx4]
                                tmp2[idx3][idx4:idx4] = list(
                                    (pair1[1], pair2[1]))
                                idv['partition'] = tmp2
                                idv['fitness'] = idv['fitness'] - (diff_cost)
                                idv['chromesome'] = Solver.route_to_chromesome(
                                    tmp2)
                                exchange_cost = task_cost[2] - task_cost[1]
                                idv['cost'][idx1] += newcost0 - \
                                    original_cost0 + exchange_cost
                                idv['cost'][idx3] += newcost1 - \
                                    original_cost1 - exchange_cost
                                exchange_load = task_load[2] - task_load[1]
                                idv['load'][idx1] += exchange_load
                                idv['load'][idx3] -= exchange_load
                                return (True, idv)
        return (False, None)

    def method_swap(self, idv):
        '''
        swap two tasks
        need to add inverse insert
        '''
        route = idv['partition']
        for idx1, trip in enumerate(route):
            last_task = len(trip) - 1
            for idx2, task1 in enumerate(trip):
                load_task1 = self.gf[task1[0]][task1[1]]['demand']
                cost_task1 = self.gf[task1[0]][task1[1]]['cost']
                if idx2 == 0:
                    prev_p1 = self.depot
                else:
                    prev_p1 = trip[idx2 - 1][1]
                if last_task == idx2:
                    next_p1 = self.depot
                else:
                    next_p1 = trip[idx2 + 1][0]
                cost01 = self.gf.get_shortest_path(prev_p1, task1[0])[1]
                cost02 = self.gf.get_shortest_path(task1[1], next_p1)[1]
                scost1 = cost01 + cost02
                tmp1 = Solver.copy_partition(route)
                del tmp1[idx1][idx2]
                # find another task
                idx3 = idx1
                if idx2 + 2 <= last_task:
                    for offset, task2 in enumerate(trip[idx2 + 2:]):
                        # only for that trip, skip the consecutive task
                        idx4 = idx2 + offset + 2
                        prev_p2 = trip[idx4 - 1][1]
                        if last_task == idx4:
                            next_p2 = self.depot
                        else:
                            next_p2 = trip[idx4 + 1][0]
                        # print(prev_p, task)
                        cost1 = self.gf.get_shortest_path(prev_p2, task2[0])[1]
                        cost2 = self.gf.get_shortest_path(task2[1], next_p2)[1]
                        scost2 = cost1 + cost2
                        cost11 = self.gf.get_shortest_path(
                            prev_p1, task2[0])[1]
                        cost12 = self.gf.get_shortest_path(
                            task2[1], next_p1)[1]
                        cost21 = self.gf.get_shortest_path(
                            prev_p2, task1[0])[1]
                        cost22 = self.gf.get_shortest_path(
                            task1[1], next_p2)[1]
                        final_save = scost1 + scost2 - cost11 - cost12 - cost21 - cost22
                        if final_save > 0:
                            tmp2 = Solver.copy_partition(tmp1)
                            tmp2[idx1].insert(idx2, task2)
                            del tmp2[idx3][idx4]
                            tmp2[idx3].insert(idx4, task1)
                            idv['fitness'] = idv['fitness'] - final_save
                            idv['partition'] = tmp2
                            idv['cost'][idx1] -= final_save
                            idv['chromesome'] = Solver.route_to_chromesome(
                                tmp2)
                            return (True, idv)

                for offset, trip2 in enumerate(tmp1[idx1 + 1:]):
                    idx3 = offset + idx1 + 1
                    last_task2 = len(trip2) - 1
                    for idx4, task2 in enumerate(trip2):
                        load_task2 = self.gf[task2[0]][task2[1]]['demand']
                        cost_task2 = self.gf[task2[0]][task2[1]]['cost']
                        if idv['load'][idx3] - load_task2 + load_task1 > self.capacity \
                                or idv['load'][idx1] - load_task1 + load_task2 > self.capacity:
                            continue
                        if idx4 == 0:
                            prev_p2 = self.depot
                        else:
                            prev_p2 = trip2[idx4 - 1][1]
                        if last_task2 == idx4:
                            next_p2 = self.depot
                        else:
                            next_p2 = trip2[idx4 + 1][0]

                        cost1 = self.gf.get_shortest_path(prev_p2, task2[0])[1]
                        cost2 = self.gf.get_shortest_path(task2[1], next_p2)[1]
                        scost2 = cost1 + cost2

                        # normal swap
                        cost11 = self.gf.get_shortest_path(
                            prev_p1, task2[0])[1]
                        cost12 = self.gf.get_shortest_path(
                            task2[1], next_p1)[1]
                        cost21 = self.gf.get_shortest_path(
                            prev_p2, task1[0])[1]
                        cost22 = self.gf.get_shortest_path(
                            task1[1], next_p2)[1]
                        final_save = scost1 + scost2 - cost11 - cost12 - cost21 - cost22

                        if final_save > 0:

                            tmp2 = Solver.copy_partition(tmp1)
                            tmp2[idx1].insert(idx2, task2)
                            del tmp2[idx3][idx4]
                            tmp2[idx3].insert(idx4, task1)
                            idv['fitness'] = idv['fitness'] - final_save
                            idv['partition'] = tmp2
                            idv['cost'][idx1] += cost_task2 - \
                                cost_task1 + cost11 + cost12 - scost1
                            idv['cost'][idx3] += cost_task1 - \
                                cost_task2 + cost21 + cost22 - scost2
                            idv['load'][idx1] += load_task2 - load_task1
                            idv['load'][idx3] += load_task1 - load_task2
                            idv['chromesome'] = Solver.route_to_chromesome(
                                tmp2)
                            return (True, idv)

                        # inverse first
                        cost31 = self.gf.get_shortest_path(
                            prev_p1, task2[1])[1]
                        cost32 = self.gf.get_shortest_path(
                            task2[0], next_p1)[1]
                        final_save = scost1 + scost2 - cost31 - cost32 - cost21 - cost22
                        if final_save > 0:
                            tmp2 = Solver.copy_partition(tmp1)
                            tmp2[idx1].insert(idx2, task2[::-1])
                            del tmp2[idx3][idx4]
                            tmp2[idx3].insert(idx4, task1)
                            idv['fitness'] = idv['fitness'] - final_save
                            idv['partition'] = tmp2
                            idv['cost'][idx1] += cost_task2 - \
                                cost_task1 + cost31 + cost32 - scost1
                            idv['cost'][idx3] += cost_task1 - \
                                cost_task2 + cost21 + cost22 - scost2
                            idv['load'][idx1] += load_task2 - load_task1
                            idv['load'][idx3] += load_task1 - load_task2
                            idv['chromesome'] = Solver.route_to_chromesome(
                                tmp2)
                            return (True, idv)
                        # inverse second
                        cost41 = self.gf.get_shortest_path(
                            prev_p2, task1[1])[1]
                        cost42 = self.gf.get_shortest_path(
                            task1[0], next_p2)[1]
                        final_save = scost1 + scost2 - cost11 - cost12 - cost41 - cost42
                        if final_save > 0:
                            tmp2 = Solver.copy_partition(tmp1)
                            tmp2[idx1].insert(idx2, task2)
                            del tmp2[idx3][idx4]
                            tmp2[idx3].insert(idx4, task1[::-1])
                            idv['fitness'] = idv['fitness'] - final_save
                            idv['partition'] = tmp2
                            idv['cost'][idx1] += cost_task2 - \
                                cost_task1 + cost11 + cost12 - scost1
                            idv['cost'][idx3] += cost_task1 - \
                                cost_task2 + cost41 + cost42 - scost2
                            idv['load'][idx1] += load_task2 - load_task1
                            idv['load'][idx3] += load_task1 - load_task2
                            idv['chromesome'] = Solver.route_to_chromesome(
                                tmp2)
                            return (True, idv)
                        # inverse both
                        cost41 = self.gf.get_shortest_path(
                            prev_p2, task1[1])[1]
                        cost42 = self.gf.get_shortest_path(
                            task1[0], next_p2)[1]
                        final_save = scost1 + scost2 - cost31 - cost32 - cost41 - cost42
                        if final_save > 0:
                            tmp2 = Solver.copy_partition(tmp1)
                            tmp2[idx1].insert(idx2, task2[::-1])
                            del tmp2[idx3][idx4]
                            tmp2[idx3].insert(idx4, task1[::-1])
                            idv['fitness'] = idv['fitness'] - final_save
                            idv['partition'] = tmp2
                            idv['cost'][idx1] += cost_task2 - \
                                cost_task1 + cost31 + cost32 - scost1
                            idv['cost'][idx3] += cost_task1 - \
                                cost_task2 + cost41 + cost42 - scost2
                            idv['load'][idx1] += load_task2 - load_task1
                            idv['load'][idx3] += load_task1 - load_task2
                            idv['chromesome'] = Solver.route_to_chromesome(
                                tmp2)
                            return (True, idv)
        return (False, None)

    @staticmethod
    def route_to_chromesome(route):
        chromesome = []
        for trip in route:
            chromesome += trip
        return chromesome

    def mutation(self, idv):
        idxa, idxb = random.sample(xrange(len(idv['chromesome'])), 2)
        # print('mutation', idxa, idxb)
        tmp = idv['chromesome'][idxa]
        idv['chromesome'][idxa] = idv['chromesome'][idxb]
        idv['chromesome'][idxb] = tmp
        idv['partition'] = self.chromesome_partition(idv['chromesome'])
        idv['load'], idv['cost'], idv['fitness'] = self.solution_verify(idv['partition'])[
            :3]
        return idv

    def random_init(self):
        tasks = self.gf.get_tasks_unique()
        solution = list(tasks)
        shuffle(solution)

        def flip(task):
            if random.random() < 0.5:
                return (task[1], task[0])
            else:
                return task
        solution = map(flip, solution)
        return solution

    def which_better(self, u1, u2, load):
        r_cq1 = self.gf[u1[0]][u1[1]]['cost'] / self.gf[u1[0]][u1[1]]['demand']
        r_cq2 = self.gf[u2[0]][u2[1]]['cost'] / self.gf[u2[0]][u2[1]]['demand']
        return_cost1 = self.gf.get_shortest_path(u1[1], self.depot)[1]
        return_cost2 = self.gf.get_shortest_path(u2[1], self.depot)[1]
        # random rules
        rule = random.choice([0, 1, 2, 3, 4])
        if rule == 0:
            if r_cq1 > r_cq2:
                return u1
            elif r_cq1 < r_cq2:
                return u2
            else:
                return random.choice([u1, u2])
        elif rule == 1:
            if return_cost1 > return_cost2:
                return u1
            elif return_cost1 < return_cost2:
                return u2
            else:
                return random.choice([u1, u2])
        elif rule == 2:
            if r_cq1 < r_cq2:
                return u1
            elif r_cq1 > r_cq2:
                return u2
            else:
                return random.choice([u1, u2])
        elif rule == 3:
            if return_cost1 < return_cost2:
                return u1
            elif return_cost1 > return_cost2:
                return u2
            else:
                return random.choice([u1, u2])
        elif rule == 4:
            if load < self.capacity / 2:
                if return_cost1 > return_cost2:
                    return u1
                elif return_cost1 < return_cost2:
                    return u2
                else:
                    return random.choice([u1, u2])
            else:
                if return_cost1 < return_cost2:
                    return u1
                elif return_cost1 > return_cost2:
                    return u2
                else:
                    return random.choice([u1, u2])

    def ps_to_idv(self, result):
        '''
        input pathscanning solution
        output chromesome rep
        '''
        idv = defaultdict(dict)
        chromesome = list()
        partition = list()
        load = list()
        cost = list()
        for k, v in result[0].iteritems():
            chromesome += v
            partition.append(v)
            load.append(result[1][k])
            cost.append(result[2][k])
        idv['partition'] = partition
        idv['chromesome'] = chromesome
        idv['load'] = load
        idv['cost'] = cost
        idv['fitness'] = sum(cost)
        return idv

    def path_scanning(self):
        '''
        get init solutions from path scanning
        '''
        k = 0
        R = defaultdict(dict)
        load = defaultdict(dict)
        cost = defaultdict(dict)
        free_task = set(self.gf.get_tasks())
        while free_task:
            k += 1
            R[k] = list()
            load[k], cost[k] = 0, 0
            end = self.depot
            u = None
            while True:
                if not free_task:
                    break
                d_min = float('inf')
                for f_task in free_task:
                    if self.gf[f_task[0]][f_task[1]]['demand'] + load[k] > self.capacity:
                        d_min = float('inf')
                        break
                    if u == None:
                        u = f_task
                        d_min = self.gf.get_shortest_path(end, f_task[0])[1]
                    d_tmp = self.gf.get_shortest_path(end, f_task[0])[1]
                    # print(d_tmp,d_min, end,f_task, u)
                    if d_tmp < d_min:
                        d_min = d_tmp
                        u = f_task
                    elif d_tmp == d_min:
                        d_min = d_tmp
                        # print(u)
                        u = self.which_better(u, f_task, load[k])
                        # print(u)
                if d_min == float('inf'):
                    break
                R[k].append(u)
                free_task.remove(u)
                free_task.remove((u[1], u[0]))
                cost[k] += self.gf[u[0]][u[1]]['cost'] + d_min
                load[k] += self.gf[u[0]][u[1]]['demand']
                end = u[1]
            cost[k] += self.gf.get_shortest_path(u[1], self.depot)[1]
        return R, load, cost
        # return R

    def concate_circles(self, circle1, circle2, idx1, idx2):
        """
        params: circle: the path
        return [circle_list, overpapping_best, cost_largest]
        """
        overlapping_best = (0, 0)
        cost_largest = 0  # largest saving cost
        for p1, val1 in enumerate(circle1[-1:-1 - idx1:-1]):
            for p2, val2 in enumerate(circle2[0:idx2]):
                if val1 == val2:
                    cost_save_1 = Graph.calculate_path_cost(
                        self.gf, circle1[-1:-1 - p1 - 1])
                    cost_save_2 = Graph.calculate_path_cost(
                        self.gf, circle2[0:p2 + 1])
                    save_total = cost_save_1 + cost_save_2
                    if cost_largest < save_total:
                        overlapping_best = (p1, p2)
                        cost_largest = save_total
        return circle1[:-1 - overlapping_best[0]] + circle2[overlapping_best[1]:], overlapping_best, cost_largest

    def get_first_last_req(self, circle):
        """
        params circle: dict
        """
        first, last = 0, 0
        for idx, val in enumerate(circle['circle'][-1::-1]):
            required = False
            for required_e in circle['aq_set']:
                if val in required_e:
                    last = idx
                    # print(val, required_e)
                    required = True
                    break
            if required:
                break
        for idx, val in enumerate(circle['circle']):
            required = False
            for required_e in circle['aq_set']:
                if val in required_e:
                    first = idx
                    required = True
                    break
            if required:
                break
        return first, last

    def merge_circles(self, circle1, circle2):
        if circle1['load'] + circle2['load'] > self.capacity:
            return None
        idx1 = self.get_first_last_req(circle1)
        idx2 = self.get_first_last_req(circle2)
        # print(idx1,idx2)
        results = list()
        results.append(self.concate_circles(
            circle1['circle'], circle2['circle'], idx1[1], idx2[0]))
        results.append(self.concate_circles(
            circle1['circle'][::-1], circle2['circle'], idx1[0], idx2[0]))
        results.append(self.concate_circles(
            circle2['circle'], circle1['circle'], idx2[1], idx1[0]))
        results.append(self.concate_circles(
            circle2['circle'], circle1['circle'][::-1], idx2[1], idx1[1]))
        max_save = 0
        new_circle = None
        for result in results:
            if result[2] >= max_save:
                new_circle = result[0]
                max_save = result[2]
        if new_circle == None:
            # print(results)
            return None
        return {'circle': new_circle, 'cost': circle1['cost'] + circle2['cost'] - max_save, 'saving': max_save,
                'load': circle1['load'] + circle2['load'], 'aq_set': circle1['aq_set'].union(circle2['aq_set'])}

    @staticmethod
    def pairwise(iterable):
        "s -> (s0,s1), (s1,s2), (s2, s3), ..."
        a, b = tee(iterable)
        next(b, None)
        return izip(a, b)

    @staticmethod
    def is_inclueded(path, target):
        inv_target = (target[1], target[0])
        for edge in Solver.pairwise(path):
            # print(target, edge)
            if target == edge or inv_target == edge:
                return True
        return False

    def augment_merge(self):
        # init routes
        k = 0
        free_tasks = set(self.gf.get_tasks_unique())
        R = defaultdict(dict)
        # cost = defaultdict(dict)
        for f_task in free_tasks:
            x = self.gf.get_shortest_path(self.depot, f_task[0])
            y = self.gf.get_shortest_path(f_task[1], self.depot)
            if x[1] == 0:
                x = ([self.depot, ], y[1])
            if y[1] == 0:
                y[0] = ([self.depot, ], x[1])
            R[k]['circle'] = x[0] + y[0]
            R[k]['cost'] = x[1] + y[1]
            R[k]['load'] = self.gf[f_task[0]][f_task[1]]['demand']
            R[k]['aq_set'] = set()
            R[k]['aq_set'].add(f_task)
            #print(f_task, R[k], cost[k])
            k += 1
        # augment phase
        R_sorted = sorted(R.iteritems(), key=lambda (k, v): len(v['circle']), reverse=True)
        deleted = set()
        for idx, circle in enumerate(R_sorted):
            for smaller_circle in R_sorted[idx + 1:]:
                if smaller_circle[0] in deleted:
                    continue
                if circle[1]['load'] + smaller_circle[1]['load'] > self.capacity:
                    continue
                # print(smaller_circle[1][1]['aq_set'])
                flag_include = True
                for edge in smaller_circle[1]['aq_set']:
                    # print(circle)
                    if not self.is_inclueded(circle[1]['circle'], edge):
                        flag_include = False
                if flag_include:
                    deleted.add(smaller_circle[0])
                    circle[1]['aq_set'] = circle[1]['aq_set'].union(
                        smaller_circle[1]['aq_set'])
                    circle[1]['load'] += smaller_circle[1]['load']
                    #print("[oK]", circle, smaller_circle)
        R_aug = list()
        for circle in R_sorted:
            if circle[0] not in deleted:
                circle[1]['delete'] = False
                R_aug.append(circle[1])
        # merge phase
        while True:
            merge_res = list()
            merge_next = list()
            for idx1, circle1 in enumerate(R_aug):
                for idx2, circle2 in enumerate(R_aug[idx1 + 1:]):
                    #print(self.gf, circle1, circle2)
                    tmp = self.merge_circles(circle1, circle2)
                    if tmp:
                        merge_res.append((tmp, idx1, idx1 + idx2 + 1))
                        #print(tmp, idx1, idx2+idx1+1, circle1, circle2)
            if len(merge_res) is 0:
                break
            merge_res = sorted(merge_res, key=lambda (tmp, idx1, idx2): tmp['saving'], reverse=True)
            for merger in merge_res:
                if not R_aug[merger[1]]['delete'] and not R_aug[merger[2]]['delete']:
                    # print(merger[1],merger[2])
                    R_aug[merger[1]]['delete'] = True
                    R_aug[merger[2]]['delete'] = True
                    del(merger[0]['saving'])
                    merger[0]['delete'] = False
                    merge_next.append(merger[0])
            for circle in R_aug:
                if not circle['delete']:
                    # print(circle)
                    merge_next.append(circle)
            R_aug = merge_next
        R_final = R_aug
        return R_final

    def am_to_chromesome(self, am_solution):
        result = list()
        for item in am_solution:
            circle = item['circle']
            for p in Solver.pairwise(circle):
                tmp = self.gf.get_unique_edge(p)
                if tmp in item['aq_set'] and p not in result and p[::-1] not in result:
                    result.append(p)
        return result

    def chromesome_partition(self, chromesome):
        '''
        transform the solution from chromesome format to partitioned solution optimally
        input: chromesome and graph
        output:
        '''
        # generate Auxiliary graph
        aux_graph = DiGraph()
        start_cost = list()
        end_cost = list()
        arc_cost = dict()
        aq_edges = list()
        pre_task = -1
        for idx, task in enumerate(chromesome):
            start_cost.append(
                self.gf.get_shortest_path(self.depot, task[0])[1])
            aq_edges.append(
                (self.gf[task[0]][task[1]]['cost'], self.gf[task[0]][task[1]]['demand']))
            end_cost.append(self.gf.get_shortest_path(task[1], self.gf)[1])
            if pre_task != -1:
                arc_cost[(idx - 1, idx)
                         ] = self.gf.get_shortest_path(pre_task, task[0])[1]
            pre_task = task[1]

        # print(start_cost, end_cost, arc_cost, edge_cost)
        for node1 in range(len(chromesome)):
            cost = start_cost[node1]
            load = 0
            for node2 in range(node1 + 1, len(chromesome) + 1):
                if load + aq_edges[node2 - 1][1] > self.capacity:
                    break
                load += aq_edges[node2 - 1][1]
                cost += aq_edges[node2 - 1][0]
                aux_graph.add_weighted_edge(
                    (node1, node2), cost + end_cost[node2 - 1])
                if node2 != len(chromesome):
                    cost += arc_cost[(node2 - 1, node2)]
                #print(node1, node2)
                # aux_graph.add_weighted_edge()

        result = aux_graph.get_shortest_path((0, len(chromesome)))
        partitioned = list()
        for pair in self.pairwise(result[0]):
            partitioned.append(chromesome[pair[0]:pair[1]])
        return partitioned

    @staticmethod
    def cxOrdered(x1, x2):
        """Executes an ordered crossover (OX) on the input
        individuals. The two individuals are modified in place. This crossover
        expects :term:`sequence` individuals of indices, the result for any other
        type of individuals is unpredictable.

        :param x1: The first individual participating in the crossover.
        :param x2: The second individual participating in the crossover.
        :returns: A tuple of two individuals.
        Moreover, this crossover generates holes in the input
        individuals. A hole is created when an attribute of an individual is
        between the two crossover points of the other individual. Then it rotates
        the element so that all holes are between the crossover points and fills
        them with the removed elements in order. For more details see
        [Goldberg1989]_.

        This function uses the :func:`~random.sample` function from the python base
        :mod:`random` module.

        .. [Goldberg1989] Goldberg. Genetic algorithms in search, 
        optimization and machine learning. Addison Wesley, 1989
        """
        ind1, ind2 = copy.copy(x1), copy.copy(x2)
        size = min(len(ind1), len(ind2))
        a, b = random.sample(xrange(size), 2)
        if a > b:
            a, b = b, a

        holes1, holes2 = set(), set()
        for i in range(size):
            if i < a or i > b:
                holes1.add(Graph.get_unique_edge(ind2[i]))
                holes2.add(Graph.get_unique_edge(ind1[i]))

        temp1, temp2 = ind1, ind2
        k1, k2 = b + 1, b + 1
        for i in range(size):
            if Graph.get_unique_edge(temp1[(i + b + 1) % size]) in holes1:
                ind1[k1 % size] = temp1[(i + b + 1) % size]
                k1 += 1

            if Graph.get_unique_edge(temp2[(i + b + 1) % size]) in holes2:
                ind2[k2 % size] = temp2[(i + b + 1) % size]
                k2 += 1

        # Swap the content between a and b (included)
        for i in range(a, b + 1):
            ind1[i], ind2[i] = ind2[i], ind1[i]

        return ind1, ind2

    def solution_verify(self, partitioned_solution):
        '''
        get the solution quality
        '''
        loadlist = list()
        costlist = list()
        for route in partitioned_solution:
            # costlist.append(route)
            load = 0
            cost = 0
            prev_task = None
            cost += self.gf.get_shortest_path(route[0][0], self.depot)[1]
            for task in route:
                # print(task)
                if prev_task is not None:
                    cost += self.gf.get_shortest_path(
                        prev_task[1], task[0])[1]
                load += self.gf[task[0]][task[1]]['demand']
                cost += self.gf[task[0]][task[1]]['cost']
                prev_task = task
            loadlist.append(load)
            cost += self.gf.get_shortest_path(
                route[-1][1], self.depot)[1]
            costlist.append(cost)
        # print(sum(loadlist))
        return loadlist, costlist, sum(costlist), sum(loadlist)
