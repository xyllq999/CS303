# coding=utf-8
import copy
import random
import numpy as np
import sys
import time


# 读入dat文件并将数据存进一个list
def read_file(data_file):
    # 只读模式打开文件指针放在开头
    file = open(data_file, 'r')
    lines = file.readlines()
    # print(len(lines))
    line_index = 0
    data = []
    for line in lines:
        if line_index == 0:
            line = line.split()
            data.append(line[2])
            line_index += 1
        elif line_index <= 2 or line_index == 5 or line_index == 6:
            line = line.split()
            data.append(int(line[2]))
            line_index += 1
        elif line_index <= 4:
            line = line.split()
            data.append(int(line[3]))
            line_index += 1
        elif line_index == 7:
            line = line.split()
            data.append(int(line[6]))
            line_index += 1
        elif line_index == 8:
            line_index += 1
        elif 'END' in line:
            break
        else:
            edge = line.split()
            # print(edge)
            for i in range(len(edge)):
                edge[i] = int(edge[i])
            data.append(edge)
    # print(data)
    return data


# 计算需要清理的边
def cal_demand_edge(data):
    demand_edge_set = []
    # data数据的坐标8开始为边的数据
    for line in range(8, len(data)):
        # 当demand为0则将这一行加入set
        if data[line][3] != 0:
            demand_edge_set.append(data[line])
    return demand_edge_set


# 转化为邻接矩阵
def convert_matrix(data):
    adjacent_matrix = {}

    # 对数据8行到最后进行遍历
    for line in range(8, len(data)):
        node1 = data[line][0]
        node2 = data[line][1]
        cost = data[line][2]
        demand = data[line][3]
        # 分别判断两个nodes分别是否在矩阵中
        if node1 in adjacent_matrix:
            # 如果已经存在该nodes则取出来直接添加
            dic = adjacent_matrix[node1]
            dic[node2] = (cost, demand)
        else:
            dic = {node2: (cost, demand)}
            adjacent_matrix[node1] = dic

        if node2 in adjacent_matrix:
            dic = adjacent_matrix[node2]
            dic[node1] = (cost, demand)
        else:
            dic = {node1: (cost, demand)}
            adjacent_matrix[node2] = dic
    return adjacent_matrix


# 寻找任意两点间最短cost
def floyd(cost_demand_adjacent_matrix, vertices_num):
    matrix = np.full((vertices_num + 1, vertices_num + 1), np.inf)
    for i in range(1, vertices_num + 1):
        for j in range(1, vertices_num + 1):
            if i == j:
                matrix[i][j] = 0
    for i, value in cost_demand_adjacent_matrix.items():
        for j, cost in value.items():
            matrix[i][j] = cost[0]
    for k in range(vertices_num + 1):
        for i in range(vertices_num + 1):
            for j in range(vertices_num + 1):
                matrix[i][j] = min(matrix[i][j], matrix[i][k] + matrix[k][j])
    return matrix


def check_if_better(new_edge, edge, remain_capacity, min_cost_matrix, capacity, rule_index, exchange_order, depot):
    # 根据课件内容写path-scanning的五个规则
    function_list = [None, rule1, rule2, rule3, rule4, rule5]
    function = function_list[rule_index]
    return function(new_edge, edge, remain_capacity, min_cost_matrix, capacity, exchange_order, depot)


#  maximize the distance from the task to the depot
def rule1(new_edge, edge, remain_capacity, min_cost_matrix, capacity, exchange_order, depot):
    # 不存在直接加
    if edge is None:
        return True
    # 起点的位置到仓库或者终点的位置到仓库与之前比较
    if exchange_order:
        if min_cost_matrix[new_edge[0], depot] > min_cost_matrix[edge[1], depot]:
            return True
        else:
            return False
    else:
        if min_cost_matrix[new_edge[1], depot] > min_cost_matrix[edge[1], depot]:
            return True
        else:
            return False


