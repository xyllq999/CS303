import numpy as np
import random
import time

COLOR_BLACK = -1
COLOR_WHITE = 1
COLOR_NONE = 0
random.seed(2)

chess_type = {
    # win
    "AAAAA": 50000,
    # live_four
    "?AAAA?": 4320,
    # dead_four1
    "AAAA?": 730,
    "?AAAA": 730,
    # live_three
    "?AAA??": 730,
    "??AAA?": 730,
    # dead_four2
    "AAA?A": 710,
    "A?AAA": 710,
    # dead_four3
    "AA?AA": 710,
    # dead_three
    "?A?AA?": 710,
    "?AA?A?": 710,
    # live_two
    "??AA??": 120,
    "A?A?A": 120,
    "AAA??": 120,
    "??AAA": 120,
    # dead_two
    # "?A?A??": 110,
    # "??A?A?": 110,
    "???A??": 20,
    "??A???": 20
    }


# don't change the class name
class AI(object):
    # chessboard_size, color, time_out passed from agent
    def __init__(self, chessboard_size, color, time_out):
        self.chessboard_size = chessboard_size
        # You are white or black
        self.color = color
        # the max time you should use, your algorithm's run time must not exceed the time limit.
        self.time_out = time_out
        # You need add your decision into your candidate_list. System will get the end of your candidate_list as your decision .
        self.candidate_list = []

    # The input is current chessboard.
    def go(self, chessboard):
        # Clear candidate_list
        self.candidate_list.clear()
        # ==================================================================
        # To write your algorithm here
        point_value = {}
        options = []
        # style
        k1 = 6
        k2 = 4
        can = self.candidate(chessboard)
        if len(can) == 0:
            idx = np.where(chessboard == COLOR_NONE)
            idx = list(zip(idx[0], idx[1]))
            if len(idx) == 0:
                return
            new_pos = (self.chessboard_size//2, self.chessboard_size//2)
        else:
            for c in can:
                if chessboard[c[0], c[1]] == 0:
                    value_self = self.check(chessboard, c[0], c[1], self.color)
                    value_enemy = self.check(chessboard, c[0], c[1], -self.color)
                    point_value[c] = k1 * value_self + k2 * value_enemy
            # random choice
            if not point_value:
                return
            sorted_list = sorted(point_value.items(), key=lambda d: d[1], reverse=True)
            v = sorted_list[0][1]
            # print(sorted_list)
            for s in sorted_list:
                if s[1] == v:
                    options.append(s[0])
                else:
                    break
            new_pos = random.choice(options)
            # print(new_pos)
            # print(chessboard)
        assert chessboard[new_pos[0], new_pos[1]] == 0
        self.candidate_list.append(new_pos)

    # valuable empty positions
    def candidate(self, chessboard):
        empty = set()
        idx = np.where(chessboard == COLOR_NONE)
        idx = list(zip(idx[0], idx[1]))
        if len(idx) < pow(self.chessboard_size, 2)//5:
            idx = np.where(chessboard == COLOR_NONE)
            empty = set(zip(idx[0], idx[1]))
            return empty
        for emp in idx:
            square = chessboard[max(0,emp[0]-2):min(self.chessboard_size,emp[0]+3),max(0,emp[1]-2):min(self.chessboard_size,emp[1]+3)]
            zero = np.full(np.shape(square), COLOR_NONE, dtype=int)
            if not np.array_equal(square, zero):
                empty.add(emp)
        return empty

    def check(self, chessboard, i, j, color):
        value = 0
        warn = 0
        temp = 0
        # check column
        code = "A"
        for x in range(i-1, -1, -1):
            if chessboard[x, j] == -color:
                break
            elif chessboard[x, j] == 0:
                code = "?" + code
            else:
                code = "A" + code
        for x in range(i + 1, self.chessboard_size):
            if chessboard[x, j] == -color:
                break
            elif chessboard[x, j] == 0:
                code = code + "?"
            else:
                code = code + "A"
        for key in chess_type:
            if key in code:
                value += chess_type[key]
                if chess_type[key] > 500:
                    warn += 1
                    temp += chess_type[key]
                # value += code.count("A") * 2 + code.count("?") * 1
                code = code.replace(key, "")
        # check row
        code = "A"
        for x in range(j-1, -1, -1):
            if chessboard[i, x] == -color:
                break
            elif chessboard[i, x] == 0:
                code = "?" + code
            else:
                code = "A" + code
        for x in range(j + 1, self.chessboard_size):
            if chessboard[i, x] == -color:
                break
            elif chessboard[i, x] == 0:
                code = code + "?"
            else:
                code = code + "A"
        for key in chess_type:
            if key in code:
                value += chess_type[key]
                if chess_type[key] > 500:
                    warn += 1
                    temp += chess_type[key]
                # value += code.count("A") * 2 + code.count("?") * 1
                code = code.replace(key, "")
        # check left diagonal
        code = "A"
        x = i
        y = j
        while x > 0 and y > 0:
            x -= 1
            y -= 1
            if chessboard[x, y] == -color:
                break
            elif chessboard[x, y] == 0:
                code = "?" + code
            else:
                code = "A" + code
        x = i
        y = j
        while x < self.chessboard_size-1 and y < self.chessboard_size-1:
            x += 1
            y += 1
            if chessboard[x, y] == -color:
                break
            elif chessboard[x, y] == 0:
                code = code + "?"
            else:
                code = code + "A"
        for key in chess_type:
            if key in code:
                value += chess_type[key]
                if chess_type[key] > 500:
                    warn += 1
                    temp += chess_type[key]
                # value += code.count("A") * 2 + code.count("?") * 1
                code = code.replace(key, "")
        # check right diagonal
        code = "A"
        x = i
        y = j
        while x < self.chessboard_size-1 and y >0:
            x += 1
            y -= 1
            if chessboard[x, y] == -color:
                break
            elif chessboard[x, y] == 0:
                code = "?" + code
            else:
                code = "A" + code
        x = i
        y = j
        while x > 0 and y < self.chessboard_size-1:
            x -= 1
            y += 1
            if chessboard[x, y] == -color:
                break
            elif chessboard[x, y] == 0:
                code = code + "?"
            else:
                code = code + "A"
        for key in chess_type:
            if key in code:
                value += chess_type[key]
                if chess_type[key] > 500:
                    warn += 1
                    temp += chess_type[key]
                # value += code.count("A") * 2 + code.count("?") * 1
                code = code.replace(key, "")
        # if warn > 1:
        #     value += temp
        return value


