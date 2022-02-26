COLOR_BLACK = -1
COLOR_WHITE = 1
COLOR_NONE = 0


class AI(object):
    def __init__(self, chessboard_size, color, time_out):
        self.chessboard_size = chessboard_size
        self.color = color
        self.time_out = time_out
        self.candidate_list = []

    def go(self, chessboard):
        self.candidate_list.clear()
        b = self.parse(chessboard)
        s = Searcher(self.chessboard_size, b)
        p = tuple()
        if self.color == -1:
            p = s.deter(1, 1)
        else:
            p = s.deter(2, 1)
        self.candidate_list.append(p)
        # print(p)

    def parse(self, chessboard):
        sz = self.chessboard_size
        board = [[0 for i in range(sz)] for j in range(sz)]
        for i in range(sz):
            for j in range(sz):
                if chessboard[i][j] == -1:
                    board[i][j] = 1
                elif chessboard[i][j] == 1:
                    board[i][j] = 2
        return board


class Evaluator(object):
    def __init__(self, chessboard_size):
        self.cb_sz = chessboard_size
        self.positions = []
        for i in range(self.cb_sz):  # 给棋盘划分层，最外为0，向内increment
            row = [self.cb_sz // 2 - max(abs(i - self.cb_sz // 2), abs(j - self.cb_sz // 2)) for j in range(self.cb_sz)]
            self.positions.append(tuple(row))
        self.positions = tuple(self.positions)
        self.r_2 = 1  # 冲二
        self.r_3 = 2  # 冲三
        self.r_4 = 3  # 冲四
        self.l_2 = 4  # 活二
        self.l_3 = 5  # 活三
        self.l_4 = 6  # 活四
        self.l_5 = 7  # 活五
        self.over = 255
        self.todo = 0
        self.result = [0 for i in range(self.cb_sz)]
        self.line = [0 for i in range(self.cb_sz)]
        self.record = [[[0, 0, 0, 0] for i in range(15)] for j in range(15)]
        # 记录水平，垂直，左斜，右斜
        self.count = [[0 for i in range(10)] for i in range(3)]
        self.reset()

    def reset(self):
        todo = self.todo
        count = self.count
        for i in range(self.cb_sz):
            line = self.record[i]
            for j in range(self.cb_sz):
                for k in range(4):
                    line[j][k] = todo
        for i in range(10):
            for j in range(3):
                count[j][i] = 0
        return 0

    def evaluate(self, board, turn):
        score = self.__evaluate(board, turn)
        count = self.count
        if score < -9000:
            stone = turn == 1 and 2 or 1
            for i in range(10):
                if count[stone][i] > 0:
                    score -= i
        elif score > 9000:
            stone = turn == 1 and 2 or 1
            for i in range(10):
                if count[stone][i] > 0:
                    score += i
        return score

    def __evaluate(self, board, turn):
        record, count = self.record, self.count
        todo, over = self.todo, self.over
        self.reset()
        for i in range(self.cb_sz):
            boardrow = board[i]
            recordrow = record[i]
            for j in range(self.cb_sz):
                if boardrow[j] != 0:
                    if recordrow[j][0] == todo:
                        self.evaluate_horizon(board, i, j)
                    if recordrow[j][1] == todo:
                        self.evaluate_vertical(board, i, j)
                    if recordrow[j][2] == todo:
                        self.evaluate_left_diag(board, i, j)
                    if recordrow[j][3] == todo:
                        self.evaluate_right_diag(board, i, j)

        p = [self.l_5, self.l_4, self.l_3, self.l_2, self.r_4, self.r_3, self.r_2]
        for i in range(self.cb_sz):
            for j in range(self.cb_sz):
                stone = board[i][j]
                if stone != 0:
                    for k in range(4):
                        ch = record[i][j][k]
                        if ch in p:
                            count[stone][ch] += 1

        return self.detailed_eva(turn, count, board)

    def detailed_eva(self, color, count, board):
        _l_5, _l_4, _l_3, _l_2 = self.l_5, self.l_4, self.l_3, self.l_2
        _r_4, _r_3, _r_2 = self.r_4, self.r_3, self.r_2
        other = 0
        if color == 1:
            other = 2
        else:
            other = 1
        if count[other][_l_5]:
            return -9999
        if count[color][_l_5]:
            return 9999
        if count[color][_r_4] >= 2:
            count[color][_l_4] += 1
        if count[other][_r_4] >= 2:
            count[other][_l_4] += 1
        c_value, o_value, win = 0, 0, 0
        if count[color][_l_4] > 0:
            return 9990
        if count[color][_r_4] > 0:
            return 9980
        if count[other][_l_4] > 0:
            return -9970
        if count[other][_r_4] and count[other][_l_3]:
            return -9960
        if count[color][_l_3] and count[other][_r_4] == 0:
            return 9950
        if count[other][_l_3] > 1 and \
                count[color][_r_4] == 0 and \
                count[color][_l_3] == 0 and \
                count[color][_r_3] == 0:
            return -9940
        if count[color][_l_3] > 1:
            c_value += 2000
        elif count[color][_l_3]:
            c_value += 200
        if count[other][_l_3] > 1:
            o_value += 500
        elif count[other][_l_3]:
            o_value += 100
        if count[color][_r_3]:
            c_value += count[color][_r_3] * 10
        if count[other][_r_3]:
            o_value += count[other][_r_3] * 10
        if count[color][_l_2]:
            c_value += count[color][_l_2] * 4
        if count[other][_l_2]:
            o_value += count[other][_l_2] * 4
        if count[color][_r_2]:
            c_value += count[color][_r_2]
        if count[other][_r_2]:
            o_value += count[other][_r_2]
        for i in range(self.cb_sz):
            for j in range(self.cb_sz):
                stone = board[i][j]
                if stone != 0:
                    if stone == color:
                        c_value += self.positions[i][j]
                    else:
                        o_value += self.positions[i][j]
        return c_value - o_value

    def evaluate_horizon(self, board, i, j):
        line, result, record = self.line, self.result, self.record
        todo = self.todo
        for x in range(self.cb_sz):
            line[x] = board[i][x]
        self.evaluate_line(line, result, self.cb_sz, j)
        for x in range(self.cb_sz):
            if result[x] != todo:
                record[i][x][0] = result[x]

    def evaluate_vertical(self, board, i, j):
        line, result, record = self.line, self.result, self.record
        todo = self.todo
        for x in range(self.cb_sz):
            line[x] = board[x][j]
        self.evaluate_line(line, result, self.cb_sz, i)
        for x in range(self.cb_sz):
            if result[x] != todo:
                record[x][j][1] = result[x]

    def evaluate_left_diag(self, board, i, j):
        maxx = self.cb_sz - 1
        line, result, record = self.line, self.result, self.record
        todo = self.todo
        if i < j:
            x = j - i
            y = 0
        else:
            x = 0
            y = i - j
        k = 0
        while k < self.cb_sz:
            if x + k > maxx or y + k > maxx:
                break
            line[k] = board[y + k][x + k]
            k += 1
        self.evaluate_line(line, result, k, j - x)
        for s in range(k):
            if result[s] != todo:
                record[y + s][x + s][2] = result[s]

    def evaluate_right_diag(self, board, i, j):
        line, result, record = self.line, self.result, self.record
        todo = self.todo
        if self.cb_sz - 1 - i < j:
            x = j - self.cb_sz + 1 + i
            y = self.cb_sz - 1
        else:
            x = 0
            y = i + j
        k = 0
        while k < self.cb_sz:
            if x + k > self.cb_sz - 1 or y - k < 0:
                break
            line[k] = board[y - k][x + k]
            k += 1
        self.evaluate_line(line, result, k, j - x)
        for s in range(k):
            if result[s] != todo:
                record[y - s][x + s][3] = result[s]

    def evaluate_line(self, line, record, num, pos):
        todo, over = self.todo, self.over
        if num < 5:
            for i in range(num):
                record[i] = over
            return 0
        _l_5, _l_4, _r_4, _l_3, _r_3, _l_2, _r_2 = self.l_5, self.l_4, self.r_4, self.l_3, self.r_3, self.l_2, self.r_2
        while len(line) < self.cb_sz * 2:
            line.append(0xf)
        while len(record) < self.cb_sz * 2:
            record.append(todo)
        for i in range(num, self.cb_sz * 2):
            line[i] = 0xf
        for i in range(num):
            record[i] = todo
        stone = line[pos]
        inverse = 0
        if stone == 1:
            inverse = 2
        elif stone == 2:
            inverse = 1
        num -= 1
        l, r = pos, pos
        while l > 0:
            if line[l - 1] != stone:
                break
            l -= 1
        while r < num:
            if line[r + 1] != stone:
                break
            r += 1
        real_l, real_r = l, r
        while real_l > 0:
            if line[real_l - 1] == inverse:
                break
            real_l -= 1
        while real_r < num:
            if line[real_r + 1] == inverse:
                break
            real_r += 1
        if real_r - real_l < 4:
            for k in range(real_l, real_r + 1):
                record[k] = over
            return 0
        for k in range(l, r + 1):
            record[k] = over
        consecutive_range = r - l
        if consecutive_range >= 4:
            record[pos] = _l_5
            return _l_5
        if consecutive_range == 3:
            if real_l < l and real_r > r:
                record[pos] = _l_4
            elif (real_l == l and real_r > r) or (real_l < l and real_r == r):
                record[pos] = _r_4
            return record[pos]
        if consecutive_range == 2:
            if (l - real_l > 1 and real_r > r and line[l - 2] == line[pos]) or \
                    (real_l < l and real_r - r > 1 and line[r + 2] == line[pos]):
                record[pos] = _r_4
            elif (l - real_l > 1 and real_r == r and line[l - 2] == line[pos]) or \
                    (real_l == l and real_r - r > 1 and line[r + 2] == line[pos]):
                record[pos] = _r_4
            elif real_l < l and real_r > r:
                record[pos] = _l_3
            elif (real_l == l and real_r > r) or (real_l < l and real_r == r):
                record[pos] = _r_3
            return record[pos]
        if consecutive_range == 1:
            if (l - real_l > 2 and real_r > r and line[l - 2] == line[pos] and line[l - 3] == line[pos]) or \
                    (real_l < l and real_r - r > 1 and line[r + 2] == line[pos] and line[r + 3] == line[pos]):
                record[pos] = _r_4
            elif (l - real_l > 2 and real_r == r and line[l - 2] == line[pos] and line[l - 3] == line[pos]) or \
                    (real_l == l and real_r - r > 2 and line[r + 2] == line[pos] and line[r + 3] == line[pos]):
                record[pos] = _r_4
            elif (l - real_l > 1 and real_r > r and line[l - 2] == line[pos]) or \
                    (real_l < l and real_r - r > 1 and line[r + 2] == line[pos]):
                record[pos] = _r_3
            elif (l - real_l > 1 and real_r == r and line[l - 2] == line[pos]) or \
                    (real_l == l and real_r - r > 1 and line[r + 2] == line[pos]):
                record[pos] = _r_3
            elif real_l < l and real_r > r:
                record[pos] = _l_2
            elif (real_l == l and real_r > r) or (real_l < l and real_r == r):
                record[pos] = _r_2
            return record[pos]
        return 0


class Searcher(object):
    def __init__(self, chessboard_size, chessboard):
        self.cb_sz = chessboard_size
        self.eva = Evaluator(self.cb_sz)
        self.board = chessboard
        self.max_depth = 3
        self.__go = tuple()

    def next_move(self):
        moves = []
        board = self.board
        for i in range(self.cb_sz):
            for j in range(self.cb_sz):
                if board[i][j] == 0:
                    score = self.eva.positions[i][j]
                    moves.append((score, i, j))
        moves.sort()
        moves.reverse()
        return moves

    def __search(self, turn, depth, alpha=-0x7fffffff, beta=0x7fffffff):
        score = self.eva.evaluate(self.board, turn)
        if depth <= 0 or abs(score) >= 9999:
            return score
        moves = self.next_move()
        go = tuple()
        for score, row, col in moves:
            self.board[row][col] = turn
            next_turn = turn == 1 and 2 or 1
            score = - self.__search(next_turn, depth - 1, -beta, -alpha)
            self.board[row][col] = 0
            if score > alpha:
                alpha = score
                go = (row, col)
                if alpha >= beta:
                    break

        if depth == self.max_depth and go:
            self.__go = go

        return alpha

    def search(self, turn, depth=1):
        self.max_depth = depth
        score = self.__search(turn, depth)
        if abs(score) > 8000:
            self.max_depth = depth
            self.__search(turn, 1)
        row, col = self.__go
        return score, row, col

    def deter(self, turn, depth):
        (scoreA, A1, B1) = self.search(1, depth)
        (scoreB, A2, B2) = self.search(2, depth)
        if turn == 1 and scoreB > scoreA:
            return A2, B2
        elif turn == 1 and scoreA >= scoreB:
            return A1, B1
        elif turn == 2 and scoreA > scoreB:
            return A1, B1
        else:
            return A2, B2

