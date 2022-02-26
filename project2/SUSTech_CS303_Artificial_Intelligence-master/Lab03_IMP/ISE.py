#!/usr/bin/env python2
# -*- coding=utf-8 -*-
'''
Entry file for Influence Spread Estimating ISE

i. Input: the format of the estimator call should be as follows:
python ISE.py –i <social network> -s <seed set> -m <diffusion
model> -b <termination type> -t <time budget> -r <random seed>
test python I
./ISE.py -i network.txt -s seeds.txt -m IC -b 0 -t 1 -r xxx
<social network> is the absolute path of the social network file
<seed set> is the absolute path of the seed set file
<diffusion model> can only be IC or LT
<termination type> specifies the termination manner and the value can
only be 0 or 1. If it is set to 0, the termination condition is as the same
defined in your algorithm. Otherwise, the maximal time budget specifies
the termination condition of your algorithm.
<time budget> is a positive number which indicates how many seconds
(in Wall clock time, range: [60s, 1200s]) your algorithm can spend on
this instance. If the <termination type> is 0, it still needs to accept -t
<time budget>, but can just ignore it while estimating.
<random seed> specifies the random seed used in this run. In case that
your solver is stochastic, the random seed controls all the stochastic
behaviors of your solver, such that the same random seeds will make
your solver produce the same results. If your solver is deterministic, it
still needs to accept –r <random seed>, but can just ignore them while
estimating.

ii. Output: the value of the estimated influence spread.

'''
import argparse
import logging
import time
import threading
import sys
from threading import Thread
import Queue as q2
from multiprocessing import Process, Queue
from utils.digraph import DiGraph
from utils.esitimater import Estimater

N_PROCESSORS = 8


def main():
    '''
    decode the parameters
    '''
    start = time.time()
    parser = argparse.ArgumentParser(
        description='Program for Influence Spread Computation\nCoded by Edward FANG')
    parser.add_argument('-i', metavar='social_network', type=argparse.FileType('r'),
                        required=True, help='the absolute path of the social network file')
    parser.add_argument('-s', metavar='seed_set', type=argparse.FileType('r'),
                        required=True, help='the absolute path of the seed set file')
    parser.add_argument('-m', metavar='diffusion_model',
                        required=True, help='can only be IC or LT')
    parser.add_argument('-b', metavar='termination_type', type=int,
                        required=True, help='specifies the termination manner')
    parser.add_argument('-t', metavar='time_budget', type=int,
                        help='allowed time for tha algorithm, in second')
    parser.add_argument('-r', metavar='random_seed',
                        help='random seed for stochastic algorithm')
    parser.add_argument('-d', help='debug mode', action="store_true")
    args = parser.parse_args()
    if args.d:
        logging.basicConfig(level=logging.DEBUG)
    graph = InfluenceNetwork()
    graph.load_from_file(args.i)
    seeds = loadseeds(args.s)
    termination_type = args.b
    time_limit = args.t
    logging.debug("%s, %s", termination_type, time_limit)
    args.i.close()
    args.s.close()
    random_seed = args.r
    estimaters = list()
    solution_receiver = Queue()
    results = [None] * N_PROCESSORS
    thread1 = solution_updater(
        solution_receiver, results)
    thread1.start()

    # multi processors processing
    for idx in range(N_PROCESSORS):
        if random_seed:
            unique_seed = random_seed + str(idx)
        else:
            unique_seed = None
        proc = Process(target=start_estimater, args=(
            graph, seeds, args.m, solution_receiver, idx, termination_type, unique_seed))
        estimaters.append(proc)
        proc.start()
        begin = (time.time() - start)

    if termination_type == 1 and time_limit is not None:
        # start a thread for timing
        thread2 = Thread(target=time_up_sig, args=(time_limit, begin, estimaters))
        thread2.daemon = True
        thread2.start()
    # exit
    for proc in estimaters:
        proc.join()
    thread1.stop()
    print(str(sum(results) / N_PROCESSORS))
    sys.stdout.flush()


def start_estimater(graph, seeds, mode, solution_receiver, processid, termination_type, random_seed):
    '''
    function to start new process
    '''
    est = Estimater(graph, seeds, mode, solution_receiver,
                    processid, termination_type, random_seed)
    est.estimate()


def time_up_sig(time_limit, start_time, solvers):
    '''
    terminate all procs when time is running out
    '''
    # print(time.time() - start_time)
    time.sleep(time_limit - start_time - 0.3 - time_limit * 0.01)

    for solver in solvers:
        solver.terminate()
    return


class solution_updater(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, solution_receiver, results):
        super(solution_updater, self).__init__()
        self._stop_event = threading.Event()
        self.solution_receiver = solution_receiver
        self.results = results

    def run(self):
        while not self._stop_event.is_set():
            try:
                new_result = self.solution_receiver.get(
                    block=True, timeout=0.1)
                self.results[new_result[0]] = new_result[1]
                # logging.debug(new_result)
            except q2.Empty:
                continue

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


class InfluenceNetwork(DiGraph):
    '''
    Inheritance from Digraph
    '''

    def __init__(self):
        DiGraph.__init__(self)
        self.spec = {'nodes': -1, 'edges': -1}

    def load_from_file(self, filed):
        '''
        load from the file
        '''
        lines = filed.readlines()
        self.spec['nodes'] = int(lines[0][0])
        self.spec['edges'] = int(lines[0][1])
        for line in lines[1:]:
            data = line.split()
            if len(data) == 3:
                self.add_weighted_edge(
                    (int(data[0]), int(data[1])), float(data[2]))


def loadseeds(filed):
    '''
    load seeds from the file
    '''
    seeds = set()
    lines = filed.readlines()
    for line in lines:
        data = line.split()
        if len(data) == 1:
            seeds.add(int(data[0]))
    return seeds


if __name__ == '__main__':
    main()