#   minimize the distance from the task to the depot
def rule2(new_edge, edge, remain_capacity, min_cost_matrix, capacity, exchange_order, depot):
    # 不存在直接加
    if edge is None:
        return True
    # 起点的位置到仓库或者终点的位置到仓库与之前比较
    if exchange_order:
        if min_cost_matrix[new_edge[0], depot] < min_cost_matrix[edge[1], depot]:
            return True
        else:
            return False
    else:
        if min_cost_matrix[new_edge[1], depot] < min_cost_matrix[edge[1], depot]:
            return True
        else:
            return False


#   maximize the term dem(t)/sc(t), where dem(t) and sc(t) are demand and serving cost of task t, respectively;
def rule3(new_edge, edge, remain_capacity, min_cost_matrix, capacity, exchange_order, depot):
    # 不存在直接加
    if edge is None:
        return True
    new_rate = new_edge[3] / new_edge[2]
    prev_rate = edge[3] / edge[2]
    if new_rate > prev_rate:
        return True
    else:
        return False


#  minimize the term dem(t)/sc(t);
def rule4(new_edge, edge, remain_capacity, min_cost_matrix, capacity, exchange_order, depot):
    # 不存在直接加
    if edge is None:
        return True
    new_rate = new_edge[3] / new_edge[2]
    prev_rate = edge[3] / edge[2]
    if new_rate < prev_rate:
        return True
    else:
        return False


#   use rule 1) if the vehicle is less than half- full, otherwise use rule 2)
def rule5(new_edge, edge, remain_capacity, min_cost_matrix, capacity, exchange_order, depot):
    if edge is None:
        return True
    if remain_capacity < capacity / 2:
        return rule1(new_edge, edge, remain_capacity, min_cost_matrix, capacity, exchange_order, depot)
    else:
        return rule2(new_edge, edge, remain_capacity, min_cost_matrix, capacity, exchange_order, depot)


def remove_edge(demand_edge_set, edge):
    del_index = -1
    [start, end, _, _] = edge
    for index in range(len(demand_edge_set)):
        [start_node, end_node, _, _] = demand_edge_set[index]
        if (start_node == start and end_node == end) or (start_node == end and end_node == start):
            del_index = index
            break
    del demand_edge_set[del_index]


def path_scanning(set, min_cost_matrix, capacity, rule_index, depot):
    out_of_bounds = rule_index < 0 or rule_index > 5
    demand_edge_set = copy.deepcopy(set)
    route = []
    load_list = []
    cost_list = []
    while True:
        route_list = []
        load = 0
        cost = 0
        remain_capacity = capacity
        index = depot
        while True:
            distance = np.inf
            edge = None
            for new_edge in demand_edge_set:
                start_node, end_node, node_cost, node_demand = new_edge
                if out_of_bounds:
                    rule_index = random.randint(1, 5)
                if load + node_demand <= capacity:
                    # 考虑起点
                    if min_cost_matrix[index][start_node] < distance:
                        distance = min_cost_matrix[index][start_node]
                        edge = new_edge
                    elif min_cost_matrix[index][start_node] == distance and \
                            check_if_better(new_edge, edge, remain_capacity, min_cost_matrix, capacity, rule_index,
                                            False, depot):
                        edge = new_edge
                    # 考虑终点
                    if min_cost_matrix[index][end_node] < distance:
                        distance = min_cost_matrix[index][end_node]
                        edge = [end_node, start_node, node_cost, node_demand]
                    elif min_cost_matrix[index][end_node] == distance and \
                            check_if_better(new_edge, edge, remain_capacity, min_cost_matrix, capacity, rule_index,
                                            True, depot):
                        edge = [end_node, start_node, node_cost, node_demand]
                else:
                    continue
            # 如果找到了最好的边
            if edge is not None:
                [_, end_node, node_cost, node_demand] = edge
                route_list.append(edge)
                # print(route_list)
                remove_edge(demand_edge_set, edge)
                load += node_demand
                remain_capacity = capacity - load
                cost += (distance + node_cost)
                index = end_node
            # 如果所有demand边都遍历完或者没有合适的距离仍为Inf则结束
            if len(demand_edge_set) == 0 or (distance == np.inf):
                break
        cost += min_cost_matrix[index][depot]
        load_list.append(load)
        cost_list.append(cost)
        route.append(route_list)
        if len(demand_edge_set) == 0:
            break
    return route, load_list, cost_list


