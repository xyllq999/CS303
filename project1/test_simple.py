import unittest
from project1 import test
import numpy as npy

from project1.xuyan_submit import AI

ini_board = npy.zeros([8, 8], dtype=npy.int8)
board1 = npy.zeros([8, 8], dtype=npy.int8)

ini_board[3][3], ini_board[4][4], ini_board[3][4], ini_board[4][3] = 1, 1, -1, -1
board1[-1][0], board1[0][-1], board1[6][6], board1[0][0], board1[5][5] = 1, 1, -1, -1, 1

test1_ans = [(2, 4), (3, 5), (4, 2), (5, 3)]
test2_ans = [(7, 7)]


class MyTestCase(unittest.TestCase):
    def test1(self):
        ai = AI(8, 1, 5)
        ai.go(ini_board)
        self.assertEqual(ai.candidate_list, test1_ans)

    def test2(self):
        ai = AI(8, 1, 5)
        ai.go(board1)
        self.assertEqual(ai.candidate_list, test2_ans)


if __name__ == '__main__':
    unittest.main()
