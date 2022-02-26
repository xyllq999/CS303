import numpy as np
import random
import time

COLOR_BLACK = -1
COLOR_WHITE = 1
COLOR_NONE = 0
random.seed(0)


def find_color(chessboard, color):
    idxes = np.where(chessboard == color)
    return list(zip(idxes[0], idxes[1]))


class AI(object):
    start_time = 0
    time_no = False
    loc_chose = (0, 0)
    weight_list = (990, -40, 300, 200, -400, 4, 2, 5, 1, 0)

    direction = ((0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1))

    def __init__(self, chessboard_size, color, time_out):
        self.chessboard_size = chessboard_size
        self.color = color
        self.time_out = time_out
        self.no_time_left = False
        self.candidate_list = []
        self.value_for_action = 50
        self.value_for_weight = 2
        self.value_for_stable = 8
        self.value_for_edge = 25
        self.value_for_difference = 12
        self.corner_position = [(0, 1), (0, 6), (1, 0), (1, 7), (6, 0), (6, 7), (7, 1), (7, 6)]
        self.star_position = [(1, 1), (1, 6), (6, 1), (6, 6)]
        self.from_nw_to_se = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)]
        self.from_ne_to_sw = [(6, 1), (5, 2), (4, 3), (3, 4), (2, 5), (1, 6)]
        self.corner_side_position = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7),
                                     (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7),
                                     (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0),
                                     (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7)]
        self.weight_table = np.array([[990, -40, 300, 200, 200, 300, -40, 990],
                                      [-40, -400, 4, 2, 2, 4, -400, -40],
                                      [300, 4, 5, 1, 1, 5, 4, 300],
                                      [200, 2, 1, 0, 0, 1, 2, 200],
                                      [200, 2, 1, 0, 0, 1, 2, 200],
                                      [300, 4, 5, 1, 1, 5, 4, 300],
                                      [-40, -400, 4, 2, 2, 4, -400, -40],
                                      [990, -40, 300, 200, 200, 300, -40, 990]])

    def go(self, chessboard):
        # 测试出一个不超时方案
        self.start_time = time.time() - 1.2
        self.no_time_left = False
        self.candidate_list.clear()

        empty_loc = find_color(chessboard, COLOR_NONE)
        valid_locs, valid_move_directions = self.get_valid_moves(chessboard, self.color, empty_loc)
        self.candidate_list = valid_locs.copy()

        # # 如果只有一个点可行或者没有可以走的直接返回列表
        if (len(valid_locs) == 0) or (len(valid_locs) == 1):
            return self.candidate_list

        empty_loc_num = len(empty_loc)
        valid_move_count = len(valid_locs)

        if empty_loc_num > 53:
            depth = 1
        elif empty_loc_num > 13:
            depth = 2
        else:
            depth = 3

        if valid_move_count < 4:
            depth = 3
        elif valid_move_count < 8:
            depth = 2
        elif valid_move_count > 9:
            depth = 1

        loc_direction_value_list = []
        for i in range(valid_move_count):
            loc_direction_value_list.append([valid_locs[i], valid_move_directions[i], float('-inf')])

        for i in range(valid_move_count):
            # 对每一个可行点尝试下棋
            chessboard_after_move = self.move(chessboard.copy(), loc_direction_value_list[i][0], self.color,
                                              loc_direction_value_list[i][1])
            value, move = self.alphabeta_search(chessboard_after_move, depth - 1)
            print(loc_direction_value_list[i][0], value)
            if self.no_time_left:
                break
            loc_direction_value_list[i][2] = value

        loc_direction_value_list = sorted(loc_direction_value_list, key=lambda x: x[2], reverse=True)
        self.candidate_list.append(loc_direction_value_list[0][0])

        if loc_direction_value_list[0][2] == float('inf') or depth > 15:
            return self.candidate_list

        if time.time() - self.start_time > self.time_out:
            self.no_time_left = True
            return self.candidate_list

        depth += 1

    def alphabeta_search(self, chessboard, search_depth):
        """Search game to determine best action; use alpha-beta pruning.
        As in [Figure 5.7], this version searches all the way to the leaves."""

        def max_value(chessboard, alpha, beta, depth):

            empty_loc = find_color(chessboard, COLOR_NONE)
            this_move, this_direction = self.get_valid_moves(chessboard, self.color, empty_loc)
            if depth == 0:
                return self.get_evaluate_score(chessboard, self.color), None
            if len(this_move) == 0:
                this_move2, this_direction2 = self.get_valid_moves(chessboard, -self.color, empty_loc)
                if len(this_move2) == 0:
                    return self.get_evaluate_score(chessboard, self.color), None

                return min_value(chessboard, alpha, beta, depth)
            v, move = float('-inf'), None
            for i in range(len(this_move)):
                new_chessboard = self.move(chessboard.copy(), this_move[i], self.color, this_direction[i])
                v2, _ = min_value(new_chessboard, alpha, beta, depth - 1)
                if v2 > v:
                    v, move = v2, this_move[i]
                    alpha = max(alpha, v)
                if v >= beta:
                    return v, move
            return v, move

        def min_value(chessboard, alpha, beta, depth):

            empty_loc = find_color(chessboard, COLOR_NONE)
            this_move, this_direction = self.get_valid_moves(chessboard, -self.color, empty_loc)
            if depth == 0:
                return self.get_evaluate_score(chessboard, -self.color), None
            if len(this_move) == 0:
                this_move2, this_direction2 = self.get_valid_moves(chessboard, self.color, empty_loc)
                if len(this_move2) == 0:
                    return self.get_evaluate_score(chessboard, -self.color), None

                return max_value(chessboard, alpha, beta, depth)
            v, move = float('inf'), None
            for i in range(len(this_move)):
                new_chessboard = self.move(chessboard.copy(), this_move[i], -self.color, this_direction[i])
                v2, _ = max_value(new_chessboard, alpha, beta, depth - 1)
                # TODO: update *v*, *move* and *beta*
                if v2 < v:
                    v, move = v2, this_move[i]
                    beta = min(beta, v)
                if v <= alpha:
                    return v, move
            return v, move

        return min_value(chessboard.copy(), float('-inf'), float('inf'), search_depth)

    def alpha_beta_search(self, chessboard_after_move, color, search_depth, alpha, beta):
        if time.time() - self.start_time > self.time_out:
            self.no_time_left = True
            return alpha

        empty_loc = find_color(chessboard_after_move, COLOR_NONE)
        this_move, this_direction = self.get_valid_moves(chessboard_after_move, color, empty_loc)
        # 当搜索到双方都无子可以下,判断谁胜利，根据结果返回值

        # 相当于叶子节点
        if search_depth == 0:
            return self.evaluate(chessboard_after_move)

        index = 0
        for move in this_move:
            new_chessboard = self.move(chessboard_after_move.copy(), move, color, this_direction[index])
            index += 1
            self.loc_chose = move
            value = 0
            if move in self.corner_position:
                if self.do_lose_corner(chessboard_after_move, move):
                    value += 2000
            if move in self.star_position:
                if (move == (1, 1) or move == (6, 6)) and chessboard_after_move[0, 0] != self.color and \
                        chessboard_after_move[7, 7] != self.color:
                    for diagonal in self.from_nw_to_se:
                        if diagonal != move and new_chessboard[diagonal] != self.color:
                            value += 2800
                            break
                if (move == (1, 6) or move == (6, 1)) and chessboard_after_move[0, 7] != self.color and \
                        chessboard_after_move[7, 0] != self.color:
                    for diagonal in self.from_ne_to_sw:
                        if diagonal != move and new_chessboard[diagonal] != self.color:
                            value += 2800
                            break
            value = self.alpha_beta_search(new_chessboard, -color, search_depth - 1, -beta, -alpha)
            if value >= beta:
                return beta
            if value > alpha:
                alpha = value
        return alpha

    def evaluate(self, chessboard, end):
        value = 0
        for i in range(8):
            for j in range(8):
                value -= chessboard[i][j] * self.color * self.weight_table[i][j]
        return value

    def get_evaluate_score(self, chessboard, color):
        empty_loc = find_color(chessboard, COLOR_NONE)
        empty_loc_num = len(empty_loc)

        this_move_len = len(self.get_valid_moves(chessboard, self.color, empty_loc)[0])
        that_move_len = len(self.get_valid_moves(chessboard, -self.color, empty_loc)[0])
        if this_move_len == 0 and that_move_len == 0:
            evaluation = np.sum(chessboard) * self.color
            if evaluation > 0:
                return float('-inf')
            elif evaluation < 0:
                return float('inf')
            else:
                return 0

        my_move_num = len(self.get_valid_moves(chessboard, color, empty_loc)[0])
        your_move_num = len(self.get_valid_moves(chessboard, -color, empty_loc)[0])
        mobility = (my_move_num - your_move_num) * self.value_for_action

        weight_table_copy = self.weight_table.copy()
        if chessboard[0, 0] != COLOR_NONE:
            if chessboard[0, 0] == chessboard[1, 0]:
                weight_table_copy[1, 0] = 400
            if chessboard[0, 0] == chessboard[0, 1]:
                weight_table_copy[0, 1] = 400
            if chessboard[1, 1] == chessboard[0, 0] == chessboard[1, 0] == chessboard[0, 1]:
                weight_table_copy[1, 1] = 100
        if chessboard[7, 0] != COLOR_NONE:
            if chessboard[7, 1] == chessboard[7, 0]:
                weight_table_copy[7, 1] = 400
            if chessboard[6, 0] == chessboard[7, 0]:
                weight_table_copy[6, 0] = 400
            if chessboard[6, 1] == chessboard[7, 1] == chessboard[7, 0] == chessboard[6, 0]:
                weight_table_copy[6, 1] = 100
        if chessboard[0, 7] != COLOR_NONE:
            if chessboard[0, 6] == chessboard[0, 7]:
                weight_table_copy[0, 6] = 400
            if chessboard[1, 7] == chessboard[0, 7]:
                weight_table_copy[1, 7] = 400
            if chessboard[1, 7] == chessboard[0, 7] == chessboard[0, 6] == chessboard[1, 6]:
                weight_table_copy[1, 6] = 100
        if chessboard[7, 7] != COLOR_NONE:
            if chessboard[6, 7] == chessboard[7, 7]:
                weight_table_copy[6, 7] = 400
            if chessboard[7, 6] == chessboard[7, 7]:
                weight_table_copy[7, 6] = 400
            if chessboard[6, 7] == chessboard[7, 7] == chessboard[6, 6] == chessboard[7, 6]:
                weight_table_copy[6, 6] = 100

        my_number = 0
        your_number = 0

        my_edge = 0
        your_edge = 0

        my_stable = 0
        your_stable = 0

        for x in range(8):
            for y in range(8):
                if chessboard[x, y] == COLOR_NONE:
                    continue
                elif chessboard[x, y] == color:
                    my_number += 1
                    for direction in self.direction:
                        x_new = x + direction[0]
                        y_new = y + direction[1]
                        if 0 <= x_new <= 7 and 0 <= y_new <= 7 and chessboard[x_new, y_new] == COLOR_NONE:
                            your_edge += 1
                            break
                    if (x, y) in self.corner_side_position and self.check_if_stable(chessboard, x, y, color):
                        my_stable += 1
                else:
                    your_number += 1
                    for direction in self.direction:
                        x_new = x + direction[0]
                        y_new = y + direction[1]
                        if 0 <= x_new <= 7 and 0 <= y_new <= 7 and chessboard[x_new, y_new] == COLOR_NONE:
                            my_edge += 1
                            break
                    if (x, y) in self.corner_side_position and self.check_if_stable(chessboard, x, y, -color):
                        my_stable += 1

        edge = self.value_for_edge * (my_edge - your_edge)

        weight = np.sum(weight_table_copy * chessboard) * self.color * self.value_for_weight

        difference = (your_number - my_number) * self.value_for_difference

        stable = (my_stable - your_stable) * self.value_for_stable

        value = mobility + edge + weight + difference + stable
        return -value

    # 这个方法用于判断合法下子位置以及每个点可能的吃子位置和方向
    def get_eat_and_move(self, chessboard, color, valid_loc):
        eat_num = 0
        x, y = valid_loc
        valid_move_directions = []

        for direction in range(8):
            step = 1
            while (0 <= (x + (step + 1) * self.direction[direction][0]) < 8) and (
                    0 <= (y + (step + 1) * self.direction[direction][1]) < 8) and (
                    (chessboard[x + step * self.direction[direction][0]][
                        y + step * self.direction[direction][1]]) == -color):
                if color == chessboard[x + (step + 1) * self.direction[direction][0]][
                    y + (step + 1) * self.direction[direction][1]]:
                    eat_num += step
                    valid_move_directions.append(direction)
                    break
                step += 1
        return eat_num, valid_move_directions

    # 这个方法用于找到合法的走法，并调用get_eat_and_move,返回合法的走法和合法走法对应的吃子方向
    def get_valid_moves(self, chessboard, color, empty_loc):
        valid_move_direction = []
        valid_moves = []
        for valid_loc in empty_loc:
            eat_num, move_direction = self.get_eat_and_move(chessboard, color, valid_loc)
            if eat_num != 0:
                valid_moves.append(valid_loc)
                valid_move_direction.append(move_direction)
        return valid_moves, valid_move_direction

    # 移动一个位置的棋子后返回的新的棋盘
    def move(self, chessboard, valid_loc, my_color, valid_direction):
        chessboard[valid_loc] = my_color
        for direction in valid_direction:
            x = valid_loc[0] + self.direction[direction][0]
            y = valid_loc[1] + self.direction[direction][1]

            while chessboard[x][y] != my_color:
                chessboard[x][y] = my_color
                x = x + self.direction[direction][0]
                y = y + self.direction[direction][1]
        return chessboard

    def check_if_stable(self, chessboard, x, y, color):
        direction = [(1, 0), (1, 1), (0, 1), (-1, 1)]
        stable_direction_count = 0
        for dir in direction:
            check_blank = False
            check_your = False
            inc = 1
            while True:
                x_new = x + dir[0] * inc
                y_new = y + dir[1] * inc
                if 0 <= x_new <= 7 and 0 <= y_new <= 7:
                    if chessboard[x_new, y_new] == color:
                        pass
                    elif chessboard[x_new, y_new] == -color:
                        check_your = True
                    else:
                        check_blank = True
                        break
                    inc += 1
                else:
                    break
            if not check_your and not check_blank:
                stable_direction_count += 1
            elif check_your and not check_blank:
                inc = -1
                reverse_your_flag = False
                while True:
                    x_new = x + dir[0] * inc
                    y_new = y + dir[1] * inc
                    if 0 <= x_new <= 7 and 0 <= y_new <= 7:
                        if chessboard[x_new, y_new] == -color:
                            reverse_your_flag = True
                        elif chessboard[x_new, y_new] == COLOR_NONE:
                            if not reverse_your_flag:
                                return False
                            else:
                                break
                        else:
                            pass
                        inc -= 1
                    else:
                        break
                stable_direction_count += 1
            elif check_your and check_blank:
                inc = -1
                check_your_reverse = False
                while True:
                    x_new = x + dir[0] * inc
                    y_new = y + dir[1] * inc
                    if 0 <= x_new <= 7 and 0 <= y_new <= 7:
                        if chessboard[x_new, y_new] == COLOR_NONE:
                            if not check_your_reverse:
                                return False
                            else:
                                break
                        elif chessboard[x_new, y_new] == color:
                            pass
                        else:
                            check_your_reverse = True
                        inc -= 1
                    else:
                        break
                stable_direction_count += 1
            else:
                inc = -1
                while True:
                    x_new = x + dir[0] * inc
                    y_new = y + dir[1] * inc
                    if 0 <= x_new <= 7 and 0 <= y_new <= 7:
                        if chessboard[x_new, y_new] != color:
                            return False
                        inc -= 1
                    else:
                        break
                stable_direction_count += 1
        if stable_direction_count == 4:
            return True
        else:
            return False

    def do_lose_corner(self, chessboard, move):
        north_west = [(0, 1), (1, 0)]
        north_east = [(0, 6), (1, 7)]
        south_west = [(6, 0), (7, 1)]
        south_east = [(6, 7), (7, 6)]
        if move in north_west:
            if chessboard[0, 0] == self.color:
                return False
            elif chessboard[0, 0] == -self.color:
                x_new = 2 * move[0]
                y_new = 2 * move[1]
                if chessboard[x_new, y_new] == -self.color:
                    return False
                else:
                    return True
            else:
                x_inc = move[0]
                y_inc = move[1]
                x_new = move[0]
                y_new = move[1]
                my_counter = 0
                blank_counter = 0
                while True:
                    x_new += x_inc
                    y_new += y_inc
                    if 0 <= x_new <= 7 and 0 <= y_new <= 7:
                        if chessboard[x_new, y_new] == self.color:
                            my_counter += 1
                            if blank_counter % 2 == 1:
                                return True
                            else:
                                blank_counter = 0
                        elif chessboard[x_new, y_new] == -self.color:
                            return True
                        else:
                            blank_counter += 1
                    else:
                        break
                return False

        elif move in north_east:
            if chessboard[0, 7] == self.color:
                return False
            elif chessboard[0, 7] == -self.color:
                x_new = 2 * move[0] - 0
                y_new = 2 * move[1] - 7
                if chessboard[x_new, y_new] == -self.color:
                    return False
                else:
                    return True
            else:
                x_inc = move[0] - 0
                y_inc = move[1] - 7
                x_new = move[0]
                y_new = move[1]
                my_counter = 0
                blank_counter = 0
                while True:
                    x_new += x_inc
                    y_new += y_inc
                    if 0 <= x_new <= 7 and 0 <= y_new <= 7:
                        if chessboard[x_new, y_new] == self.color:
                            my_counter += 1
                            if blank_counter % 2 == 1:
                                return True
                            else:
                                blank_counter = 0
                        elif chessboard[x_new, y_new] == -self.color:
                            return True
                        else:
                            blank_counter += 1
                    else:
                        break
                return False
        elif move in south_west:
            if chessboard[7, 0] == self.color:
                return False
            elif chessboard[7, 0] == -self.color:
                x_new = 2 * move[0] - 7
                y_new = 2 * move[1] - 0
                if chessboard[x_new, y_new] == -self.color:
                    return False
                else:
                    return True
            else:
                x_inc = move[0] - 7
                y_inc = move[1] - 0
                x_new = move[0]
                y_new = move[1]
                my_counter = 0
                blank_counter = 0
                while True:
                    x_new += x_inc
                    y_new += y_inc
                    if 0 <= x_new <= 7 and 0 <= y_new <= 7:
                        if chessboard[x_new, y_new] == self.color:
                            my_counter += 1
                            if blank_counter % 2 == 1:
                                return True
                            else:
                                blank_counter = 0
                        elif chessboard[x_new, y_new] == -self.color:
                            return True
                        else:
                            blank_counter += 1
                    else:
                        break
                return False
        elif move in south_east:
            if chessboard[7, 7] == self.color:
                return False
            elif chessboard[7, 7] == -self.color:
                x_new = 2 * move[0] - 7
                y_new = 2 * move[1] - 7
                if chessboard[x_new, y_new] == -self.color:
                    return False
                else:
                    return True
            else:
                x_inc = move[0] - 7
                y_inc = move[1] - 7
                x_new = move[0]
                y_new = move[1]
                my_counter = 0
                blank_counter = 0
                while True:
                    x_new += x_inc
                    y_new += y_inc
                    if 0 <= x_new <= 7 and 0 <= y_new <= 7:
                        if chessboard[x_new, y_new] == self.color:
                            my_counter += 1
                            if blank_counter % 2 == 1:
                                return True
                            else:
                                blank_counter = 0
                        elif chessboard[x_new, y_new] == -self.color:
                            return True
                        else:
                            blank_counter += 1
                    else:
                        break
                return False


# import time
#
# a = time.time()
# board = np.array(
#     [[0, 0, 0, 0, 0, 0, 0, 0],
#      [0, 0, 0, 1, 0, 0, 0, 0],
#      [0, 0, 0, 1, 1, 0, 0, 0],
#      [1, 0, 0, 1, 1, 0, 0, 0],
#      [-1, 1, 1, 1, 1, 1, 1, 0],
#      [0, -1, 1, 0, 0, 0, 0, 0],
#      [-1, -1, -1, 1, 0, 0, 0, 0],
#      [0, 0, -1, 0, 0, 0, 0, 0]])
# ai = AI(8, 1, 100)
# ai.go(board)
# print(ai.candidate_list)
# b = time.time()  # 获取当前时间
# durn = (b - a)  # 两个时间差，并以秒显示出来
# print(durn)
