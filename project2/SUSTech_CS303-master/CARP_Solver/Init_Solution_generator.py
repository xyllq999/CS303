from Initialization import Pre_work, INF
import sys
import random
import time
import copy


class Generator:
    def __init__(self, pw):
        self.init = pw
        self.solution = []
        self.depot = -1
        self.v = 0
        self.cap = 0
        self.require = 0
        self.duty_list = list()
        self.deal_set = set()
        # self.total_cost = []
        self.total_cost = INF

    def generation(self, seed=None):
        if seed is not None:
            random.seed(seed)
        # self.init.scan_graph()
        # self.init.floyd()
        self.v = self.init.V
        self.depot = self.init.info_map['DEPOT']
        self.cap = self.init.info_map['CAPACITY']
        self.require = self.init.info_map['REQUIRED EDGES']
        for i in range(1, self.v + 1):
            for j in range(1, self.v + 1):
                if self.init.demand[i][j] > 0:
                    self.duty_list.append((i, j))
        for times in range(1000):
            self.deal_set.clear()
            cost = 0
            solution = list()
            while len(self.deal_set) < self.require:
                route = [0]
                last_vis = self.depot
                remain_cap = self.cap
                while True:
                    min_dis_tuple = tuple()
                    min_dis = INF
                    reach_min_dis = INF
                    for i in self.duty_list:
                        if (i[0], i[1]) not in self.deal_set and (i[1], i[0]) not in self.deal_set:
                            if self.init.dis[last_vis][i[0]] < reach_min_dis:
                                reach_min_dis = self.init.dis[last_vis][i[0]]
                        if ((i[0], i[1]) not in self.deal_set and (i[1], i[0]) not in self.deal_set) \
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
                        self.deal_set.add(min_dis_tuple)
                        cost += min_dis + self.init.pure_dis[min_dis_tuple[0]][min_dis_tuple[1]]
                    # elif random.random() < 0.01 * self.init.demand[min_dis_tuple[0]][min_dis_tuple[1]] / \
                    #         self.init.dis[last_vis][min_dis_tuple[0]] / self.cap:
                    else:
                        cost += self.init.dis[last_vis][self.depot]
                        route.append(0)
                        solution.append(route)
                        # self.total_cost += cost
                        break
            if cost < self.total_cost:
                self.total_cost = cost
                self.solution = solution
            # self.solution.append(solution)
            # self.total_cost.append(cost)

    def feasible_judge(self, solution):
        for route in solution:
            route_cost = 0
            for j in range(1, len(route) - 1):
                route_cost += self.init.demand[route[j][0]][route[j][1]]
            if route_cost > self.cap:
                return False
        return True

    def eliminate_term(self, solution):
        for i in range(len(solution)-1, -1, -1):
            if len(solution[i]) == 2:
                solution.pop(i)

    def solution_cost_calc(self, solution):
        cost = 0
        for route in solution:
            if len(route) > 2:
                cost += self.init.dis[self.depot][route[1][0]]
                for i in range(1, len(route) - 1):
                    cost += self.init.pure_dis[route[i][0]][route[i][1]]
                for i in range(1, len(route) - 2):
                    cost += self.init.dis[route[i][1]][route[i + 1][0]]
                cost += self.init.dis[route[len(route) - 2][1]][self.depot]
        return cost

    def to_sol_form(self, solution):
        # print(solution)
        res = list()
        _solution = copy.deepcopy(solution)
        for route in _solution:
            for i in range(len(route)):
                if isinstance(route[i], tuple):
                    route[i] = '(%s,%s)' % (route[i][0], route[i][1])
            res.append(','.join(str(i) for i in route))
        res = ','.join(res)
        return res


# if __name__ == '__main__':
#     # print(sys.argv[1])
#     gen = Generator('egl-s1-A.dat')
#     # gen.generation(sys.argv[5])
#     gen.generation()
#     print('s ', end='')
#     print(gen.solution)
#     print(gen.to_sol_form(gen.solution))
#     # ans_li = []
#     # for j in gen.solution[0]:
#     #     ans_li.append(','.join(str(i) for i in j))
#     # ans_li = ','.join(ans_li)
#     # print(ans_li)
#     # print(''.join(str(i) for i in gen.solution[0]))
#     # print(''.join(''.join(str(i) for i in gen.solution[0])))
#     print('q ', end='')
#     print(gen.solution_cost_calc(gen.solution))

