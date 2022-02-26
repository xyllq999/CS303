import numpy as np
import chessboard


class evaluation(object):
    def __init__(self, chessboard_size):
        self.cb_sz = chessboard_size
        self.POS = []
        for i in range(self.cb_sz):  # 给棋盘划分层，最外为0，向内increment
            row = [self.cb_sz // 2 - max(abs(i - self.cb_sz // 2), abs(j - self.cb_sz // 2)) for j in range(self.cb_sz)]
            self.POS.append(tuple(row))
        self.POS = tuple(self.POS)
        self.STWO = 1  # 冲二
        self.STHREE = 2  # 冲三
        self.SFOUR = 3  # 冲四
        self.TWO = 4  # 活二
        self.THREE = 5  # 活三
        self.FOUR = 6  # 活四
        self.FIVE = 7  # 活五
        self.DFOUR = 8  # 双四
        self.FOURT = 9  # 四三
        self.DTHREE = 10  # 双三
        # TODO 死四， 死三
        self.NOTYPE = 11  # 无匹配类型
        self.ANALYSED = 255  # 已经分析过
        self.TODO = 0  # 没有分析过
        self.result = [0 for i in range(self.cb_sz * 2)]  # 保存当前直线分析值，横竖两个方向
        self.line = [0 for i in range(self.cb_sz * 2)]  # 当前直线数据，横竖两个方向
        self.record = []  # 全盘分析结果 [row][col][方向]
        for i in range(self.cb_sz):
            self.record.append([])
            self.record[i] = []
            for j in range(self.cb_sz):
                self.record[i].append([0, 0, 0, 0])
        # record初始化为15*15个[0, 0, 0, 0]
        # 记录水平，垂直，左斜，右斜
        self.count = []  # 每种棋局的个数：count[黑棋/白棋][模式]
        for i in range(3):
            data = [0 for i in range(20)]  # TODO 更换 20，20应该为种类数
            self.count.append(data)
        # record初始化为3*20个[0, 0, 0, 0, 0...]
        self.reset()

    def reset(self):
        TODO = self.TODO  #
        count = self.count
        for i in range(self.cb_sz):
            line = self.record[i]  # 15 个 [0, 0, 0, 0]
            for j in range(self.cb_sz):
                line[j][0] = TODO
                line[j][1] = TODO
                line[j][2] = TODO
                line[j][3] = TODO
        for i in range(20):  # TODO 更换 20，20应该为种类数
            count[0][i] = 0
            count[1][i] = 0
            count[2][i] = 0
        return 0

    # 四个方向（水平，垂直，左斜，右斜）分析评估棋盘，然后根据分析结果打分
    def evaluate(self, board, turn):
        score = self.__evaluate(board, turn)
        count = self.count
        # print(1 == 1 and 2 or 1) result : 2
        # print(2 == 1 and 2 or 1) result : 1
        if score < -9000:
            stone = turn == 1 and 2 or 1
            for i in range(20):
                if count[stone][i] > 0:
                    score -= i
        elif score > 9000:
            stone = turn == 1 and 2 or 1
            for i in range(20):
                if count[stone][i] > 0:
                    score += i
        return score

        # 四个方向（水平，垂直，左斜，右斜）分析评估棋盘，然后根据分析结果打分

    def __evaluate(self, board, turn):
        record, count = self.record, self.count
        TODO, ANALYSED = self.TODO, self.ANALYSED
        self.reset()
        # 四个方向分析
        for i in range(self.cb_sz):
            boardrow = board[i]
            recordrow = record[i]
            for j in range(self.cb_sz):
                if boardrow[j] != 0:
                    if recordrow[j][0] == TODO:  # 水平没有分析过？
                        self.__analysis_horizon(board, i, j)
                    if recordrow[j][1] == TODO:  # 垂直没有分析过？
                        self.__analysis_vertical(board, i, j)
                    if recordrow[j][2] == TODO:  # 左斜没有分析过？
                        self.__analysis_left(board, i, j)
                    if recordrow[j][3] == TODO:  # 右斜没有分析过
                        self.__analysis_right(board, i, j)

        FIVE, FOUR, THREE, TWO = self.FIVE, self.FOUR, self.THREE, self.TWO
        SFOUR, STHREE, STWO = self.SFOUR, self.STHREE, self.STWO
        check = {}

        # 分别对白棋黑棋计算：FIVE, FOUR, THREE, TWO等出现的次数
        for c in (FIVE, FOUR, SFOUR, THREE, STHREE, TWO, STWO):
            check[c] = 1
        for i in range(self.cb_sz):
            for j in range(self.cb_sz):
                stone = board[i][j]  # stone 是黑/白棋
                if stone != 0:
                    for k in range(4):
                        ch = record[i][j][k]
                        if ch in check:
                            count[stone][ch] += 1

        # 如果有五连则马上返回分数
        BLACK, WHITE = 1, 2
        if turn == WHITE:  # 当前是白棋
            if count[BLACK][FIVE]:
                return -9999
            if count[WHITE][FIVE]:
                return 9999
        else:  # 当前是黑棋
            if count[WHITE][FIVE]:
                return -9999
            if count[BLACK][FIVE]:
                return 9999

        # 如果存在两个冲四，则相当于有一个活四
        if count[WHITE][SFOUR] >= 2:
            count[WHITE][FOUR] += 1
        if count[BLACK][SFOUR] >= 2:
            count[BLACK][FOUR] += 1

        # 具体打分
        wvalue, bvalue, win = 0, 0, 0
        if turn == WHITE:
            if count[WHITE][FOUR] > 0:
                return 9990
            if count[WHITE][SFOUR] > 0:
                return 9980
            if count[BLACK][FOUR] > 0:
                return -9970
            if count[BLACK][SFOUR] and count[BLACK][THREE]:
                return -9960
            if count[WHITE][THREE] and count[BLACK][SFOUR] == 0:
                return 9950
            if count[BLACK][THREE] > 1 and \
                    count[WHITE][SFOUR] == 0 and \
                    count[WHITE][THREE] == 0 and \
                    count[WHITE][STHREE] == 0:
                return -9940
            if count[WHITE][THREE] > 1:
                wvalue += 2000
            elif count[WHITE][THREE]:
                wvalue += 200
            if count[BLACK][THREE] > 1:
                bvalue += 500
            elif count[BLACK][THREE]:
                bvalue += 100
            if count[WHITE][STHREE]:
                wvalue += count[WHITE][STHREE] * 10
            if count[BLACK][STHREE]:
                bvalue += count[BLACK][STHREE] * 10
            if count[WHITE][TWO]:
                wvalue += count[WHITE][TWO] * 4
            if count[BLACK][TWO]:
                bvalue += count[BLACK][TWO] * 4
            if count[WHITE][STWO]:
                wvalue += count[WHITE][STWO]
            if count[BLACK][STWO]:
                bvalue += count[BLACK][STWO]
        else:
            if count[BLACK][FOUR] > 0:
                return 9990
            if count[BLACK][SFOUR] > 0:
                return 9980
            if count[WHITE][FOUR] > 0:
                return -9970
            if count[WHITE][SFOUR] and count[WHITE][THREE]:
                return -9960
            if count[BLACK][THREE] and count[WHITE][SFOUR] == 0:
                return 9950
            if count[WHITE][THREE] > 1 and \
                    count[BLACK][SFOUR] == 0 and \
                    count[BLACK][THREE] == 0 and \
                    count[BLACK][STHREE] == 0:
                return -9940
            if count[BLACK][THREE] > 1:
                bvalue += 2000
            elif count[BLACK][THREE]:
                bvalue += 200
            if count[WHITE][THREE] > 1:
                wvalue += 500
            elif count[WHITE][THREE]:
                wvalue += 100
            if count[BLACK][STHREE]:
                bvalue += count[BLACK][STHREE] * 10
            if count[WHITE][STHREE]:
                wvalue += count[WHITE][STHREE] * 10
            if count[BLACK][TWO]:
                bvalue += count[BLACK][TWO] * 4
            if count[WHITE][TWO]:
                wvalue += count[WHITE][TWO] * 4
            if count[BLACK][STWO]:
                bvalue += count[BLACK][STWO]
            if count[WHITE][STWO]:
                wvalue += count[WHITE][STWO]

        # 加上位置权值，棋盘最中心点权值是7，往外一格-1，最外圈是0
        # TODO 考虑是否加上位置权值
        wc, bc = 0, 0
        for i in range(self.cb_sz):
            for j in range(self.cb_sz):
                stone = board[i][j]
                if stone != 0:
                    if stone == WHITE:
                        wc += self.POS[i][j]
                    else:
                        bc += self.POS[i][j]
        wvalue += wc
        bvalue += bc

        if turn == WHITE:
            return wvalue - bvalue

        return bvalue - wvalue

    # 分析横向
    def __analysis_horizon(self, board, i, j):
        line, result, record = self.line, self.result, self.record
        TODO = self.TODO
        for x in range(self.cb_sz):
            line[x] = board[i][x]  # 拷贝待分析的线
        self.analysis_line(line, result, self.cb_sz, j)
        for x in range(self.cb_sz):
            if result[x] != TODO:
                record[i][x][0] = result[x]
        return record[i][j][0]  # 0表示横向

    # 分析纵向
    def __analysis_vertical(self, board, i, j):
        line, result, record = self.line, self.result, self.record
        TODO = self.TODO
        for x in range(self.cb_sz):
            line[x] = board[x][j]
        self.analysis_line(line, result, self.cb_sz, i)
        for x in range(self.cb_sz):
            if result[x] != TODO:
                record[x][j][1] = result[x]
        return record[i][j][1]  # 1表示纵向

    # 分析左斜
    def __analysis_left(self, board, i, j):
        line, result, record = self.line, self.result, self.record
        TODO = self.TODO
        if i < j:
            x, y = j - i, 0  # 定出起点
        else:
            x, y = 0, i - j  # 定出起点
        k = 0
        while k < self.cb_sz:  # 考虑这个斜线上所有的点
            if x + k > self.cb_sz - 1 or y + k > self.cb_sz - 1:
                break
            line[k] = board[y + k][x + k]
            k += 1
        self.analysis_line(line, result, k, j - x)
        for s in range(k):
            if result[s] != TODO:
                record[y + s][x + s][2] = result[s]
        return record[i][j][2]

    # 分析右斜
    def __analysis_right(self, board, i, j):
        line, result, record = self.line, self.result, self.record
        TODO = self.TODO
        if self.cb_sz - 1 - i < j:
            x, y, realnum = j - self.cb_sz + 1 + i, self.cb_sz - 1, self.cb_sz - 1 - i
        else:
            x, y, realnum = 0, i + j, j
        k = 0
        while k < self.cb_sz:
            if x + k > self.cb_sz - 1 or y - k < 0:
                break
            line[k] = board[y - k][x + k]
            k += 1
        self.analysis_line(line, result, k, j - x)
        for s in range(k):
            if result[s] != TODO:
                record[y - s][x + s][3] = result[s]
        return record[i][j][3]

    def test(self, board):
        self.reset()
        record = self.record
        TODO = self.TODO
        for i in range(self.cb_sz):
            for j in range(self.cb_sz):
                if board[i][j] != 0 and 1:
                    if self.record[i][j][0] == TODO:
                        self.__analysis_horizon(board, i, j)
                        pass
                    if self.record[i][j][1] == TODO:
                        self.__analysis_vertical(board, i, j)
                        pass
                    if self.record[i][j][2] == TODO:
                        self.__analysis_left(board, i, j)
                        pass
                    if self.record[i][j][3] == TODO:
                        self.__analysis_right(board, i, j)
                        pass
        return 0

    # 分析一条线：五四三二等棋型
    def analysis_line(self, line, record, num, pos):  # pos是中心点， line保存了当前需要分析的数据， record记录分析结果， num保存了待分析长度
        TODO, ANALYSED = self.TODO, self.ANALYSED
        THREE, STHREE = self.THREE, self.STHREE
        FOUR, SFOUR = self.FOUR, self.SFOUR
        while len(line) < self.cb_sz * 2:
            line.append(0xf)
        while len(record) < self.cb_sz * 2:
            record.append(TODO)
        for i in range(num, self.cb_sz * 2):
            line[i] = 0xf
        for i in range(num):
            record[i] = TODO
        if num < 5:  # 不到5个，没必要分析
            for i in range(num):
                record[i] = ANALYSED
            return 0
        stone = line[pos]  # 获取落子方
        inverse = (0, 2, 1)[stone]  # 取对方
        num -= 1
        xl = pos
        xr = pos
        while xl > 0:  # 探索左边界
            if line[xl - 1] != stone:
                break
            xl -= 1
        while xr < num:  # 探索右边界
            if line[xr + 1] != stone:
                break
            xr += 1
        left_range = xl
        right_range = xr
        while left_range > 0:  # 探索左边范围（非对方棋子的格子坐标）即带没有落子及我方落子的边界
            if line[left_range - 1] == inverse:
                break
            left_range -= 1
        while right_range < num:  # 探索右边范围（非对方棋子的格子坐标）
            if line[right_range + 1] == inverse:
                break
            right_range += 1

        # 如果该直线范围小于 5，则直接返回
        if right_range - left_range < 4:
            for k in range(left_range, right_range + 1):
                record[k] = ANALYSED
            return 0

        # 设置已经分析过
        for k in range(xl, xr + 1):
            record[k] = ANALYSED

        srange = xr - xl

        # 如果是 5连
        if srange >= 4:
            record[pos] = self.FIVE
            return self.FIVE

        # 如果是 4连
        if srange == 3:
            left4 = False  # 是否左边是空格
            if xl > 0:
                if line[xl - 1] == 0:  # 活四
                    left4 = True
            if xr < num:
                if line[xr + 1] == 0:
                    if left4:
                        record[pos] = self.FOUR  # 活四
                    else:
                        record[pos] = self.SFOUR  # 冲四
                else:
                    if left4:
                        record[pos] = self.SFOUR  # 冲四
            else:
                if left4:
                    record[pos] = self.SFOUR  # 冲四
            return record[pos]

        # 如果是 3连
        if srange == 2:  # 三连
            left3 = False  # 是否左边是空格
            if xl > 0:
                if line[xl - 1] == 0:  # 左边有空格
                    if xl > 1 and line[xl - 2] == stone:
                        record[xl] = SFOUR  # 跳冲四
                        record[xl - 2] = ANALYSED
                    else:
                        left3 = True
                elif xr == num or line[xr + 1] != 0:
                    return 0
            if xr < num:
                if line[xr + 1] == 0:  # 右边有空格
                    if xr < num - 1 and line[xr + 2] == stone:
                        record[xr] = SFOUR  # 跳冲四
                        record[xr + 2] = ANALYSED
                    elif left3:
                        record[xr] = THREE
                    else:
                        record[xr] = STHREE
                elif record[xl] == SFOUR:
                    return record[xl]
                elif left3:
                    record[pos] = STHREE
            else:
                if record[xl] == SFOUR:
                    return record[xl]
                if left3:
                    record[pos] = STHREE
            return record[pos]

        # 如果是 2连
        if srange == 1:  # 两连
            left2 = False
            if xl > 2:
                if line[xl - 1] == 0:  # 左边有空格
                    if line[xl - 2] == stone:
                        if line[xl - 3] == stone:  # 跳冲四
                            record[xl - 3] = ANALYSED
                            record[xl - 2] = ANALYSED
                            record[xl] = SFOUR
                        elif line[xl - 3] == 0:  # 跳冲三
                            record[xl - 2] = ANALYSED
                            record[xl] = STHREE
                    else:
                        left2 = True
            if xr < num:
                if line[xr + 1] == 0:  # 右边有空格
                    if xr < num - 2 and line[xr + 2] == stone:
                        if line[xr + 3] == stone:
                            record[xr + 3] = ANALYSED
                            record[xr + 2] = ANALYSED
                            record[xr] = SFOUR
                        elif line[xr + 3] == 0:
                            record[xr + 2] = ANALYSED
                            record[xr] = left2 and THREE or STHREE
                    else:
                        if record[xl] == SFOUR:
                            return record[xl]
                        if record[xl] == STHREE:
                            record[xl] = THREE
                            return record[xl]
                        if left2:
                            record[pos] = self.TWO
                        else:
                            record[pos] = self.STWO
                else:
                    if record[xl] == SFOUR:
                        return record[xl]
                    if left2:
                        record[pos] = self.STWO
            return record[pos]
        return 0


class searcher(object):

    # 初始化
    def __init__(self, board, chessboard_size):
        self.cb_sz = chessboard_size
        self.evaluator = evaluation(chessboard_size)
        self.board = board
        self.gameover = 0
        self.overvalue = 0
        self.maxdepth = 3

    # 产生当前棋局的走法
    def genmove(self, turn):
        moves = []
        board = self.board
        POSES = self.evaluator.POS  # 备选位置
        for i in range(self.cb_sz):
            for j in range(self.cb_sz):
                if board[i][j] == 0:
                    score = POSES[i][j]  # TODO ?
                    moves.append((score, i, j))
        moves.sort()  # list sort以tuple为元素的list时按照第一个元素排序
        moves.reverse()
        return moves

    # 递归搜索：返回最佳分数
    def __search(self, turn, depth, alpha=-0x7fffffff, beta=0x7fffffff):

        # 深度为零则评估棋盘并返回
        if depth <= 0:
            score = self.evaluator.evaluate(self.board, turn)
            return score

        # 如果游戏结束则立马返回
        score = self.evaluator.evaluate(self.board, turn)
        if abs(score) >= 9999 and depth < self.maxdepth:
            return score

        # 产生新的走法
        moves = self.genmove(turn)
        bestmove = None

        # 枚举当前所有走法
        for score, row, col in moves:

            # 标记当前走法到棋盘
            self.board[row][col] = turn

            # 计算下一回合该谁走
            nturn = turn == 1 and 2 or 1
            # print((row, col), end=" ")
            # 深度优先搜索，返回评分，走的行和走的列
            score = - self.__search(nturn, depth - 1, -beta, -alpha)
            # print(score)
            # 棋盘上清除当前走法
            self.board[row][col] = 0

            # 计算最好分值的走法
            # alpha/beta 剪枝
            if score > alpha:
                alpha = score
                bestmove = (row, col)
                if alpha >= beta:
                    break

        # 如果是第一层则记录最好的走法
        if depth == self.maxdepth and bestmove:
            self.bestmove = bestmove

        # 返回当前最好的分数，和该分数的对应走法
        return alpha

    # 具体搜索：传入当前是该谁走(turn=1/2)，以及搜索深度(depth)
    def search(self, turn, depth=3):
        self.maxdepth = depth
        self.bestmove = None
        score = self.__search(turn, depth)
        if abs(score) > 8000:
            self.maxdepth = depth
            score = self.__search(turn, 1)
        row, col = self.bestmove
        return score, row, col

    def deter(self, turn, depth):
        (scoreA, A1, B1) = s.search(1, depth)
        (scoreB, A2, B2) = s.search(2, depth)
        if turn == 1 and scoreB > scoreA:
            return A2, B2
        elif turn == 1 and scoreA >= scoreB:
            return A1, B1
        elif turn == 2 and scoreA > scoreB:
            return A1, B1
        else:
            return A2, B2


if __name__ == '__main__':
    e = evaluation(14)
    # board = \
    #     [
    #         [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     ]
    # print(e.evaluate(board, 1))
    # print(e.evaluate(board, 2))
    # board = \
    #     [
    #         [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     ]
    # print(e.evaluate(board, 1))
    # print(e.evaluate(board, 2))
    # board = \
    #     [
    #         [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     ]
    # print(e.evaluate(board, 1))
    # print(e.evaluate(board, 2))
    # board = \
    #     [
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 0, 0, 0, 0],
    #         [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     ]
    # print(e.evaluate(board, 1))
    # print(e.evaluate(board, 2))
    board = \
        [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
    print(e.evaluate(board, 1))
    print(e.evaluate(board, 2))
    s = searcher(board, 14)
    print(s.deter(2, 1))
    board = \
        [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
    print(e.evaluate(board, 1))
    print(e.evaluate(board, 2))
    board = \
        [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 2, 2, 2, 2, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
    print(e.evaluate(board, 1))
    print(e.evaluate(board, 2))