# 去掉cost和demand只保留边的起点终点信息
def simplify_edge(route):
    route_list = []
    for i in range(len(route)):
        line = []
        for j in range(len(route[i])):
            line.append([route[i][j][0], route[i][j][1]])
        route_list.append(line)
    return route_list


def inver_edge(edge):
    [start_node, end_node] = edge
    return [end_node, start_node]


def reverse_sub_route(sub_route):
    temp_sub_route = copy.deepcopy(sub_route)
    # 首先反向顺序
    temp_sub_route = temp_sub_route[::-1]
    # 然后将每一个edge反向
    for index in range(0, len(temp_sub_route)):
        temp_sub_route[index] = inver_edge(temp_sub_route[index])
    return temp_sub_route


class Path(object):
    def __init__(self, path, vehicles_num, capacity, depot):
        self.path = path
        self.total_cost = np.inf
        self.total_demand = np.inf
        self.cost_list = []
        self.demand_list = []
        self.legal = False
        self.vehicles_num = vehicles_num
        self.capacity = capacity
        self.depot = depot

    def __lt__(self, other):
        return self.total_cost < other.total_cost

    def is_legal(self):
        # 只要有一条路的demand超过了capacity直接返回不合法
        for demand in self.demand_list:
            if demand > self.capacity:
                self.legal = False
                return self.legal
        self.legal = True
        return self.legal

    def calculate_cost(self, min_cost_matrix, cost_demand_adjacent_matrix):
        self.cost_list = []
        self.demand_list = []
        self.total_cost = 0
        self.total_demand = 0
        for i in range(len(self.path)):
            temp_cost = 0
            temp_demand = 0
            prev_node = self.depot
            # 遍历每条线路经过的每条边
            # [[[8, 7], [7, 6], [6, 5]], [[2, 3], [3, 4]]] path样例
            for j in range(len(self.path[i])):
                start_node, end_node = self.path[i][j]
                temp_cost += (
                        min_cost_matrix[prev_node][start_node] + cost_demand_adjacent_matrix[start_node][end_node][
                    0])
                temp_demand += (cost_demand_adjacent_matrix[start_node][end_node][1])
                prev_node = end_node
            temp_cost += min_cost_matrix[prev_node][self.depot]
            self.cost_list.append(temp_cost)
            self.demand_list.append(temp_demand)
            self.total_cost += temp_cost
            self.total_demand += temp_demand

    def variation(self, variation_type):
        function = {
            1: self.flip,
            2: self.single_insertion,
            3: self.double_insertion,
            4: self.swap,
            5: self.variation_2_opt_single,
            6: self.variation_2_opt_double
        }
        vari = function[variation_type]
        return vari()

    def flip(self):
        after_vari_path = []
        if len(self.path) == 0:
            return None
        if len(self.path) == 1:
            vari_route_index = 0
        else:
            vari_route_index = random.randint(0, len(self.path) - 1)
        for index in range(0, len(self.path)):
            temp_route = copy.deepcopy(self.path[index])
            if index == vari_route_index:
                if len(temp_route) == 0:
                    return None
                if len(temp_route) == 1:
                    vari_edge_index = 0
                else:
                    vari_edge_index = random.randint(0, len(temp_route) - 1)
                edge = temp_route[vari_edge_index]
                inverse_edge = inver_edge(edge)
                temp_route.remove(edge)
                temp_route.insert(vari_edge_index, inverse_edge)
            after_vari_path.append(temp_route)
        return (after_vari_path,)

    # Try to insert each individual task after other tasks or depot in the same route or another route.
    def single_insertion(self):
        after_vari_path = []
        edge = None
        if len(self.path) == 0:
            return None
        if len(self.path) == 1:
            vari_route_index = 0
        else:
            vari_route_index = random.randint(0, len(self.path) - 1)
        for index in range(0, len(self.path)):
            temp_route = copy.deepcopy(self.path[index])
            if index == vari_route_index:
                if len(temp_route) == 0:
                    return None
                if len(temp_route) == 1:
                    vari_edge_index = 0
                else:
                    vari_edge_index = random.randint(0, len(temp_route) - 1)
                edge = temp_route[vari_edge_index]
                temp_route.remove(edge)
            after_vari_path.append(temp_route)
        if len(after_vari_path) == 1:
            vari_route_index = 0
        else:
            vari_route_index = random.randint(0, len(after_vari_path) - 1)
        temp_route = after_vari_path[vari_route_index]
        if len(temp_route) == 0:
            after_vari_path[vari_route_index] = [edge]
        else:
            vari_edge_index = random.randint(0, len(temp_route))
            temp_route.insert(vari_edge_index, edge)
        return (after_vari_path,)

    # Similar to the Single Insertion, two consecutive tasks try to be inserted after
    # other tasks or depot in the same route or another route.
    def double_insertion(self):
        after_vari_path = []
        if len(self.path) == 0:
            return None
        if len(self.path) == 1:
            vari_route_index = 0
        else:
            vari_route_index = random.randint(0, len(self.path) - 1)
        have_len3_route = False
        for index in range(0, len(self.path)):
            if len(self.path[index]) >= 3:
                have_len3_route = True
        if not have_len3_route:
            return None
        while len(self.path[vari_route_index]) < 3:
            vari_route_index = random.randint(0, len(self.path) - 1)
        change_edge1 = None
        change_edge2 = None
        for index in range(0, len(self.path)):
            temp_route = copy.deepcopy(self.path[index])
            if index == vari_route_index:
                vari_edge_index = random.randint(0, len(temp_route) - 2)
                change_edge1 = temp_route[vari_edge_index]
                change_edge2 = temp_route[vari_edge_index + 1]
                temp_route.remove(change_edge1)
                temp_route.remove(change_edge2)
            after_vari_path.append(temp_route)
        if len(self.path) == 0:
            return None
        if len(self.path) == 1:
            insert_route_index = 0
        else:
            insert_route_index = random.randint(0, len(self.path) - 1)
        temp_route = after_vari_path[insert_route_index]
        if len(temp_route) == 0:
            after_vari_path[insert_route_index] = [change_edge1, change_edge2]
        else:
            insert_edge_index = random.randint(0, len(temp_route))
            temp_route.insert(insert_edge_index, change_edge1)
            temp_route.insert(insert_edge_index + 1, change_edge2)
        return (after_vari_path,)

    def swap(self):
        after_swap_path = []
        if len(self.path) == 0:
            return None
        if len(self.path) == 1:
            vari_route_index1 = 0
            vari_route_index2 = 0
        else:
            vari_route_index1 = random.randint(0, len(self.path) - 1)
            vari_route_index2 = random.randint(0, len(self.path) - 1)
        edge1 = None
        edge2 = None
        vari_edge_index1 = None
        vari_edge_index2 = None
        for index in range(0, len(self.path)):
            temp_route = copy.deepcopy(self.path[index])
            if vari_route_index1 == index:
                if len(temp_route) == 0:
                    return None
                if len(temp_route) == 1:
                    vari_edge_index1 = 0
                else:
                    vari_edge_index1 = random.randint(0, len(temp_route) - 1)
                edge1 = copy.deepcopy(temp_route[vari_edge_index1])
            if vari_route_index2 == index:
                if len(temp_route) == 0:
                    return None
                if len(temp_route) == 1:
                    vari_edge_index2 = 0
                else:
                    vari_edge_index2 = random.randint(0, len(temp_route) - 1)
                edge2 = copy.deepcopy(temp_route[vari_edge_index2])
            after_swap_path.append(temp_route)
        after_swap_path[vari_route_index1][vari_edge_index1] = edge2
        after_swap_path[vari_route_index2][vari_edge_index2] = edge1
        return (after_swap_path,)

    # optimal for single route
    def variation_2_opt_single(self):
        after_vari_path = copy.deepcopy(self.path)
        if len(after_vari_path) == 0:
            return None
        if len(after_vari_path) == 1:
            vari_route_index = 0
        else:
            vari_route_index = random.randint(0, len(after_vari_path) - 1)
        # 1和2之间代表要翻转的部分
        if len(after_vari_path[vari_route_index]) <= 1:
            return None
        else:
            sub_route1 = random.randint(0, len(after_vari_path[vari_route_index]) - 1)
            sub_route2 = random.randint(0, len(after_vari_path[vari_route_index]) - 1)
        if sub_route1 == sub_route2:
            return None
        if sub_route1 > sub_route2:
            sub_route1, sub_route2 = sub_route2, sub_route1

        temp_route = copy.deepcopy(after_vari_path[vari_route_index])
        # 对序号和为sub1+sub2的边进行交换并且翻转
        for index in range(sub_route1, sub_route2 + 1)[::-1]:
            after_vari_path[vari_route_index][sub_route2 + sub_route1 - index] = inver_edge(temp_route[index])
        return (after_vari_path,)

    # optimal for double route
    def variation_2_opt_double(self):
        after_vari_path1 = []
        after_vari_path2 = []
        if len(self.path) <= 1:
            return None
        else:
            vari_route_index1 = random.randint(0, len(self.path) - 1)
            vari_route_index2 = random.randint(0, len(self.path) - 1)
        while vari_route_index2 == vari_route_index1:
            vari_route_index1 = random.randint(0, len(self.path) - 1)
            vari_route_index2 = random.randint(0, len(self.path) - 1)
        if len(self.path[vari_route_index1]) <= 1:
            return None
        if len(self.path[vari_route_index2]) <= 1:
            return None
        sub_index1 = random.randint(0, len(self.path[vari_route_index1]) - 1)
        sub_index2 = random.randint(0, len(self.path[vari_route_index2]) - 1)
        for index in range(0, len(self.path)):
            if index != vari_route_index1 and index != vari_route_index2:
                after_vari_path1.append(copy.deepcopy(self.path[index]))
                after_vari_path2.append(copy.deepcopy(self.path[index]))

        # 首先考虑ppt第一种情况PLAN1
        temp_route1 = copy.deepcopy(self.path[vari_route_index1][:sub_index1])
        temp_route2 = copy.deepcopy(self.path[vari_route_index2][sub_index2:])
        after_vari_path1.append(temp_route1 + temp_route2)

        temp_route1 = copy.deepcopy(self.path[vari_route_index2][:sub_index2])
        temp_route2 = copy.deepcopy(self.path[vari_route_index1][sub_index1:])
        after_vari_path1.append(temp_route1 + temp_route2)

        # 然后PLAN2
        temp_route1 = copy.deepcopy(self.path[vari_route_index1][:sub_index1])
        temp_route2 = reverse_sub_route(self.path[vari_route_index2][:sub_index2])
        after_vari_path2.append(temp_route1 + temp_route2)

        temp_route1 = reverse_sub_route(self.path[vari_route_index1][sub_index1:])
        temp_route2 = copy.deepcopy(self.path[vari_route_index2][sub_index2:])
        after_vari_path2.append(temp_route1 + temp_route2)

        return after_vari_path1, after_vari_path2

    # def fix_path(self, min_cost_matrix, cost_demand_adjacent_matrix, capacity, fixed_type, depot):
    #     fixed_path = []
    #     demand_edge_set = []
    #     load_list = []
    #     test = 0
    #     for route_index in range(0, len(self.path)):
    #         fixed_route = []
    #         temp_load = 0
    #         route_demand = 0
    #         for edge_index in range(0, len(self.path[route_index])):
    #             start_node, end_node = self.path[route_index][edge_index]
    #             demand = route_demand + cost_demand_adjacent_matrix[start_node][end_node][1]
    #             if demand <= capacity:
    #                 route_demand = demand
    #                 temp_load = demand
    #                 fixed_route.append([start_node, end_node])
    #             else:
    #                 route_demand = demand
    #                 node_cost = cost_demand_adjacent_matrix[start_node][end_node][0]
    #                 node_demand = cost_demand_adjacent_matrix[start_node][end_node][1]
    #                 demand_edge_set.append([start_node, end_node, node_cost, node_demand])
    #         load_list.append(temp_load)
    #         test += route_demand
    #         fixed_path.append(fixed_route)
    #
    #     # 如果修之后有空的route则删除掉
    #     while [] in fixed_path:
    #         fixed_path.remove([])
    #
    #     fixed_route_index = -1
    #     vari_out_bounds = fixed_type < 0 or fixed_type > 5
    #     while True:
    #         fixed_route_index += 1
    #         if fixed_route_index < len(fixed_path):
    #             route = fixed_path[fixed_route_index]
    #             # 取出最后一个edge的终点
    #             last_node = route[-1][1]
    #             load = load_list[fixed_route_index]
    #         else:
    #             route = []
    #             last_node = depot
    #             load = 0
    #         remain_space = capacity - load
    #
    #         while True:
    #             distance = np.inf
    #             edge = None
    #             for new_edge in demand_edge_set:
    #                 start_node, end_node, node_cost, node_demand = new_edge
    #                 if vari_out_bounds:
    #                     fixed_type = random.randint(1, 5)
    #                 if load + node_demand <= capacity:
    #                     # 考虑起点
    #                     if min_cost_matrix[last_node][start_node] < distance:
    #                         distance = min_cost_matrix[last_node][start_node]
    #                         edge = new_edge
    #                     elif min_cost_matrix[last_node][start_node] == distance and \
    #                             check_if_better(new_edge, edge, remain_space, min_cost_matrix, capacity, fixed_type,
    #                                             False, depot):
    #                         edge = new_edge
    #                     # 考虑终点
    #                     if min_cost_matrix[last_node][end_node] < distance:
    #                         distance = min_cost_matrix[last_node][end_node]
    #                         edge = [end_node, start_node, node_cost, node_demand]
    #                     elif min_cost_matrix[last_node][end_node] == distance and \
    #                             check_if_better(new_edge, edge, remain_space, min_cost_matrix, capacity, fixed_type,
    #                                             True, depot):
    #                         edge = [end_node, start_node, node_cost, node_demand]
    #                 else:
    #                     continue
    #             # 如果找到了最好的边
    #             if edge is not None:
    #                 start_node, end_node, _, node_demand = edge
    #                 route.append([start_node, end_node])
    #                 remove_edge(demand_edge_set, edge)
    #                 load += node_demand
    #                 remain_space = capacity - load
    #                 last_node = end_node
    #
    #             # 如果所有demand边都遍历完或者没有合适的距离仍为Inf则结束
    #             if len(demand_edge_set) == 0 or (distance == np.inf):
    #                 break
    #
    #         if fixed_route_index < len(load_list):
    #             load_list[fixed_route_index] = load
    #         else:
    #             load_list.append(load)
    #             fixed_path.append(route)
    #
    #         if len(demand_edge_set) == 0:
    #             break
    #     return fixed_path


