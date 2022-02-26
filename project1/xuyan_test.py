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
    direction = ((0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1))

    def __init__(self, chessboard_size, color, time_out):
        self.chessboard_size = chessboard_size
        self.color = color
        self.time_out = time_out
        self.no_time_left = False
        self.candidate_list = []
        self.depth = 5
        self.weight_table = np.array([[500, 5, 25, 15, 15, 25, 5, 500],
                                      [5, -100, 1, 1, 1, 1, -100, 25],
                                      [25, 1, 3, 2, 2, 3, 1, 25],
                                      [15, 1, 2, 1, 1, 2, 1, 15],
                                      [15, 1, 2, 1, 1, 2, 1, 15],
                                      [25, 1, 3, 2, 2, 3, 1, 25],
                                      [5, -100, 1, 1, 1, 1, -100, 5],
                                      [500, 5, 25, 15, 15, 25, 5, 500]])

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
        valid_move_count = len(self.candidate_list)
        loc_direction_ear_list = []
        for i in range(valid_move_count):
            loc_direction_ear_list.append([valid_locs[i], valid_move_directions[i], float('-inf')])
        max_value = -9999999
        for i in range(valid_move_count):
            # 对每一个可行点尝试下棋
            chessboard_after_move = self.move(chessboard.copy(), loc_direction_ear_list[i][0], self.color,
                                              loc_direction_ear_list[i][1])
            value, move = self.alphabeta_search(chessboard_after_move, self.depth - 1)
            print(loc_direction_ear_list[i][0], value)
            if max_value < value:
                max_value = value
                self.candidate_list.append(loc_direction_ear_list[i][0])

    def alphabeta_search(self, chessboard, search_depth):
        """Search game to determine best action; use alpha-beta pruning.
        As in [Figure 5.7], this version searches all the way to the leaves."""

        def max_value(chessboard, alpha, beta, depth):
            empty_loc = find_color(chessboard, COLOR_NONE)
            this_move, this_direction = self.get_valid_moves(chessboard, self.color, empty_loc)
            if depth == 0:
                return self.evaluate(chessboard), None
            if len(this_move) == 0:
                this_move2, this_direction2 = self.get_valid_moves(chessboard, -self.color, empty_loc)
                if len(this_move2) == 0:
                    return self.evaluate(chessboard), None

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
                return self.evaluate(chessboard), None
            if len(this_move) == 0:
                this_move2, this_direction2 = self.get_valid_moves(chessboard, self.color, empty_loc)
                if len(this_move2) == 0:
                    return self.evaluate(chessboard), None

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

    def evaluate(self, chessboard):
        value = 0
        for i in range(8):
            for j in range(8):
                value -= chessboard[i][j] * self.color * self.weight_table[i][j]
        return value

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

import time
a = time.time()
board = np.array(
    [[0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 1, 0, 0, 0, 0],
     [0, 0, 0, 1, 1, 0, 0, 0],
     [1, 0, 0, 1, 1, 0, 0, 0],
     [-1, 1, 1, 1, 1, 1, 1, 0],
     [0, -1, 1, 0, 0, 0, 0, 0],
     [-1, -1, -1, 1, 0, 0, 0, 0],
     [0, 0, -1, 0, 0, 0, 0, 0], ])
ai = AI(8, 1, 100)
ai.go(board)
print(ai.candidate_list)
b = time.time()  # 获取当前时间
durn = (b - a)# 两个时间差，并以秒显示出来
print(durn)
