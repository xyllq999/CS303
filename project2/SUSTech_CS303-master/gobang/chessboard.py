# import time
#
# COLOR_BLACK = -1
# COLOR_WHITE = 1
# COLOR_NONE = 0
#
#
# class AI_1(object):
#     def __init__(self, chessboard_size, color, time_out):
#         self.chessboard_size = chessboard_size
#         self.color = color
#         self.time_out = time_out
#         self.candidate_list = []
#
#     def go(self, chessboard):
#         self.candidate_list.clear()
#         b = self.parse(chessboard)
#         s = Searcher(self, self.chessboard_size, b)
#         p = tuple()
#         if self.color == -1:
#             p = s.deter(1, 1)
#         else:
#             p = s.deter(2, 1)
#         self.candidate_list.append(p)
#         # print(p)
#
#     def parse(self, chessboard):
#         sz = self.chessboard_size
#         board = [[0 for i in range(sz)] for j in range(sz)]
#         for i in range(sz):
#             for j in range(sz):
#                 if chessboard[i][j] == -1:
#                     board[i][j] = 1
#                 elif chessboard[i][j] == 1:
#                     board[i][j] = 2
#         return board
#
#
# class Evaluator(object):
#     def __init__(self, chessboard_size):
#         self.cb_sz = chessboard_size
#         self.positions = []
#         for i in range(self.cb_sz):  # 给棋盘划分层，最外为0，向内increment
#             row = [self.cb_sz // 2 - max(abs(i - self.cb_sz // 2), abs(j - self.cb_sz // 2)) for j in range(self.cb_sz)]
#             self.positions.append(tuple(row))
#         self.positions = tuple(self.positions)
#         self.r_2 = 1  # 冲二
#         self.r_3 = 2  # 冲三
#         self.r_4 = 3  # 冲四
#         self.l_2 = 4  # 活二
#         self.l_3 = 5  # 活三
#         self.l_4 = 6  # 活四
#         self.l_5 = 7  # 活五
#         self.over = 255
#         self.todo = 0
#         self.result = [0 for i in range(self.cb_sz)]
#         self.line = [0 for i in range(self.cb_sz)]
#         self.record = [[[0, 0, 0, 0] for i in range(15)] for j in range(15)]
#         # 记录水平，垂直，左斜，右斜
#         self.count = [[0 for i in range(10)] for i in range(3)]
#         self.reset()
#
#     def reset(self):
#         todo = self.todo
#         count = self.count
#         for i in range(self.cb_sz):
#             line = self.record[i]
#             for j in range(self.cb_sz):
#                 for k in range(4):
#                     line[j][k] = todo
#         for i in range(10):
#             for j in range(3):
#                 count[j][i] = 0
#         return 0
#
#     def evaluate(self, board, turn):
#         score = self.__evaluate(board, turn)
#         count = self.count
#         if score < -9000:
#             stone = turn == 1 and 2 or 1
#             for i in range(10):
#                 if count[stone][i] > 0:
#                     score -= i
#         elif score > 9000:
#             stone = turn == 1 and 2 or 1
#             for i in range(10):
#                 if count[stone][i] > 0:
#                     score += i
#         return score
#
#     def __evaluate(self, board, turn):
#         record, count = self.record, self.count
#         todo, over = self.todo, self.over
#         self.reset()
#         for i in range(self.cb_sz):
#             boardrow = board[i]
#             recordrow = record[i]
#             for j in range(self.cb_sz):
#                 if boardrow[j] != 0:
#                     if recordrow[j][0] == todo:
#                         self.evaluate_horizon(board, i, j)
#                     if recordrow[j][1] == todo:
#                         self.evaluate_vertical(board, i, j)
#                     if recordrow[j][2] == todo:
#                         self.evaluate_left_diag(board, i, j)
#                     if recordrow[j][3] == todo:
#                         self.evaluate_right_diag(board, i, j)
#
#         p = [self.l_5, self.l_4, self.l_3, self.l_2, self.r_4, self.r_3, self.r_2]
#         for i in range(self.cb_sz):
#             for j in range(self.cb_sz):
#                 stone = board[i][j]
#                 if stone != 0:
#                     for k in range(4):
#                         ch = record[i][j][k]
#                         if ch in p:
#                             count[stone][ch] += 1
#
#         return self.detailed_eva(turn, count, board)
#
#     def detailed_eva(self, color, count, board):
#         _l_5, _l_4, _l_3, _l_2 = self.l_5, self.l_4, self.l_3, self.l_2
#         _r_4, _r_3, _r_2 = self.r_4, self.r_3, self.r_2
#         other = 0
#         if color == 1:
#             other = 2
#         else:
#             other = 1
#         if count[other][_l_5]:
#             return -9999
#         if count[color][_l_5]:
#             return 9999
#         if count[color][_r_4] >= 2:  # 双沖四
#             count[color][_l_4] += 1
#         if count[other][_r_4] >= 2:  # 双沖四
#             count[other][_l_4] += 1
#         c_value, o_value, win = 0, 0, 0
#         if count[color][_l_4] > 0:
#             return 9990
#         if count[color][_r_4] > 0:
#             return 9980
#         if count[other][_l_4] > 0:
#             return -9970
#         if count[other][_r_4] and count[other][_l_3]:  # 沖四活三
#             return -9960
#         if count[color][_l_3] and count[other][_r_4] == 0:  # 沖四活三
#             return 9950
#         if count[other][_l_3] > 1 and \
#                 count[color][_r_4] == 0 and \
#                 count[color][_l_3] == 0 and \
#                 count[color][_r_3] == 0:
#             return -9940
#         if count[color][_l_3] > 1:
#             c_value += 2000
#         elif count[color][_l_3]:
#             c_value += 200
#         if count[other][_l_3] > 1:
#             o_value += 500
#         elif count[other][_l_3]:
#             o_value += 100
#         if count[color][_r_3]:
#             c_value += count[color][_r_3] * 10
#         if count[other][_r_3]:
#             o_value += count[other][_r_3] * 10
#         if count[color][_l_2]:
#             c_value += count[color][_l_2] * 4
#         if count[other][_l_2]:
#             o_value += count[other][_l_2] * 4
#         if count[color][_r_2]:
#             c_value += count[color][_r_2]
#         if count[other][_r_2]:
#             o_value += count[other][_r_2]
#         for i in range(self.cb_sz):
#             for j in range(self.cb_sz):
#                 stone = board[i][j]
#                 if stone != 0:
#                     if stone == color:
#                         c_value += self.positions[i][j]
#                     else:
#                         o_value += self.positions[i][j]
#         # print("cvalue:" + str(c_value))
#         # print("ovalue:" + str(o_value))
#         return c_value - o_value
#
#     def evaluate_horizon(self, board, i, j):
#         line, result, record = self.line, self.result, self.record
#         todo = self.todo
#         for x in range(self.cb_sz):
#             line[x] = board[i][x]
#         self.evaluate_line(line, result, self.cb_sz, j)
#         for x in range(self.cb_sz):
#             if result[x] != todo:
#                 record[i][x][0] = result[x]
#
#     def evaluate_vertical(self, board, i, j):
#         line, result, record = self.line, self.result, self.record
#         todo = self.todo
#         for x in range(self.cb_sz):
#             line[x] = board[x][j]
#         self.evaluate_line(line, result, self.cb_sz, i)
#         for x in range(self.cb_sz):
#             if result[x] != todo:
#                 record[x][j][1] = result[x]
#
#     def evaluate_left_diag(self, board, i, j):
#         maxx = self.cb_sz - 1
#         line, result, record = self.line, self.result, self.record
#         todo = self.todo
#         if i < j:
#             x = j - i
#             y = 0
#         else:
#             x = 0
#             y = i - j
#         k = 0
#         while k < self.cb_sz:
#             if x + k > maxx or y + k > maxx:
#                 break
#             line[k] = board[y + k][x + k]
#             k += 1
#         self.evaluate_line(line, result, k, j - x)
#         for s in range(k):
#             if result[s] != todo:
#                 record[y + s][x + s][2] = result[s]
#
#     def evaluate_right_diag(self, board, i, j):
#         line, result, record = self.line, self.result, self.record
#         todo = self.todo
#         if self.cb_sz - 1 - i < j:
#             x = j - self.cb_sz + 1 + i
#             y = self.cb_sz - 1
#         else:
#             x = 0
#             y = i + j
#         k = 0
#         while k < self.cb_sz:
#             if x + k > self.cb_sz - 1 or y - k < 0:
#                 break
#             line[k] = board[y - k][x + k]
#             k += 1
#         self.evaluate_line(line, result, k, j - x)
#         for s in range(k):
#             if result[s] != todo:
#                 record[y - s][x + s][3] = result[s]
#
#     def evaluate_line(self, line, record, num, pos):  # pos是中心点， line保存了当前需要分析的数据， record记录分析结果， num保存了待分析长度
#         TODO, ANALYSED = self.todo, self.over
#         THREE, STHREE = self.l_3, self.r_3
#         FOUR, SFOUR = self.l_4, self.r_4
#         while len(line) < self.cb_sz * 2:
#             line.append(0xf)
#         while len(record) < self.cb_sz * 2:
#             record.append(TODO)
#         for i in range(num, self.cb_sz * 2):
#             line[i] = 0xf
#         for i in range(num):
#             record[i] = TODO
#         if num < 5:  # 不到5个，没必要分析
#             for i in range(num):
#                 record[i] = ANALYSED
#             return 0
#         stone = line[pos]  # 获取落子方
#         inverse = (0, 2, 1)[stone]  # 取对方
#         num -= 1
#         xl = pos
#         xr = pos
#         while xl > 0:  # 探索左边界
#             if line[xl - 1] != stone:
#                 break
#             xl -= 1
#         while xr < num:  # 探索右边界
#             if line[xr + 1] != stone:
#                 break
#             xr += 1
#         left_range = xl
#         right_range = xr
#         while left_range > 0:  # 探索左边范围（非对方棋子的格子坐标）即带没有落子及我方落子的边界
#             if line[left_range - 1] == inverse:
#                 break
#             left_range -= 1
#         while right_range < num:  # 探索右边范围（非对方棋子的格子坐标）
#             if line[right_range + 1] == inverse:
#                 break
#             right_range += 1
#
#         # 如果该直线范围小于 5，则直接返回
#         if right_range - left_range < 4:
#             for k in range(left_range, right_range + 1):
#                 record[k] = ANALYSED
#             return 0
#
#         # 设置已经分析过
#         for k in range(xl, xr + 1):
#             record[k] = ANALYSED
#
#         srange = xr - xl
#
#         # 如果是 5连
#         if srange >= 4:
#             record[pos] = self.l_5
#             return self.l_5
#
#         # 如果是 4连
#         if srange == 3:
#             left4 = False  # 是否左边是空格
#             if xl > 0:
#                 if line[xl - 1] == 0:  # 活四
#                     left4 = True
#             if xr < num:
#                 if line[xr + 1] == 0:
#                     if left4:
#                         record[pos] = self.l_4  # 活四
#                     else:
#                         record[pos] = self.r_4  # 冲四
#                 else:
#                     if left4:
#                         record[pos] = self.r_4  # 冲四
#             else:
#                 if left4:
#                     record[pos] = self.r_4  # 冲四
#             return record[pos]
#
#         # 如果是 3连
#         if srange == 2:  # 三连
#             left3 = False  # 是否左边是空格
#             if xl > 0:
#                 if line[xl - 1] == 0:  # 左边有空格
#                     if xl > 1 and line[xl - 2] == stone:
#                         record[xl] = SFOUR  # 跳冲四
#                         record[xl - 2] = ANALYSED
#                     else:
#                         left3 = True
#                 elif xr == num or line[xr + 1] != 0:
#                     return 0
#             if xr < num:
#                 if line[xr + 1] == 0:  # 右边有空格
#                     if xr < num - 1 and line[xr + 2] == stone:
#                         record[xr] = SFOUR  # 跳冲四
#                         record[xr + 2] = ANALYSED
#                     elif left3:
#                         record[xr] = THREE
#                     else:
#                         record[xr] = STHREE
#                 elif record[xl] == SFOUR:
#                     return record[xl]
#                 elif left3:
#                     record[pos] = STHREE
#             else:
#                 if record[xl] == SFOUR:
#                     return record[xl]
#                 if left3:
#                     record[pos] = STHREE
#             return record[pos]
#
#         # 如果是 2连
#         if srange == 1:  # 两连
#             left2 = False
#             if xl > 2:
#                 if line[xl - 1] == 0:  # 左边有空格
#                     if line[xl - 2] == stone:
#                         if line[xl - 3] == stone:  # 跳冲四
#                             record[xl - 3] = ANALYSED
#                             record[xl - 2] = ANALYSED
#                             record[xl] = SFOUR
#                         elif line[xl - 3] == 0:  # 跳冲三
#                             record[xl - 2] = ANALYSED
#                             record[xl] = STHREE
#                     else:
#                         left2 = True
#             if xr < num:
#                 if line[xr + 1] == 0:  # 右边有空格
#                     if xr < num - 2 and line[xr + 2] == stone:
#                         if line[xr + 3] == stone:
#                             record[xr + 3] = ANALYSED
#                             record[xr + 2] = ANALYSED
#                             record[xr] = SFOUR
#                         elif line[xr + 3] == 0:
#                             record[xr + 2] = ANALYSED
#                             record[xr] = left2 and THREE or STHREE
#                     else:
#                         if record[xl] == SFOUR:
#                             return record[xl]
#                         if record[xl] == STHREE:
#                             record[xl] = THREE
#                             return record[xl]
#                         if left2:
#                             record[pos] = self.l_2
#                         else:
#                             record[pos] = self.r_2
#                 else:
#                     if record[xl] == SFOUR:
#                         return record[xl]
#                     if left2:
#                         record[pos] = self.r_2
#             return record[pos]
#         return 0
#
#     # def evaluate_line(self, line, record, num, pos):
#     #     todo, over = self.todo, self.over
#     #     if num < 5:
#     #         for i in range(num):
#     #             record[i] = over
#     #         return 0
#     #     _l_5, _l_4, _r_4, _l_3, _r_3, _l_2, _r_2 = self.l_5, self.l_4, self.r_4, self.l_3, self.r_3, self.l_2, self.r_2
#     #     while len(line) < self.cb_sz * 2:
#     #         line.append(0xf)
#     #     while len(record) < self.cb_sz * 2:
#     #         record.append(todo)
#     #     for i in range(num, self.cb_sz * 2):
#     #         line[i] = 0xf
#     #     for i in range(num):
#     #         record[i] = todo
#     #     stone = line[pos]
#     #     inverse = 0
#     #     if stone == 1:
#     #         inverse = 2
#     #     elif stone == 2:
#     #         inverse = 1
#     #     num -= 1
#     #     l, r = pos, pos
#     #     while l > 0:
#     #         if line[l - 1] != stone:
#     #             break
#     #         l -= 1
#     #     while r < num:
#     #         if line[r + 1] != stone:
#     #             break
#     #         r += 1
#     #     real_l, real_r = l, r
#     #     while real_l > 0:
#     #         if line[real_l - 1] == inverse:
#     #             break
#     #         real_l -= 1
#     #     while real_r < num:
#     #         if line[real_r + 1] == inverse:
#     #             break
#     #         real_r += 1
#     #     if real_r - real_l < 4:
#     #         for k in range(real_l, real_r + 1):
#     #             record[k] = over
#     #         return 0
#     #     for k in range(l, r + 1):
#     #         record[k] = over
#     #     consecutive_range = r - l
#     #     if consecutive_range >= 4:
#     #         record[pos] = _l_5
#     #         return _l_5
#     #     if consecutive_range == 3:
#     #         if real_l < l and real_r > r:
#     #             record[pos] = _l_4
#     #         elif (real_l == l and real_r > r) or (real_l < l and real_r == r):
#     #             record[pos] = _r_4
#     #         return record[pos]
#     #     if consecutive_range == 2:
#     #         if (l - real_l > 1 and real_r > r and line[l - 2] == line[pos]) or \
#     #                 (real_l < l and real_r - r > 1 and line[r + 2] == line[pos]):
#     #             record[pos] = _r_4
#     #         elif (l - real_l > 1 and real_r == r and line[l - 2] == line[pos]) or \
#     #                 (real_l == l and real_r - r > 1 and line[r + 2] == line[pos]):
#     #             record[pos] = _r_4
#     #         elif real_l < l and real_r > r:
#     #             record[pos] = _l_3
#     #         elif (real_l == l and real_r > r) or (real_l < l and real_r == r):
#     #             record[pos] = _r_3
#     #         return record[pos]
#     #     if consecutive_range == 1:
#     #         if (l - real_l > 2 and real_r > r and line[l - 2] == line[pos] and line[l - 3] == line[pos]) or \
#     #                 (real_l < l and real_r - r > 1 and line[r + 2] == line[pos] and line[r + 3] == line[pos]):
#     #             record[pos] = _r_4
#     #         elif (l - real_l > 2 and real_r == r and line[l - 2] == line[pos] and line[l - 3] == line[pos]) or \
#     #                 (real_l == l and real_r - r > 2 and line[r + 2] == line[pos] and line[r + 3] == line[pos]):
#     #             record[pos] = _r_4
#     #         elif (l - real_l > 1 and real_r > r and line[l - 2] == line[pos]) or \
#     #                 (real_l < l and real_r - r > 1 and line[r + 2] == line[pos]):
#     #             record[pos] = _r_3
#     #         elif (l - real_l > 1 and real_r == r and line[l - 2] == line[pos]) or \
#     #                 (real_l == l and real_r - r > 1 and line[r + 2] == line[pos]):
#     #             record[pos] = _r_3
#     #         elif real_l < l and real_r > r:
#     #             record[pos] = _l_2
#     #         elif (real_l == l and real_r > r) or (real_l < l and real_r == r):
#     #             record[pos] = _r_2
#     #         return record[pos]
#     #     return 0
#
#
# class Searcher(object):
#     def __init__(self, AI, chessboard_size, chessboard):
#         self.cb_sz = chessboard_size
#         self.eva = Evaluator(self.cb_sz)
#         self.board = chessboard
#         self.max_depth = 3
#         self.__go = tuple()
#         self.AI = AI
#
#     def next_move(self):
#         moves = []
#         board = self.board
#         for i in range(self.cb_sz):
#             for j in range(self.cb_sz):
#                 if board[i][j] == 0:
#                     score = self.eva.positions[i][j]
#                     moves.append((score, i, j))
#         moves.sort()
#         moves.reverse()
#         return moves
#
#     def __search(self, turn, depth, alpha=-0x7fffffff, beta=0x7fffffff):
#         score = self.eva.evaluate(self.board, turn)
#         if depth <= 0 or abs(score) >= 9999:
#             return score
#         moves = self.next_move()
#         go = tuple()
#         for score, row, col in moves:
#             self.board[row][col] = turn
#             next_turn = turn == 1 and 2 or 1
#             score = - self.__search(next_turn, depth - 1, -beta, -alpha)
#             self.board[row][col] = 0
#             if score > alpha:
#                 alpha = score
#                 go = (row, col)
#                 self.AI.candidate_list.append((row, col))
#                 if alpha >= beta:
#                     break
#
#         if depth == self.max_depth and go:
#             self.__go = go
#
#         return alpha
#
#     def search(self, turn, depth=1):
#         self.max_depth = depth
#         score = self.__search(turn, depth)
#         if abs(score) > 8000:
#             self.max_depth = depth
#             self.__search(turn, 1)
#         row, col = self.__go
#         return score, row, col
#
#     def deter(self, turn, depth):
#         (scoreA, A1, B1) = self.search(1, depth)
#         (scoreB, A2, B2) = self.search(2, depth)
#         if turn == 1 and scoreB > scoreA:
#             return A2, B2
#         elif turn == 1 and scoreA >= scoreB:
#             return A1, B1
#         elif turn == 2 and scoreA > scoreB:
#             return A1, B1
#         else:
#             return A2, B2
#
#
# if __name__ == '__main__':
#     s_time = time.time()
#     board = \
#         [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
#          [1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
#          [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
#          [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
#          [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
#          [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
#          [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
#          [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
#          [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
#          [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
#          [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
#          [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
#          [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
#          [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
#          [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
#          ]
#
#     e = Evaluator(15)
#     print(e.evaluate(board, 2))
#     print("white: 冲二:" + str(e.count[1][1]) + " 冲三:" + str(e.count[1][2]) + " 冲四:" + str(e.count[1][3]) + " 活二:" +
#           str(e.count[1][4]) + " 活三:" + str(e.count[1][5]) + " 活四:" + str(e.count[1][6]) +
#           " 活五:" + str(e.count[1][7]))
#     print("black: 冲二:" + str(e.count[2][1]) + " 冲三:" + str(e.count[2][2]) + " 冲四:" + str(e.count[2][3]) + " 活二:" +
#           str(e.count[2][4]) + " 活三:" + str(e.count[2][5]) + " 活四:" + str(e.count[2][6]) +
#           " 活五:" + str(e.count[2][7]))
#     ai = AI(15, 2, 5)
#     s = Searcher(ai, 15, board)
#     print(s.deter(1, 2))
#     # print(ai.candidate_list)
#     print(time.time() - s_time)