class pathGroup:
    def __init__(self, select_size, variation_size, min_cost_matrix, cost_demand_adjacent_matrix, depot):
        self.select_size = select_size
        self.variation_size = variation_size
        self.min_cost_matrix = min_cost_matrix
        self.path_list = []
        self.is_mature = False
        self.cost_demand_adjacent_matrix = cost_demand_adjacent_matrix
        self.depot = depot

    def init_path_group(self, origin_size, demand_edge_set, min_cost_matrix, vehicles_num, capacity,
                        cost_demand_adjacent_matrix):
        # 根据给定的车辆数量得到暗示的路径数量
        for rule_index in range(1, origin_size + 1):
            path, load_list, cost_list = path_scanning(demand_edge_set, min_cost_matrix, capacity, rule_index,
                                                       self.depot)
            simple_path = simplify_edge(path)

            new_path = Path(simple_path, vehicles_num, capacity, self.depot)
            new_path.calculate_cost(min_cost_matrix, cost_demand_adjacent_matrix)
            # 添加前判断是否合法（有无超过容量的demand)
            self.add_new_path(new_path)

    def make_immature(self):
        self.is_mature = False

    # 如果合法则将路径添加到list
    def add_new_path(self, new_path):
        if new_path.is_legal():
            self.path_list.append(new_path)

    def select(self):
        self.path_list.sort()
        self.path_list = self.path_list[:self.select_size]

    def print_results(self):
        self.select()
        best_ans = self.path_list[0]
        best_path = best_ans.path
        # print(best_path)
        path_ans = "s "
        for i in range(len(best_path)):
            path_ans += "0,"
            for j in range(len(best_path[i])):
                path_ans += "({},{}),".format(best_path[i][j][0], best_path[i][j][1])
            if i == len(best_path) - 1:
                path_ans += "0"
            else:
                path_ans += "0,"
        print(path_ans)
        print("q {}".format(int(best_ans.total_cost)))

    def generate(self, variation_type, vehicles, capacity):
        new_list = []
        variation_size = self.variation_size
        while variation_size > 0:
            choose_index = random.randint(0, len(self.path_list) - 1)
            variation_path_list = self.path_list[choose_index].variation(variation_type)
            if variation_path_list is None:
                continue
            # print(len(variation_path_list))
            for path in variation_path_list:
                new_path = Path(path, vehicles, capacity, self.depot)
                new_path.calculate_cost(self.min_cost_matrix, self.cost_demand_adjacent_matrix)
                if new_path.is_legal():
                    new_list.append(new_path)
                    variation_size -= 1
                # else:
                #     fixed_type = random.randint(1, 6)
                #     new_path_fixed = new_path.fix_path(self.min_cost_matrix, self.cost_demand_adjacent_matrix, capacity, fixed_type, self.depot)
                #     fixed_path = Path(new_path_fixed, vehicles, capacity, self.depot)
                #     fixed_path.calculate_cost(self.min_cost_matrix, self.cost_demand_adjacent_matrix)
                #     if fixed_path.is_legal():
                #         new_list.append(fixed_path)
                #         variation_size -= 1
        # print("生成")
        self.path_list.extend(new_list)

    def resize(self, path_size):
        self.path_list.sort()
        self.path_list = self.path_list[:path_size]

    def check_mature(self):
        route_cost = []
        for route in self.path_list:
            route_cost.append(route.total_cost)

        count_cost_dic = {}
        for cost in route_cost:
            if route_cost.count(cost) > 1:
                count_cost_dic[cost] = route_cost.count(cost)

        if len(count_cost_dic) == 1:
            self.is_mature = True
        return self.is_mature


