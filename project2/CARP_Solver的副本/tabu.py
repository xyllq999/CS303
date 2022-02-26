import time
from Initialization import Pre_work, INF
import random
from Init_Solution_generator import Generator
from variation import Variation
import copy
import math
import sys


class Tabu_Search:
    def __init__(self, pw):
        self.start = time.time()
        self.gen = Generator(pw)
        self.gen.generation()
        # print(self.gen.solution, self.gen.total_cost)
        self.var = Variation(self.gen)
        self.p = 2
        self.N = self.gen.init.R_E
        self.current_cost, self.current_solution = self.var.merge_split_init([], self.p, INF, INF, self.gen.solution)
        self.current_cost = self.var.object_eva(self.current_cost, self.p,
                                                self.current_solution)
        self.gen.eliminate_term(self.current_solution)
        self.current_solution.sort()
        self.best = self.current_solution  # in spite of feasible or infeasible
        self.best_cost = self.current_cost
        self.best_feasible = self.current_solution
        self.best_feasible_cost = self.current_cost
        self.tabu_list = []
        self.tabu_list_length = self.N // 6
        self.k = 0  # iteration counter
        self.k_b = 0  # iteration number since best solution before intensification
        # self.k_l = 8 * self.N  # number of iterations for applying intensification
        self.k_l = 1
        self.k_bf = 0  # iteration number since best feasible solution
        self.k_f = 0  # iteration number of consecutive feasible solution
        self.k_i = 0  # iteration number of consecutive infeasible solution
        self.k_bt = 0  # iterations since best solution in total
        self.f_si = 1
        self.f_di = 2
        self.f_sw = 2
        self.keep_len = 3
        self.init_time = time.time() - self.start

    def search(self, timelimit):
        timelimit -= self.init_time + 2
        # end = time.time()
        # print(end - start)
        while True:
            # print('k: %d' % self.k)
            time_start_round = time.time()
            best_solution = []
            best_cost = INF
            best_sw_cost, best_sw_solution = self.var.swap(self.tabu_list, self.p, self.best_feasible_cost,
                                                           self.best_cost, self.current_solution)
            # print(best_sw_solution == self.current_solution)
            # print('SW %d %d' % (best_sw_cost, self.best_feasible_cost))
            if best_sw_cost < best_cost:
                best_cost = best_sw_cost
                best_solution = best_sw_solution
            best_si_cost, best_si_solution = self.var.single_insertion(self.tabu_list, self.p, self.best_feasible_cost,
                                                                       self.best_cost, self.current_solution)
            # print('SI %d %d' % (best_si_cost, self.best_feasible_cost))
            # print(best_si_solution == self.current_solution)
            if best_si_cost < best_cost:
                best_cost = best_si_cost
                best_solution = best_si_solution
            best_di_cost, best_di_solution = self.var.double_insertion(self.tabu_list, self.p, self.best_feasible_cost,
                                                                       self.best_cost, self.current_solution)
            # print('DI %d %d' % (best_sw_cost, self.best_feasible_cost))
            # print(best_di_solution == self.current_solution)
            if best_di_cost < best_cost:
                best_cost = best_di_cost
                best_solution = best_di_solution
            best_ms_cost, best_ms_solution = self.var.merge_split_init(self.tabu_list, self.p, self.best_feasible_cost,
                                                                       self.best_cost, self.current_solution)
            # print(best_ms_solution == self.current_solution)
            # print('MS %d %d' % (best_sw_cost, self.best_feasible_cost))
            if best_ms_cost < best_cost:
                best_cost = best_ms_cost
                best_solution = best_ms_solution
            self.gen.eliminate_term(best_solution)
            best_solution.sort()
            if len(self.tabu_list) == self.tabu_list_length:
                self.tabu_list.pop(0)
            self.tabu_list.append(best_solution)
            if best_cost == INF:
                return self.gen.to_sol_form(self.best_feasible), self.gen.solution_cost_calc(self.best_feasible)
            else:
                if best_cost < self.best_feasible_cost and self.gen.feasible_judge(best_solution):
                    self.best_feasible = best_solution
                    self.best_feasible_cost = best_cost
                if best_cost < self.best_cost:
                    self.best = best_solution
                    self.best_cost = best_cost
                self.current_solution = best_solution
                self.current_cost = best_cost
                if self.gen.feasible_judge(best_solution):
                    if self.k_i != 0:
                        self.k_i = 0
                    self.k_f += 1
                else:
                    if self.k_f != 0:
                        self.k_f = 0
                    self.k_i += 1
                if self.k_f == self.keep_len:
                    self.p = self.p / 2
                    self.best_cost = self.var.object_eva(self.gen.solution_cost_calc(best_solution), self.p, best_solution)
                elif self.k_i == self.keep_len:
                    self.p = self.p * 2
                    self.best_cost = self.var.object_eva(self.gen.solution_cost_calc(best_solution), self.p, best_solution)
                if self.k_f == self.keep_len or self.k_i == self.keep_len:
                    self.best_cost = self.var.object_eva(self.gen.solution_cost_calc(best_solution), self.p, best_solution)
                    self.k_f = 0
                    self.k_i = 0
                self.k += 1
                if self.p >= 16 or self.p <= 0.25:
                    self.current_solution = self.best_feasible
                    self.current_cost = self.best_feasible_cost
                # print('---------------')
                # print('best cost: %d, p: %d' % (self.best_cost, self.p))
                # print('s ', end='')
                # print(tabu.gen.to_sol_form(self.best_feasible))
                # print('q ', end='')
                # print(tabu.gen.solution_cost_calc(self.best_feasible))
                # print('---------------')
                round_time = time.time() - time_start_round
                if (self.k >= 900 * math.ceil(math.sqrt(self.N)) and self.k_bf >= 10 * self.N) or self.k_bt == 2 * self.k_l \
                        or time.time() - self.start > timelimit - round_time:
                    # print(time.time() - start)
                    return self.gen.to_sol_form(self.best_feasible), self.gen.solution_cost_calc(self.best_feasible)

#
# if __name__ == '__main__':
#     start = time.time()
#     tabu = Tabu_Search(sys.argv[1])
#     timelimit = int(sys.argv[3])
#     random.seed(sys.argv[5])
#     tabu.search(timelimit - 15)
#     print('s ', end='')
#     print(tabu.gen.to_sol_form(tabu.best_feasible))
#     print('q ', end='')
#     print(tabu.gen.solution_cost_calc(tabu.best_feasible))
#     print(time.time() - start)
#     # todo 记得优化, 使用判断是否可行先判断，不可行再计算penalty
#     # todo 计算cost时，即为使用 total_cost + max(w(i) - Q)
