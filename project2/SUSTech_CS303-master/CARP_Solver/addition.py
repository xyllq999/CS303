import copy
import random


# if pos == 0 and self.init.dis[i[1]][self.depot] < \
#         self.init.dis[min_dis_tuple[1]][self.depot]:
#     min_dis_tuple = i
# elif pos == 1 and self.init.dis[i[1]][self.depot] > \
#         self.init.dis[min_dis_tuple[1]][self.depot]:
#     min_dis_tuple = i
# elif pos == 2 and self.init.demand[i[1]][self.depot] \
#         / self.init.dis[i[1]][self.depot] \
#         < self.init.demand[min_dis_tuple[1]][self.depot] \
#         / self.init.dis[min_dis_tuple[1]][self.depot]:
#     min_dis_tuple = i
# elif pos == 3 and self.init.demand[i[1]][self.depot] \
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


# while len(self.deal_set) < self.require:
#     route = [0]
#     cost = 0
#     last_vis = self.depot
#     remain_cap = self.cap
#     while True:
#         min_dis_tuple = tuple()
#         min_dis = INF
#         for i in self.duty_list:
#             if ((i[0], i[1]) not in self.deal_set and (i[1], i[0]) not in self.deal_set) \
#                     and remain_cap >= self.init.demand[i[0]][i[1]]:
#                 if self.init.dis[last_vis][i[0]] < min_dis:
#                     min_dis_tuple = i
#                     min_dis = self.init.dis[last_vis][i[0]]
#                 elif self.init.dis[last_vis][i[0]] == min_dis:
#                     if self.init.dis[i[1]][self.depot] > self.init.dis[min_dis_tuple[1]][self.depot]:
#                         min_dis_tuple = i
#
#         if min_dis != INF:
#             last_vis = min_dis_tuple[1]
#             remain_cap -= self.init.demand[min_dis_tuple[0]][min_dis_tuple[1]]
#             route.append(min_dis_tuple[0])
#             route.append(min_dis_tuple[1])
#             self.deal_set.add(min_dis_tuple)
#             cost += min_dis + self.init.dis[min_dis_tuple[0]][min_dis_tuple[1]]
#         else:
#             cost += self.init.dis[last_vis][self.depot]
#             route.append(0)
#             self.solution.append(route)
#             self.total_cost += cost
#             break

# li = [0, (1, 5), (5, 10), (10, 20), 0, 0, (1, 2), (2, 4), 0]
# for i in range(len(li)):
#     if isinstance(li[i], tuple):
#         li[i] = '(%s,%s)' % (li[i][0], li[i][1])
# print(','.join(str(i) for i in li))

# def calc_route(solution, dis):
#     cost = 0
#     for route in solution:
#         cost += dis[depot][route[1][0]]
#         for i in range(1, len(route) - 1):
#             cost += dis[route[i][0]][route[i][1]]
#         for i in range(1, len(route) - 2):
#             cost += dis[route[i][1]][route[i+1][0]]
#         cost += dis[route[len(route) - 2][1]][depot]


# li = [[0, (1, 10), (10, 11), (11, 5), (5, 6), (6, 12), 0],
#       [0, (1, 4), (4, 2), (2, 9), (9, 10), (10, 8), 0],
#       [0, (1, 7), (7, 8), (8, 11), (11, 9), (2, 1), 0],
#       [0, (1, 12), (12, 5), (5, 3), (3, 2), (4, 3), 0],
#       [0, (12, 7), (7, 6), 0]]
# for route in li:
#     for i in range(1, len(route) - 1):
#         route[i] = (route[i][1], route[i][0])
#         calc_route()
#         route[i] = (route[i][1], route[i][0])
# print(li)

# li = [[0, (0, 1), (0, 2), 0], [0, (0, 3), (0, 4), (0, 5), 0], [0, (0, 6), 0]]
#
#
# _solution = copy.deepcopy(li)
# length = len(_solution)
# for i in range(length):
#     for j in range(1, len(_solution[i]) - 1):
#         for k in range(i, length):
#             if k == i:
#                 for l in range(j + 1, len(_solution[k]) - 1):
#                     print(i, j, k, l)
#                     this_solution = copy.deepcopy(_solution)
#                     x = this_solution[i][j]
#                     y = this_solution[k][l]
#                     this_solution[i][j] = y
#                     this_solution[k][l] = x
#                     print(this_solution)
#             else:
#                 for l in range(1, len(_solution[k]) - 1):
#                     print(i, j, k, l)
#                     this_solution = copy.deepcopy(_solution)
#                     x = this_solution[i][j]
#                     y = this_solution[k][l]
#                     this_solution[i][j] = y
#                     this_solution[k][l] = x
#                     print(this_solution)
class Addition1:
    def __init__(self):
        pass

    def print(self):
        print(random.randint(100))


class Addition:
    def __init__(self):
        self.a = Addition1


if __name__ == '__main__':
    solution = [
        [0, (1, 116), (116, 117), (117, 119), (117, 2), (118, 114), (114, 113), (113, 112), (112, 107), (107, 108),
         (108, 109), (107, 110), (110, 111), (110, 112), 0],
        [0, (11, 8), (8, 6), (6, 5), (8, 9), (13, 14), (12, 11), (27, 28), (28, 30), (30, 32), (28, 29), 0],
        [0, (66, 62), (62, 63), (63, 64), (64, 65), (56, 55), (55, 54), (55, 140), (140, 49), (49, 48), (139, 34),
         (44, 43), 0],
        [0, (87, 86), (86, 85), (85, 84), (84, 82), (82, 80), (80, 79), (79, 78), (78, 77), (77, 46), (46, 43),
         (43, 37), (37, 36), (36, 38), (38, 39), (39, 40), 0],
        [0, (95, 96), (96, 97), (97, 98), (139, 33), (33, 11), (11, 27), (27, 25), (25, 24), (24, 20), (20, 22),
         (12, 13), (124, 126), (126, 130), 0],
        [0, (107, 106), (106, 105), (105, 104), (104, 102), (66, 67), (67, 69), (69, 71), (71, 72), (72, 73), (73, 44),
         (44, 45), (45, 34), (67, 68), 0]]
    count = 0
    for route in solution:
        for i in range(1, len(route) - 1):
            count += 1
    print(count)
