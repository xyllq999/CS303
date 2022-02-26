#!/usr/bin/env python2
'''
This program is used as subprocess for the solver to get the Monto-Carlo results
'''
from __future__ import division
import random
import logging
from multiprocessing import Process


class Evaluator(Process):
    '''
    evaluator for multi-processing
    ::params: task_queue (id, seeds, round)
    result_queue (id, result)
    id = -1 => exit
    '''

    def __init__(self, graph, model, task_queue, result_queue, random_seed):
        '''
        input the global paras
        '''
        super(Evaluator, self).__init__(target=self.start)
        self.graph = graph
        self.model = model
        self.task_queue = task_queue
        self.result_queue = result_queue
        model_map = {'IC': self.ic_evaluate, 'LT': self.lt_evaluate}
        self.evaluate = model_map[model]
        self.random_seed = random_seed

    def run(self):
        '''
        start to retrive tasks from task_queue
        '''
        random.seed(self.random_seed)
        # logging.debug(random.random())
        while True:
            # logging.debug("getting tasks")
            new_task = self.task_queue.get()
            if new_task[0] == -1:
                exit(0)
            result = self.evaluate(new_task[1], new_task[2])
            self.result_queue.put((new_task[0], result))

    def ic_evaluate(self, seeds, sim_round):
        '''
        evaluate based on independent cascade model
        '''
        cnt = 0
        for _ in range(sim_round):
            activated = set()
            next_layer = set(seeds)
            while next_layer:
                activated = set.union(activated, next_layer)
                new_layer = set()
                for node in next_layer:
                    for linked_node, value in self.graph[node].iteritems():
                        if linked_node not in activated and random.random() < value['weight']:
                            new_layer.add(linked_node)
                next_layer = new_layer
            cnt += len(activated)
        return cnt / sim_round

    def lt_evaluate(self, seeds, sim_round):
        '''
        method to evaluate Linear Threshold model
        '''
        cnt = 0
        '''
        flag = 100
        prev = 0
        '''
        for _ in range(sim_round):
            activated = set(seeds)
            threshold = dict()
            for node in self.graph.vertices():
                threshold[node] = random.random()

            def get_nextround(changed_vertices):
                '''
                get influenced vertices
                '''
                next_round = set()
                for vertex in changed_vertices:
                    next_round = set.union(
                        next_round, set(self.graph[vertex].keys()))
                return next_round
            next_round = get_nextround(activated)
            while next_round:
                changed_vertices = set()
                for node in next_round:
                    indicator = 0
                    for linked_node, value in self.graph.inverse[node].iteritems():
                        if linked_node in activated:
                            indicator += value['weight']
                    if indicator > threshold[node]:
                        changed_vertices.add(node)
                        activated.add(node)
                next_round = get_nextround(changed_vertices)
            num_activated = len(activated)
            cnt += num_activated
            '''
            current = cnt / (idx + 1)
            difference = abs(current - prev)
            prev = current
            # if idx % 1000 == 0:
            #     logging.debug(difference)
            if difference < 0.03:
                flag -= 1
                if flag == 0:
                    logging.debug(idx)
                    break
            '''
        return cnt / sim_round