def solve_carp(data_file, termination, seed):
    start_time = time.time()
    data = read_file(data_file)
    vertices_num = data[1]
    depot = data[2]
    # print(depot)
    vehicles = data[5]
    capacity = data[6]
    # print(data)
    random.seed(seed)
    demand_edge = cal_demand_edge(data)
    # print(demand_edge)
    # 将边存进矩阵，双向存入，矩阵值为cost
    cost_demand_adjacent_matrix = convert_matrix(data)
    # print(cost_demand_adjacent_matrix)
    min_cost_matrix = floyd(cost_demand_adjacent_matrix, vertices_num)
    # print(min_cost_matrix)
    # 使用遗传算法计算
    paths = pathGroup(300, 900, min_cost_matrix, cost_demand_adjacent_matrix, depot)
    paths.init_path_group(3000, demand_edge, min_cost_matrix, vehicles, capacity, cost_demand_adjacent_matrix)
    paths.select()
    run_time = time.time() - start_time

    end_time = termination - 5
    # paths.print_results()
    while run_time <= end_time:
        if paths.check_mature():
            # 如果已经成熟了采用变异方法5, 6
            variation_type = random.randint(5, 6)
            # 所有大于1的cost只有一种所以只保留5种并且重新开始生成新的种群
            paths.resize(6)
            paths.make_immature()
        else:
            # 如果还没有成熟则采用随机方法
            variation_type = random.randint(1, 6)
            paths.make_immature()
        paths.generate(variation_type, vehicles, capacity)
        paths.select()
        # print("继续")
        run_time = time.time() - start_time
    # print("结束")
    paths.print_results()


if __name__ == "__main__":
    # print(sys.argv)
    data_file = sys.argv[1]
    termination = sys.argv[3]
    termination = int(termination)
    seed = sys.argv[5]
    solve_carp(data_file, termination, seed)
