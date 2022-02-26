
def simulated_annealing(self, s):
    init_temp = 20
    n = len(s) * len(s) * 10
    size_factor = 8
    cut_off = 0.2
    temp_factor = 0.95
    find_divisor = 50
    cur_temp = 20
    ans_s = s
    print(s)
    ans_q = self.check(s)
    print(ans_q)
    while cur_temp > init_temp / find_divisor:
        trials = changes = 0
        while trials < size_factor * n and changes < cut_off * n:
            trials += 1
            temp_s = self.generate(s)
            res = self.check(temp_s)
            if res > 0:
                print(res)
                if res < ans_q or random.random() < math.e ** ((ans_q - res) / cur_temp):
                    s = temp_s
                    print(s)
                    changes += 1
                    if res < ans_q:
                        ans_s = temp_s
                        ans_q = res
        cur_temp = cur_temp * temp_factor


# def search(self):
#     start = time.time()
#     while True:
#         adm_sol_list = []
#         best_solution = []
#         best_cost = INF
#         if self.k % self.f_sw == 0:
#             best_sw_cost, best_sw_solution, adm_list = self.var.swap(self.tabu_list, self.p,
#                                                                      self.best_feasible_cost,
#                                                                      self.best_cost, self.current_solution)
#             if best_sw_cost < best_cost:
#                 best_cost = best_sw_cost
#                 best_solution = best_sw_solution
#             adm_sol_list += adm_list
#         if self.k % self.f_si == 0:
#             best_si_cost, best_si_solution, adm_list = self.var.single_insertion(self.tabu_list, self.p,
#                                                                                  self.best_feasible_cost,
#                                                                                  self.best_cost,
#                                                                                  self.current_solution)
#             if best_si_cost < best_cost:
#                 best_cost = best_si_cost
#                 best_solution = best_si_solution
#             adm_sol_list += adm_list
#         if self.k % self.f_di == 0:
#             best_di_cost, best_di_solution, adm_list = self.var.double_insertion(self.tabu_list, self.p,
#                                                                                  self.best_feasible_cost,
#                                                                                  self.best_cost,
#                                                                                  self.current_solution)
#             if best_di_cost < best_cost:
#                 best_cost = best_di_cost
#                 best_solution = best_di_solution
#             adm_sol_list += adm_list
#         ###
#         # update tabu list
#         ###
#         best_solution.sort()
#         if len(self.tabu_list) == self.tabu_list_length:
#             self.tabu_list.pop(0)
#         self.tabu_list.append(best_solution)
#         ###
#         # update
#         ###
#         if best_cost < self.best_feasible_cost and self.gen.feasible_judge(best_solution):
#             self.best_feasible = best_solution
#             self.best_feasible_cost = best_cost
#             self.k_b = 0
#             self.k_bf = 0
#             self.k_bt = 0
#         if best_cost < self.best_cost:
#             self.best = best_solution
#             self.best_cost = best_cost
#             self.k_b = 0
#             self.k_bt = 0
#         self.k += 1
#         self.k_b += 1
#         self.k_bf += 1
#         self.k_bt += 1
#         # if self.k % self.keep_len == 0:
#         #     if self.k_f == self.keep_len:
#         #         print('/')
#         #         self.p = self.p / 2
#         #     elif self.k_i == self.keep_len:
#         #         print('*')
#         #         self.p = self.p * 2
#         if self.k_f == self.keep_len:
#             print('/')
#             self.p = self.p / 2
#         elif self.k_i == self.keep_len:
#             print('*')
#             self.p = self.p * 2
#         if self.k_f == self.keep_len or self.k_i == self.keep_len:
#             self.best_cost = self.var.object_eva(self.gen.solution_cost_calc(best_solution), self.p, best_solution)
#             self.k_f = 0
#             self.k_i = 0
#         if self.gen.feasible_judge(best_solution):
#             print('feasible')
#             if self.k_i != 0:
#                 self.k_i = 0
#             self.k_f += 1
#         else:
#             print('infeasible')
#             if self.k_f != 0:
#                 self.k_f = 0
#             self.k_i += 1
#         ###
#         # change parameter
#         ###
#         if self.k_b == self.k_l // 2:
#             self.f_si = 2
#             self.f_di = 1
#             self.f_sw = 2
#         ###
#         # intensification
#         ###
#         if self.k_b == self.k_l:
#             # if self.best_feasible_cost < INF:
#             #     self.current_solution = self.best_feasible
#             # else:
#             #     self.current_solution = self.best
#             self.current_solution = self.best
#             self.k_b = 0
#             self.p = 1
#             self.k_f = 0
#             self.k_i = 0
#             self.f_si = 1
#             self.f_di = 2
#             self.f_sw = 2
#             self.k_l = self.k_l + 2 * self.N
#             self.best_cost = self.var.object_eva(self.gen.solution_cost_calc(best_solution), self.p, best_solution)
#             self.tabu_list.clear()
#         ###
#         # stop criterion
#         ###
#         print(self.k)
#         print(self.best_feasible)
#         print(self.best_feasible_cost)
#         print(self.best_cost)
#         print(self.p)
#         if (self.k >= 900 * math.ceil(math.sqrt(self.N)) and self.k_bf >= 10 * self.N) or self.k_bt == 2 * self.k_l \
#                 or time.time() - start > 200:
#             break