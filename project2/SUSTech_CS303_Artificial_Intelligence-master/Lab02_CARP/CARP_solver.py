#!/usr/bin/env python2
# -*- coding=utf-8 -*-
'''
This Program is used to solve the CARP problem in a limited time.
'''
import argparse
import numpy as np
from utils.solver import Solver
from utils.graph import Graph
import Queue as q2
from multiprocessing import Process, Queue
from threading import Thread
import threading
import os
import time


N_PROCESSORS = 1


class bestSolution(object):
    def __init__(self):
        self.best_solution = None
        self.fitness = float('inf')

    def update(self, new_solution):
        if new_solution[1] < self.fitness:
            self.fitness = new_solution[1]
            self.best_solution = new_solution[0]
            # print("update", self.fitness)

    def __str__(self):
        result = 's '
        for route in self.best_solution:
            if len(route) == 0:
                continue
            result += '0,'
            for task in route:
                result += '(%d,%d),' % task
            result += '0,'
        cost_total = self.fitness
        result = result[:-1] + '\n'
        result += 'q %d' % cost_total
        return result


def main():
    '''
    main entrance
    '''
    start = time.time()
    parser = argparse.ArgumentParser(
        description='Find Solutions for CARP Problem\nCoded by Edward FANG')
    parser.add_argument('instance', type=argparse.FileType('r'),
                        help='filename for CARP instance')
    parser.add_argument('-t', metavar='termination', type=int,
                        help='termination time limit', required=True)
    parser.add_argument('-s', metavar='random seed',
                        help='random seed for stochastic algorithm')
    args = parser.parse_args()
    time_limit = args.t
    seed = args.s
    instance_file = args.instance
    # print(time_limit, seed)
    spec, data = read_instance_file(instance_file)
    network = Graph()
    network.load_from_data(data.tolist())
    solvers = list()
    solution_receiver = Queue()
    best_solution = bestSolution()
    thread1 = solution_updater(
        solution_receiver, best_solution)
    thread1.start()
    # multi processors processing
    for idx in range(N_PROCESSORS):
        if seed:
            unique_seed = seed + str(idx)
        else:
            unique_seed = None
        proc = Process(target=start_solver, args=(
            network, spec, unique_seed, solution_receiver))
        solvers.append(proc)
        proc.start()
        # run_time = (time.time() - start)

    # start a thread for timing
    thread2 = Thread(target=time_up_sig, args=(time_limit, start, solvers))
    thread2.daemon = True
    thread2.start()
    # exit
    for proc in solvers:
        proc.join()
    thread1.stop()
    print(str(best_solution))


def time_up_sig(time_limit, start_time, solvers):
    '''
    terminate all procs when time is running out
    '''
    # print(time.time() - start_time)
    time.sleep(time_limit - 0.3 - time_limit * 0.01)

    for solver in solvers:
        solver.terminate()
    return


class solution_updater(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, solution_receiver, best_solution):
        super(solution_updater, self).__init__()
        self._stop_event = threading.Event()
        self.solution_receiver = solution_receiver
        self.best_solution = best_solution

    def run(self):
        while not self._stop_event.is_set():
            try:
                new_solution = self.solution_receiver.get(
                    block=True, timeout=0.1)
                self.best_solution.update(new_solution)
            except q2.Empty:
                continue

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


def start_solver(network, spec, seed, best_solution):
    '''
    function to start new process
    '''
    solver = Solver(network, spec, seed, best_solution)
    solver.solve()


def read_instance_file(filedesc):
    '''
    ::param: filename: string, filename that indicates the location of instance data file
    ::return value: (specification, data)
    :: specification: dict, specification of the instance
    :: data: the numpy array with a list of edges and their cost, demand
    :: data: [vertex1 vertex2 cost demand]
    '''
    content = filedesc.readlines()
    content = [x.strip() for x in content]
    specification = dict()
    for i in range(8):
        line = content[i].split(':')
        specification[line[0].strip()] = line[1].strip()
    # print(specification)
    data = list()
    for line in content[9:-1]:
        tmp = line.split()
        data.append([int(x.strip()) for x in tmp])
    data = np.array(data)
    filedesc.close()
    return specification, data


if __name__ == '__main__':
    main()