# ver2.0 single point evaluation, reduce time complexity

import time
import random
import numpy as np

COLOR_BLACK = -1
COLOR_WHITE = 1
COLOR_NONE = 0
r_2 = 50  # 冲二
tc_2 = 25  # 冲跳二
l_2 = 100  # 活二
r_3 = 300  # 冲三
tc_3 = 200  # 跳冲三
l_3 = 500  # 活三
r_4 = 500  # 冲四
tc_4 = 400  # 跳冲四
l_4 = 1000  # 活四
l_5 = 10000  # 活五


class AI_1(object):
    def __init__(self, chessboard_size, color, time_out):
        self.chessboard_size = chessboard_size
        self.color = color
        self.chessboard = None
        self.time_out = time_out
        self.candidate_list = []

    def go(self, chessboard):
        stime = time.time()
        self.chessboard = chessboard
        self.candidate_list.clear()
        self.global_max = -100000
        self.numMAX = 5
        self.global_max = -100000
        self.pre_depth = 3
        self.empty = [[0 for i in range(self.chessboard_size)] for i in range(self.chessboard_size)]
        self.score = [[0 for i in range(self.chessboard_size)] for i in range(self.chessboard_size)]
        self.myScore = [[0 for i in range(self.chessboard_size)] for i in range(self.chessboard_size)]
        self.enScore = [[0 for i in range(self.chessboard_size)] for i in range(self.chessboard_size)]
        self.ZTable = [[[random.randint(0, pow(2, 24)) for i in range(2)] for i in range(self.chessboard_size)] \
                       for i in range(self.chessboard_size)]
        self.pos = [[0 for i in range(self.chessboard_size)] for i in range(self.chessboard_size)]
        for i in range(self.chessboard_size):  # 给棋盘划分层，最外为0，向内increment
            row = [self.chessboard_size // 2 - max(abs(i - self.chessboard_size // 2),
                                                   abs(j - self.chessboard_size // 2))
                   for j in range(self.chessboard_size)]
            self.pos[i] = row
        self.minmax(self.color, self.pre_depth)
        print(time.time() - stime)

    def minmax(self, color, depth, alpha=-1000000, beta=1000000):
        if depth <= 0:
            return self.global_eva()
        moves = self.next_move()
        if color == self.color:
            mscore = 0
            escore = 0
            go = tuple()
            for i in range(len(moves)):
                x = moves[i][0]
                y = moves[i][1]
                if mscore < self.myScore[x][y]:
                    mscore = self.myScore[x][y]
                    go = (x, y)
                if escore < self.enScore[x][y]:
                    escore = self.enScore[x][y]
            if mscore >= escore and mscore >= 1000:
                alpha = l_5
                if depth == self.pre_depth:
                    self.global_max = l_5
                    self.candidate_list.append(go)
                return alpha
            elif escore > mscore:
                for i in range(len(moves)):
                    x = moves[i][0]
                    y = moves[i][1]
                    if escore == self.enScore[x][y]:
                        self.chessboard[x][y] = color
                        self.score_mod(x, y)
                        score = self.minmax(-color, depth - 1, alpha, beta)
                        #print(score)
                        if depth == self.pre_depth and score > self.global_max:
                            self.candidate_list.append((x, y))
                            self.global_max = score
                        self.chessboard[x][y] = COLOR_NONE
                        self.score_mod(x, y)
                        if score > alpha:
                            alpha = score
                        if alpha >= beta:
                            return alpha
                return alpha
            for i in range(len(moves)):
                x = moves[i][0]
                y = moves[i][1]
                self.chessboard[x][y] = color
                self.score_mod(x, y)
                score = self.minmax(-color, depth - 1, alpha, beta)
                #print(score)
                if depth == self.pre_depth and score > self.global_max:
                    self.candidate_list.append((x, y))
                    self.global_max = score
                self.chessboard[x][y] = COLOR_NONE
                self.score_mod(x, y)
                if score > alpha:
                    alpha = score
                if alpha >= beta:
                    return alpha
            return alpha
        else:
            mscore = 0
            escore = 0
            go = tuple()
            for i in range(len(moves)):
                x = moves[i][0]
                y = moves[i][1]
                if mscore < self.myScore[x][y]:
                    mscore = self.myScore[x][y]
                if escore < self.enScore[x][y]:
                    escore = self.enScore[x][y]
                    go = (x, y)
            if mscore <= escore and escore >= 1000:
                beta = -l_5
                return beta
            elif mscore > escore:
                for i in range(len(moves)):
                    x = moves[i][0]
                    y = moves[i][1]
                    if mscore == self.myScore[x][y]:
                        self.chessboard[x][y] = color
                        self.score_mod(x, y)
                        score = self.minmax(-color, depth - 1, alpha, beta)
                        self.chessboard[x][y] = COLOR_NONE
                        self.score_mod(x, y)
                        if score < beta:
                            beta = score
                        if alpha >= beta:
                            return beta
                return beta
            for i in range(len(moves)):
                x = moves[i][0]
                y = moves[i][1]
                self.chessboard[x][y] = color
                self.score_mod(x, y)
                score = self.minmax(-color, depth - 1, alpha, beta)
                self.chessboard[x][y] = COLOR_NONE
                self.score_mod(x, y)
                if score < beta:
                    beta = score
                if alpha >= beta:
                    return beta
            return beta

    def point_eva(self, x, y, color):
        mapp = {
            'r_2': 0,  # 冲二
            'tc_2': 0,  # 冲跳二
            'l_2': 0,  # 活二
            'r_3': 0,  # 冲三
            'tc_3': 0,  # 跳冲三
            'l_3': 0,  # 活三
            'r_4': 0,  # 冲四
            'tc_4': 0,  # 跳冲四
            'l_4': 0,  # 活四
            'l_5': 0  # 活五
        }
        self.evaluate_horizon(x, y, mapp, color)
        self.evaluate_vertical(x, y, mapp, color)
        self.evaluate_left_diag(x, y, mapp, color)
        self.evaluate_right_diag(x, y, mapp, color)
        score = mapp['r_2'] * r_2 + mapp['tc_2'] * tc_2 + mapp['l_2'] * l_2 + mapp['r_3'] * r_3 + \
                mapp['tc_3'] * tc_3 + mapp['l_3'] * l_3 + mapp['r_4'] * r_4 + mapp['tc_4'] * tc_4 + \
                mapp['l_4'] * l_4 + mapp['l_5'] * l_5
        return score

    def evaluate_horizon(self, x, y, mapp, color):
        line = [0 for i in range(self.chessboard_size)]
        for p in range(self.chessboard_size):
            line[p] = self.chessboard[x][p]
        self.evaluate_line(line, self.chessboard_size, y, mapp, color)

    def evaluate_vertical(self, x, y, mapp, color):
        line = [0 for i in range(self.chessboard_size)]
        for p in range(self.chessboard_size):
            line[p] = self.chessboard[p][y]
        self.evaluate_line(line, self.chessboard_size, x, mapp, color)

    def evaluate_left_diag(self, x, y, mapp, color):
        line = [0 for i in range(self.chessboard_size)]
        maxx = self.chessboard_size - 1
        i = j = 0
        if x < y:
            i = y - x
            j = 0
        else:
            i = 0
            j = x - y
        k = 0
        while k < self.chessboard_size:
            if i + k > maxx or j + k > maxx:
                break
            line[k] = self.chessboard[j + k][i + k]
            k += 1
        self.evaluate_line(line, k, y - i, mapp, color)

    def evaluate_right_diag(self, x, y, mapp, color):
        line = [0 for i in range(self.chessboard_size)]
        i = j = 0
        if self.chessboard_size - 1 - x < y:
            i = y - self.chessboard_size + 1 + x
            j = self.chessboard_size - 1
        else:
            i = 0
            j = x + y
        k = 0
        while k < self.chessboard_size:
            if i + k > self.chessboard_size - 1 or j - k < 0:
                break
            line[k] = self.chessboard[j - k][i + k]
            k += 1
        self.evaluate_line(line, k, y - i, mapp, color)

    def evaluate_line(self, line, num, pos, mapp, color):
        if num < 5:
            return
        for i in range(num, self.chessboard_size):
            line[i] = 0xf
        stone = color
        inverse = 0
        if color == COLOR_BLACK:
            inverse = COLOR_WHITE
        elif color == COLOR_WHITE:
            inverse = COLOR_BLACK
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
            return
        consecutive_range = r - l
        if consecutive_range >= 4:
            mapp['l_5'] += 1
        if consecutive_range == 3:
            if real_l < l and real_r > r:
                mapp['l_4'] += 1
            elif (real_l == l and real_r > r) or (real_l < l and real_r == r):
                mapp['r_4'] += 1
        if consecutive_range == 2:
            if (l - real_l > 1 and real_r >= r and line[l - 2] == stone) or \
                    (real_l <= l and real_r - r > 1 and line[r + 2] == stone):
                mapp['tc_4'] += 1
            elif real_l < l and real_r > r:
                mapp['l_3'] += 1
            elif (real_l == l and real_r > r) or (real_l < l and real_r == r):
                mapp['r_3'] += 1
        if consecutive_range == 1:
            if (l - real_l > 2 and real_r >= r and line[l - 2] == stone and line[l - 3] == stone) or \
                    (real_l <= l and real_r - r > 2 and line[r + 2] == stone and line[r + 3] == stone):
                mapp['tc_4'] += 1
            elif (l - real_l > 1 and real_r >= r and line[l - 2] == stone) or \
                    (real_l <= l and real_r - r > 1 and line[r + 2] == stone):
                mapp['tc_3'] += 1
            elif real_l < l and real_r > r:
                mapp['l_2'] += 1
            elif (real_l == l and real_r > r) or (real_l < l and real_r == r):
                mapp['r_2'] += 1

    def next_move(self):
        move_list = list()
        sort_list = list()
        if self.score == self.empty:
            for i in range(0, self.chessboard_size):
                for j in range(0, self.chessboard_size):
                    if self.chessboard[i][j] == COLOR_NONE:
                        mscore = self.point_eva(i, j, self.color)
                        escore = self.point_eva(i, j, -self.color)
                        self.score[i][j] = mscore + escore
                        self.myScore[i][j] = mscore
                        self.enScore[i][j] = escore
                        sort_list.append((self.score[i][j] + self.pos[i][j], i, j))
        else:
            for i in range(0, self.chessboard_size):
                for j in range(0, self.chessboard_size):
                    if self.chessboard[i][j] == COLOR_NONE:
                        sort_list.append((self.score[i][j] + self.pos[i][j], i, j))
        sort_list.sort()
        sort_list.reverse()
        number = 0
        for i in range(len(sort_list)):
            if number == self.numMAX:
                break
            else:
                if self.chessboard[sort_list[i][1]][sort_list[i][2]] == COLOR_NONE:
                    move_list.append((sort_list[i][1], sort_list[i][2]))
                    number = number + 1
        return move_list

    def score_mod(self, x, y):
        # 向八个方向拓展更新
        dir = [[1, 0], [0, 1], [-1, 0], [0, -1], [1, -1], [-1, 1], [1, 1], [-1, -1]]
        for i in range(len(dir)):
            tx = x + dir[i][0]
            ty = y + dir[i][1]
            while 0 <= tx < self.chessboard_size and 0 <= ty < self.chessboard_size:
                num = 0
                if num >= 5:
                    break
                if self.chessboard[tx][ty] == COLOR_NONE:
                    myscore = self.point_eva(tx, ty, self.color)
                    escore = self.point_eva(tx, ty, self.color)
                    self.score[tx][ty] = myscore + escore
                    self.myScore[tx][ty] = myscore
                    self.enScore[tx][ty] = escore
                    num += 1
                tx = tx + dir[i][0]
                ty = ty + dir[i][1]

    def global_eva(self):
        summation = 0
        for i in range(self.chessboard_size):
            for j in range(self.chessboard_size):
                if self.chessboard[i][j] == COLOR_NONE:
                    summation += self.myScore[i][j] - self.enScore[i][j]
        return summation