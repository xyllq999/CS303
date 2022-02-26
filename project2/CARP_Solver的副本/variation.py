from Initialization import INF
import random
from Init_Solution_generator import Generator
import copy

li = [[0, (1, 10), (10, 11), (11, 5), (5, 6), (6, 12), 0],
      [0, (1, 4), (4, 2), (2, 9), (9, 10), (10, 8), 0],
      [0, (1, 7), (7, 8), (8, 11), (11, 9), (2, 1), 0],
      [0, (1, 12), (12, 5), (5, 3), (3, 2), (4, 3), 0],
      [0, (12, 7), (7, 6), 0]]


class Variation:
    def __init__(self, generator: Generator):
        self.gen = generator
        self.init = self.gen.init
        self.depot = self.gen.depot
        self.cap = self.gen.cap
        self.cur_cost = self.gen.total_cost

    # used for merge_split to redo the path_scanning work
    def path_scanning(self, solution):
        work_list = list()
        deal_set = set()
        cost = 0
        for route in solution:
            for i in range(1, len(route) - 1):
                work_list.append((route[i][0], route[i][1]))
                work_list.append((route[i][1], route[i][0]))
        require = len(work_list) // 2
        new_solution = list()
        while len(deal_set) < require:
            route = [0]
            last_vis = self.depot
            remain_cap = self.cap
            while True:
                min_dis_tuple = tuple()
                min_dis = INF
                reach_min_dis = INF
                for i in work_list:
                    if (i[0], i[1]) not in deal_set and (i[1], i[0]) not in deal_set:
                        if self.init.dis[last_vis][i[0]] < reach_min_dis:
                            reach_min_dis = self.init.dis[last_vis][i[0]]
                    if ((i[0], i[1]) not in deal_set and (i[1], i[0]) not in deal_set) \
                            and remain_cap >= self.init.demand[i[0]][i[1]]:
                        if self.init.dis[last_vis][i[0]] < min_dis:
                            min_dis_tuple = i
                            min_dis = self.init.dis[last_vis][i[0]]
                        elif min_dis != INF and self.init.dis[last_vis][i[0]] == min_dis:
                            choice = random.randint(0, 1)
                            if choice == 0:
                                min_dis_tuple = i
                            # pos = random.randint(0, 4)
                            # if pos == 0 and self.init.dis[i[1]][self.depot] < \
                            #         self.init.dis[min_dis_tuple[1]][self.depot]:
                            #     min_dis_tuple = i
                            # elif pos == 1 and self.init.dis[i[1]][self.depot] > \
                            #         self.init.dis[min_dis_tuple[1]][self.depot]:
                            #     min_dis_tuple = i
                            # elif pos == 2 and self.init.dis[i[1]][self.depot] != 0 \
                            #         and self.init.dis[min_dis_tuple[1]][self.depot] != 0 \
                            #         and self.init.dis[i[1]][self.depot] \
                            #         / self.init.dis[i[1]][self.depot] \
                            #         < self.init.demand[min_dis_tuple[1]][self.depot] \
                            #         / self.init.dis[min_dis_tuple[1]][self.depot]:
                            #     min_dis_tuple = i
                            # elif pos == 3 and self.init.demand[i[1]][self.depot] \
                            #         and self.init.dis[min_dis_tuple[1]][self.depot] != 0 \
                            #         and self.init.dis[i[1]][self.depot] \
                            #         / self.init.dis[i[1]][self.depot] \
                            #         > self.init.demand[min_dis_tuple[1]][self.depot] \
                            #         / self.init.dis[min_dis_tuple[1]][self.depot]:
                            #     min_dis_tuple = i
                            # elif pos == 4:
                            #     if remain_cap < self.cap / 2:
                            #         if self.init.dis[i[1]][self.depot] < \
                            #                 self.init.dis[min_dis_tuple[1]][self.depot]:
                            #             min_dis_tuple = i
                            #     else:
                            #         if self.init.dis[i[1]][self.depot] > \
                            #                 self.init.dis[min_dis_tuple[1]][self.depot]:
                            #             min_dis_tuple = i

                # if min_dis != INF and min_dis <= reach_min_dis + self.init.avg_total_cost \
                #         / (self.init.R_E + self.init.NR_E):
                if min_dis != INF and min_dis == reach_min_dis:
                    last_vis = min_dis_tuple[1]
                    remain_cap -= self.init.demand[min_dis_tuple[0]][min_dis_tuple[1]]
                    # route.append('(%d,%d)' % (min_dis_tuple[0], min_dis_tuple[1]))
                    route.append((min_dis_tuple[0], min_dis_tuple[1]))
                    deal_set.add(min_dis_tuple)
                    cost += min_dis + self.init.pure_dis[min_dis_tuple[0]][min_dis_tuple[1]]
                else:
                    cost += self.init.dis[last_vis][self.depot]
                    route.append(0)
                    new_solution.append(route)
                    # self.total_cost += cost
                    break
        return new_solution

    # return cost & solution pair
    def merge_split_init(self, sol):
        best_solution = []
        best_cost = INF
        for i in range(20):
            solution = self.merge_split(sol)
            cost_val = self.gen.solution_cost_calc(solution)
            if cost_val < best_cost:
                best_cost = cost_val
                best_solution = solution
        return best_cost, best_solution

    def merge_split(self, solution: list):
        _solution = copy.deepcopy(solution)
        if len(_solution) <= 2:
            return _solution
        change_solution = list()
        rand_a = random.randint(0, len(_solution) - 1)
        rand_b = random.randint(0, len(_solution) - 1)
        while rand_a == rand_b:
            rand_b = random.randint(0, len(_solution) - 1)
        change_solution.append(_solution.pop(max(rand_a, rand_b)))
        change_solution.append(_solution.pop(min(rand_a, rand_b)))
        scanned_solution = self.path_scanning(change_solution)
        for i in range(len(scanned_solution)):
            _solution.append(scanned_solution[i])
        return _solution

    # feasible?
    def single_insertion(self, solution: list):
        _solution = copy.deepcopy(solution)
        best_solution = []
        best_cost = INF
        for route_num in range(len(_solution)):
            for i in range(1, len(_solution[route_num]) - 1):
                this_solution = copy.deepcopy(_solution)
                tp = this_solution[route_num].pop(i)
                self.gen.eliminate_term(this_solution)
                for tp in (tp, (tp[1], tp[0])):
                    for mod_route_num in range(len(this_solution)+1):
                        if mod_route_num == len(this_solution):
                            this_mod_solution = copy.deepcopy(this_solution)
                            li = [0, 0]
                            li.insert(1, tp)
                            this_mod_solution.append(li)
                            self.gen.eliminate_term(this_mod_solution)
                            this_mod_cost = self.gen.solution_cost_calc(this_mod_solution)
                            if this_mod_cost < best_cost:
                                best_cost = this_mod_cost
                                best_solution = this_mod_solution
                        else:
                            for j in range(1, len(this_solution[mod_route_num])):
                                this_mod_solution = copy.deepcopy(this_solution)
                                this_mod_solution[mod_route_num].insert(j, tp)
                                self.gen.eliminate_term(this_mod_solution)
                                this_mod_cost = self.gen.solution_cost_calc(this_mod_solution)
                                if this_mod_cost < best_cost:
                                    best_cost = this_mod_cost
                                    best_solution = this_mod_solution

        return best_cost, best_solution

    # feasible?
    def double_insertion(self, solution: list):
        _solution = copy.deepcopy(solution)
        best_solution = []
        best_cost = INF
        for route_num in range(len(_solution)):
            for i in range(1, len(_solution[route_num]) - 2):
                this_solution = copy.deepcopy(_solution)
                tp1 = this_solution[route_num].pop(i+1)
                tp2 = this_solution[route_num].pop(i)
                self.gen.eliminate_term(this_solution)
                for tp1, tp2 in ((tp1, tp2), ((tp2[1], tp2[0]), (tp1[1], tp1[0]))):
                    for mod_route_num in range(len(this_solution) + 1):
                        if mod_route_num == len(this_solution):
                            this_mod_solution = copy.deepcopy(this_solution)
                            li = [0, 0]
                            li.insert(1, tp1)
                            li.insert(2, tp2)
                            this_mod_solution.append(li)
                            self.gen.eliminate_term(this_mod_solution)
                            this_mod_cost = self.gen.solution_cost_calc(this_mod_solution)
                            if this_mod_cost < best_cost:
                                best_cost = this_mod_cost
                                best_solution = this_mod_solution
                        else:
                            for j in range(1, len(this_solution[mod_route_num])):
                                this_mod_solution = copy.deepcopy(this_solution)
                                this_mod_solution[mod_route_num].insert(j, tp1)
                                this_mod_solution[mod_route_num].insert(j+1, tp2)
                                self.gen.eliminate_term(this_mod_solution)
                                this_mod_cost = self.gen.solution_cost_calc(this_mod_solution)
                                if this_mod_cost < best_cost:
                                    best_cost = this_mod_cost
                                    best_solution = this_mod_solution

        return best_cost, best_solution


