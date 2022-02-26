#!/usr/bin/env python2
'''
Task 2: influence maximization
i. Input: the format of the solver call should be as follows:
python IMP -i <social network> -k <predefined size of the seed set>
-m <diffusion model> -b <termination type> -t <time budget> -r
<random seed>
<social network> is the absolute path of the social network file
<predefined size of the seed set> is a positive integer
<diffusion model> can only be IC or LT
<termination type> specifies the termination options and the value can
only be 0 or 1. If it is set to 0, the termination condition is as the same
defined in your algorithm. Otherwise, the maximal time budget specifies
the termination condition of your algorithm.
<time budget> is a positive number which indicates how many seconds
(in Wall clock time, range: [60s, 1200s]) your algorithm can spend on
this instance. If the <termination type> is 0, it still needs to accept -t
<time budget>, but can just ignore it while solving IMPs.
<random seed> specifies the random seed used in this run. In case that
your solver is stochastic, the random seed controls all the stochastic
behaviors of your solver, such that the same random seeds will make
your solver produce the same results. If your solver is deterministic, it
still needs to accept -r <random seed>, but can just ignore them while
solving IMP.
ii. Output: the seed set found by your algorithm.
The format of the seed set output should be as follows: each line contains
a node index. An example is also included in the package.
'''
import argparse
import logging
import time
import random
from utils.solver import Solver
from utils.digraph import DiGraph


def main():
    '''
    decode the parameters
    '''
    start_time = time.time()
    parser = argparse.ArgumentParser(
        description='Program for Influence Spread Computation\nCoded by Edward FANG')
    parser.add_argument('-i', metavar='social_network', type=argparse.FileType('r'),
                        required=True, help='the absolute path of the social network file')
    parser.add_argument('-k', metavar='seed_set_size', type=int,
                        required=True, help='predefined size of the seed set')
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
    # logging.debug(args)
    graph = InfluenceNetwork()
    graph.load_from_file(args.i)
    args.i.close()
    time_limit = -1
    if args.b == 1:
        time_limit = args.t
    if args.r:
        random.seed(args.r)
    imp_solver = Solver(graph, args.m, time_limit -
                        time.time() + start_time - 0.3, args.r, args.k)
    imp_solver.solve()
    # implement multiple algorithm and choose them according
    # to the size of the problem and the time limit


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


if __name__ == '__main__':
    main()