if __name__ == '__main__':
    gen = Generator('egl-s1-A.dat')
    gen.generation()
    var = Variation(gen)
    print(gen.solution[0])
    li = [[0, (1, 116), (116, 117), (117, 2), (117, 119), (118, 114), (114, 113), (113, 112), (112, 110), (110, 107), (107, 106), 0], [0, (112, 107), (107, 108), (108, 109), (110, 111), (106, 105), (105, 104), (104, 102), 0], [0, (87, 86), (86, 85), (85, 84), (84, 82), (82, 80), (80, 79), (79, 78), (78, 77), (77, 46), (46, 43), (43, 37), (37, 36), (36, 38), (38, 39), (39, 40), 0], [0, (124, 126), (126, 130), (66, 67), (67, 68), (67, 69), (69, 71), (71, 72), (72, 73), (73, 44), (44, 45), (45, 34), 0], [0, (66, 62), (62, 63), (63, 64), (64, 65), (56, 55), (55, 54), (55, 140), (140, 49), (49, 48), (139, 34), (44, 43), 0], [0, (95, 96), (96, 97), (97, 98), (139, 33), (33, 11), (11, 27), (27, 25), (25, 24), (24, 20), (20, 22), (12, 13), 0], [0, (11, 8), (8, 6), (6, 5), (8, 9), (13, 14), (12, 11), (27, 28), (28, 30), (30, 32), (28, 29), 0]]
    print(gen.feasible_judge(li))
    print(gen.to_sol_form(gen.solution[0]))
    print(gen.solution_cost_calc(gen.solution[0]))
    m_c, m_s = var.merge_split_init(gen.solution[0])
    print(gen.to_sol_form(m_s))
    print(m_c)