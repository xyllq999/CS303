#!/usr/bin/env python3
import numpy as np
import os
import sys
try:
    from tkinter import *
except ImportError:  # Python 2.x
    PythonVersion = 2
    from Tkinter import *
    from tkFont import Font
    from ttk import *
    from tkMessageBox import *
    import tkFileDialog
else:  # Python 3.x
    PythonVersion = 3
    from tkinter.font import Font
    from tkinter.ttk import *
    from tkinter.messagebox import *

# tags for file
file_tag = 'train'  # train/test

# The board size of go game
BOARD_SIZE = 9
COLOR_BLACK = -1
COLOR_WHITE = 1
COLOR_NONE = 0
POINT_STATE_CHECKED = 100
POINT_STATE_UNCHECKED = 101
POINT_STATE_NOT_ALIVE = 102
POINT_STATE_ALIVE = 103
POINT_STATE_EMPYT = 104


def read_go(file_name):
    # read from txt file and save as a matrix
    go_arr = np.zeros((BOARD_SIZE, BOARD_SIZE))
    for line in open(file_name):
        line = line.strip()
        lst = line.split()
        row = int(lst[0])
        col = int(lst[1])
        val = int(lst[2])
        go_arr[row, col] = val
    return go_arr


def plot_go(go_arr, txt='Default'):
    # Visualization of a go matrix
    # First draw a canvas with 9*9 grid
    root = Tk()
    cv = Canvas(root, width=50 * (BOARD_SIZE + 1),
                height=50 * (BOARD_SIZE + 1), bg='#F7DCB4')
    cv.create_text(250, 10, text=txt, fill='blue')
    cv.pack(side=LEFT)
    size = 50
    for x in range(BOARD_SIZE):
        cv.create_line(size + x * size, size, size + x *
                       size, size + (BOARD_SIZE - 1) * size)
    for y in range(BOARD_SIZE):
        cv.create_line(size, size + y * size, size +
                       (BOARD_SIZE - 1) * size, size + size * y)
    # Second draw white and black circles on cross points
    offset = 20
    idx_black = np.argwhere(go_arr == COLOR_BLACK)
    idx_white = np.argwhere(go_arr == COLOR_WHITE)
    len_black = idx_black.shape[0]
    len_white = idx_white.shape[0]
    for i in range(len_black):
        if idx_black[i, 0] >= BOARD_SIZE or idx_black[i, 1] >= BOARD_SIZE:
            print('IndexError: index out of range')
            sys.exit(0)
        else:
            new_x = 50 * (idx_black[i, 1] + 1)
            new_y = 50 * (idx_black[i, 0] + 1)
            cv.create_oval(new_x - offset, new_y - offset, new_x + offset,
                           new_y + offset, width=1, fill='black', outline='black')
    for i in range(len_white):
        if idx_white[i, 0] >= BOARD_SIZE or idx_white[i, 1] >= BOARD_SIZE:
            print('IndexError: index out of range')
            sys.exit(0)
        else:
            new_x = 50 * (idx_white[i, 1] + 1)
            new_y = 50 * (idx_white[i, 0] + 1)
            cv.create_oval(new_x - offset, new_y - offset, new_x + offset,
                           new_y + offset, width=1, fill='white', outline='white')
    root.mainloop()


#-------------------------------------------------------
# Rule judgement  *need finish
#-------------------------------------------------------


def is_alive(check_state, go_arr, i, j, color_type):
    '''
    This function checks whether the point (i,j) and its connected points with the same color are alive, it can only be used for white/black chess only
    Depth-first searching.
    :param check_state: The guard array to verify whether a point is checked
    :param go_arr: chess board
    :param i: x-index of the start point of searching
    :param j: y-index of the start point of searching
    :return: POINT_STATE_CHECKED/POINT_STATE_ALIVE/POINT_STATE_NOT_ALIVE, 
    POINT_STATE_CHECKED=> the start point (i,j) is checked, POINT_STATE_ALIVE=> the point and its linked points with the same color are alive, POINT_STATE_NOT_ALIVE=>the point and its linked points with the same color are dead
    '''
    left_pos = None
    right_pos = None
    up_pos = None
    down_pos = None
    has_qi = False
    connected_pos = [(i, j)]
    visited = set()
    # print( go_arr.shape[0], go_arr.shape[1])
    while len(connected_pos) > 0:
        # print(connected_pos)
        (curi, curj) = connected_pos.pop()
        visited.add((curi, curj))
        if check_state[curi, curj] != POINT_STATE_UNCHECKED:
            continue
        else:
            check_state[curi, curj] = POINT_STATE_CHECKED
        if curi > 0:
            left_pos = (curi - 1, curj)
            if go_arr[left_pos[0], left_pos[1]] == COLOR_NONE:
                check_state[left_pos[0], left_pos[1]] = POINT_STATE_EMPYT
                has_qi = True
            elif go_arr[left_pos[0], left_pos[1]] == color_type:
                connected_pos.append(left_pos)
        if curj > 0:
            up_pos = (curi, curj - 1)
            if go_arr[up_pos[0], up_pos[1]] == COLOR_NONE:
                check_state[up_pos[0], up_pos[1]] = POINT_STATE_EMPYT
                has_qi = True
            elif go_arr[up_pos[0], up_pos[1]] == color_type:
                connected_pos.append(up_pos)
        if curi < go_arr.shape[0] - 1:
            right_pos = (curi + 1, curj)
            if go_arr[right_pos[0], right_pos[1]] == COLOR_NONE:
                check_state[left_pos[0], left_pos[1]] = POINT_STATE_EMPYT
                has_qi = True
            elif go_arr[right_pos[0], right_pos[1]] == color_type:
                connected_pos.append(right_pos)
        if curj < go_arr.shape[0] - 1:
            down_pos = (curi, curj + 1)
            if go_arr[down_pos[0], down_pos[1]] == COLOR_NONE:
                check_state[down_pos[0], down_pos[1]] = POINT_STATE_EMPYT
                has_qi = True
            elif go_arr[down_pos[0], down_pos[1]] == color_type:
                connected_pos.append(down_pos)
    if has_qi:
        for p in visited:
            check_state[p[0], p[1]] = POINT_STATE_ALIVE
    else:
        # print("GG")
        for p in visited:
            # print(p)
            check_state[p[0], p[1]] = POINT_STATE_NOT_ALIVE

    return check_state[i, j]


def __init_check_state2(go_arr):
    check_state = np.zeros(go_arr.shape)
    check_state[:] = POINT_STATE_EMPYT
    tmp_indx = np.where(go_arr != 0)
    check_state[tmp_indx] = POINT_STATE_UNCHECKED
    return check_state


def go_judege(go_arr):
    '''
    :param go_arr: the numpy array contains the chess board
    :return: whether this chess board fit the go rules in the document
             False => unfit rule
             True => ok
    '''
    # print(go_arr)
    is_fit_go_rule = True
    check_state = __init_check_state2(go_arr)
    for i in range(go_arr.shape[0]):
        for j in range(go_arr.shape[1]):
            if check_state[i, j] == POINT_STATE_UNCHECKED:
                tmp_alive = is_alive(check_state, go_arr, i, j, go_arr[i, j])
                if tmp_alive == POINT_STATE_NOT_ALIVE:  # once the go rule is broken, stop the searching and return the state
                    is_fit_go_rule = False
                    break
            else:
                pass  # pass if the point and its lined points are checked
    return is_fit_go_rule

#-------------------------------------------------------
# User strategy  *need finish
#-------------------------------------------------------


def __get_surrounding(go_arr, point):
    '''
    :param go_arr: chessboard
    :param point: (i,j) point to be checked
    left,right,up,below
    '''
    neighbors = list()
    (i, j) = point
    if i > 0:
        left_pos = (i - 1, j)
        neighbors.append(left_pos)
    if j > 0:
        up_pos = (i, j - 1)
        neighbors.append(up_pos)
    if i < go_arr.shape[0] - 1:
        right_pos = (i + 1, j)
        neighbors.append(right_pos)
    if j < go_arr.shape[1] - 1:
        down_pos = (i, j + 1)
        neighbors.append(down_pos)

    return neighbors


def __get_qi_set(go_arr, point, check_state, color_type):
    '''
    can be accelerated by transmitting a status matrix
    :param go_arr: chessboard
    :param point: (i,j) point to be checked
    :return status of the point
    '''
    left_pos = None
    right_pos = None
    up_pos = None
    down_pos = None
    has_qi = False
    connected_pos = [(point[0], point[1])]
    visited = set()
    qi_pos = set()

    # print( go_arr.shape[0], go_arr.shape[1])
    while connected_pos:
        # print(connected_pos)
        (curi, curj) = connected_pos.pop()
        visited.add((curi, curj))
        if check_state[curi, curj][0] != POINT_STATE_UNCHECKED:
            continue
        else:
            check_state[curi, curj, :] = (POINT_STATE_CHECKED, 0)
        if curi > 0:
            left_pos = (curi - 1, curj)
            if go_arr[left_pos[0], left_pos[1]] == COLOR_NONE:
                check_state[left_pos[0], left_pos[1], 0] = POINT_STATE_EMPYT
                has_qi = True
                qi_pos.add(left_pos)
            elif go_arr[left_pos[0], left_pos[1]] == color_type:
                connected_pos.append(left_pos)
        if curj > 0:
            up_pos = (curi, curj - 1)
            if go_arr[up_pos[0], up_pos[1]] == COLOR_NONE:
                check_state[up_pos[0], up_pos[1], 0] = POINT_STATE_EMPYT
                has_qi = True
                qi_pos.add(up_pos)
            elif go_arr[up_pos[0], up_pos[1]] == color_type:
                connected_pos.append(up_pos)
        if curi < go_arr.shape[0] - 1:
            right_pos = (curi + 1, curj)
            if go_arr[right_pos[0], right_pos[1]] == COLOR_NONE:
                check_state[left_pos[0], left_pos[1], 0] = POINT_STATE_EMPYT
                has_qi = True
                qi_pos.add(right_pos)
            elif go_arr[right_pos[0], right_pos[1]] == color_type:
                connected_pos.append(right_pos)
        if curj < go_arr.shape[0] - 1:
            down_pos = (curi, curj + 1)
            if go_arr[down_pos[0], down_pos[1]] == COLOR_NONE:
                check_state[down_pos[0], down_pos[1], 0] = POINT_STATE_EMPYT
                has_qi = True
                qi_pos.add(down_pos)
            elif go_arr[down_pos[0], down_pos[1]] == color_type:
                connected_pos.append(down_pos)
    if has_qi:
        for p in visited:
            check_state[p][:] = (POINT_STATE_ALIVE, len(qi_pos))
    else:
        for p in visited:
            check_state[p][:] = (POINT_STATE_NOT_ALIVE, 0)

    return qi_pos


def __remove_block(go_arr, pos, color):
    block = [pos, ]
    while block:
        cur_pos = block.pop()
        go_arr[cur_pos] = COLOR_NONE
        surrounding_pos = __get_surrounding(go_arr, cur_pos)
        for pos in surrounding_pos:
            # print(pos)
            if go_arr[pos] == color:
                block.append(pos)


def __get_result(go_arr, newpos):
    surrounding_pos = __get_surrounding(go_arr, newpos)
    go_arr_copy = np.copy(go_arr)
    go_arr_copy[newpos] = COLOR_WHITE

    # print("surround", surrounding_pos)
    for pos in surrounding_pos:
        if go_arr_copy[pos] == COLOR_BLACK:
            check_state = __init_check_state2(go_arr_copy)
            # print("check", pos, check_state)
            alive = is_alive(check_state, go_arr_copy,
                             pos[0], pos[1], COLOR_BLACK)
            if alive == POINT_STATE_NOT_ALIVE:
                # print("remove", pos)
                __remove_block(go_arr_copy, pos, COLOR_BLACK)
                check_state[:] = POINT_STATE_EMPYT
                tmp_indx = np.where(go_arr_copy != 0)
                check_state[tmp_indx] = POINT_STATE_UNCHECKED

    return go_arr_copy


def __get_state(go_arr, point, check_state, color_type):
    '''
    can be accelerated by transmitting a status matrix
    :param go_arr: chessboard
    :param point: (i,j) point to be checked
    :return status of the point
    '''
    left_pos = None
    right_pos = None
    up_pos = None
    down_pos = None
    has_qi = False
    connected_pos = [(point[0], point[1])]
    visited = set()
    qi_pos = set()

    # print( go_arr.shape[0], go_arr.shape[1])
    while connected_pos:
        # print(connected_pos)
        (curi, curj) = connected_pos.pop()
        visited.add((curi, curj))
        if check_state[curi, curj][0] != POINT_STATE_UNCHECKED:
            continue
        else:
            check_state[curi, curj, :] = (POINT_STATE_CHECKED, 0)
        if curi > 0:
            left_pos = (curi - 1, curj)
            if go_arr[left_pos[0], left_pos[1]] == COLOR_NONE:
                check_state[left_pos[0], left_pos[1], 0] = POINT_STATE_EMPYT
                has_qi = True
                qi_pos.add(left_pos)
            elif go_arr[left_pos[0], left_pos[1]] == color_type:
                connected_pos.append(left_pos)
        if curj > 0:
            up_pos = (curi, curj - 1)
            if go_arr[up_pos[0], up_pos[1]] == COLOR_NONE:
                check_state[up_pos[0], up_pos[1], 0] = POINT_STATE_EMPYT
                has_qi = True
                qi_pos.add(up_pos)
            elif go_arr[up_pos[0], up_pos[1]] == color_type:
                connected_pos.append(up_pos)
        if curi < go_arr.shape[0] - 1:
            right_pos = (curi + 1, curj)
            if go_arr[right_pos[0], right_pos[1]] == COLOR_NONE:
                check_state[left_pos[0], left_pos[1], 0] = POINT_STATE_EMPYT
                has_qi = True
                qi_pos.add(right_pos)
            elif go_arr[right_pos[0], right_pos[1]] == color_type:
                connected_pos.append(right_pos)
        if curj < go_arr.shape[0] - 1:
            down_pos = (curi, curj + 1)
            if go_arr[down_pos[0], down_pos[1]] == COLOR_NONE:
                check_state[down_pos[0], down_pos[1], 0] = POINT_STATE_EMPYT
                has_qi = True
                qi_pos.add(down_pos)
            elif go_arr[down_pos[0], down_pos[1]] == color_type:
                connected_pos.append(down_pos)
    if has_qi:
        for p in visited:
            check_state[p][:] = (POINT_STATE_ALIVE, len(qi_pos))
    else:
        for p in visited:
            check_state[p][:] = (POINT_STATE_NOT_ALIVE, 0)

    return check_state[point]


def user_step_eat(go_arr):
    '''
    :param go_arr: chessboard
    :return: ans=>where to put one step forward for white chess pieces so that some black chess pieces will be killed; user_arr=> the result chessboard after the step
    '''
    # first find the chesses with only one qi
    # tranverse all black blocks
    newpos_set = set()
    check_state = __init_check_state(go_arr)
    for i in range(go_arr.shape[0]):
        for j in range(go_arr.shape[1]):
            if check_state[i, j, 0] == POINT_STATE_UNCHECKED:
                if go_arr[i, j] == COLOR_BLACK:
                    qi_pos_set = __get_qi_set(
                        go_arr, (i, j), check_state, COLOR_BLACK)
                    if qi_pos_set and len(qi_pos_set) == 1:
                        newpos = qi_pos_set.pop()
                        newpos_set.add(newpos)
    new_arr = np.copy(go_arr)
    for newpos in newpos_set:
        new_arr = __get_result(new_arr, newpos)

    return newpos_set, new_arr


def __init_check_state(go_arr):
    check_state = np.zeros(
        (go_arr.shape[0], go_arr.shape[1], 2), dtype=np.int32)
    check_state[:] = np.array([POINT_STATE_EMPYT, 0])
    tmp_indx = np.where(go_arr != 0)
    check_state[tmp_indx] = np.array([POINT_STATE_UNCHECKED, 0])
    return check_state


def user_setp_possible(go_arr):
    '''
    :param go_arr: chessboard
    :return: ans=> all the possible locations to put one step forward for white chess pieces
    check block by block (connected)
    '''

    possible_list = list()
    check_state = __init_check_state(go_arr)
    # print(check_state)
    for i in range(go_arr.shape[0]):
        for j in range(go_arr.shape[1]):
            # have space for new white chess
            #print(check_state[i, j])
            if check_state[i, j, 0] == POINT_STATE_EMPYT:
                # print(check_state[i, j], (i, j))
                has_qi = False
                surrounding_pos = __get_surrounding(go_arr, (i, j))
                # detect the surrounding
                for pos in surrounding_pos:
                    if pos:
                        # 1. there is qi around the empty
                        if go_arr[pos] == COLOR_NONE:
                            # check_state[pos][:] = (POINT_STATE_CHECKED, 0)
                            # print("CS:", check_state[pos])
                            has_qi = True
                        # 2. new chess can be connected and the block will has qi
                        elif go_arr[pos] == COLOR_WHITE:
                            go_arr_copy = np.copy(go_arr)
                            if check_state[pos][0] == POINT_STATE_UNCHECKED:
                                state, num_qi = __get_state(
                                    go_arr_copy, pos, check_state, COLOR_WHITE)
                            else:
                                num_qi = check_state[pos][1]
                            if num_qi > 1:
                                has_qi = True
                # 3. some other chess can be eat
                if not has_qi:
                    go_arr_copy = np.copy(go_arr)
                    go_arr_copy[i, j] = COLOR_WHITE
                    __init_check_state(go_arr_copy)
                    for pos in surrounding_pos:
                        if check_state[pos][0] == POINT_STATE_UNCHECKED:
                            state, num_qi = __get_state(
                                go_arr_copy, pos, check_state, COLOR_BLACK)
                        else:
                            state = check_state[pos][0]
                        if state == POINT_STATE_NOT_ALIVE:
                            has_qi = True
                            break
                if has_qi:
                    possible_list.append((i, j))
    return possible_list


if __name__ == "__main__":
    chess_rule_monitor = True
    problem_tag = "Default"
    ans = []
    user_arr = np.zeros([0, 0])

    writeout = ""

    # The first problem: rule checking
    problem_tag = "Problem 0: rule checking"
    go_arr = read_go('{}_0.txt'.format(file_tag))
    plot_go(go_arr, problem_tag)
    chess_rule_monitor = go_judege(go_arr)
    print("{}:{}".format(problem_tag, chess_rule_monitor))
    plot_go(go_arr, '{}=>{}'.format(problem_tag, chess_rule_monitor))
    writeout += 'train_0\n{}\n\n'.format(chess_rule_monitor)

    problem_tag = "Problem 00: rule checking"
    go_arr = read_go('{}_00.txt'.format(file_tag))
    plot_go(go_arr, problem_tag)
    chess_rule_monitor = go_judege(go_arr)
    print("{}:{}".format(problem_tag, chess_rule_monitor))
    plot_go(go_arr, '{}=>{}'.format(problem_tag, chess_rule_monitor))
    writeout += 'train_00\n{}\n\n'.format(chess_rule_monitor)

    # The second~fifth prolbem: forward one step and eat the adverse points on the chessboard
    for i in range(1, 5):
        problem_tag = "Problem {}: forward one step".format(i)
        go_arr = read_go('{}_{}.txt'.format(file_tag, i))
        plot_go(go_arr, problem_tag)
        chess_rule_monitor = go_judege(go_arr)
        ans, user_arr = user_step_eat(go_arr)  # need finish
        print("{}:{}".format(problem_tag, ans))
        plot_go(user_arr, '{}=>{}'.format(problem_tag, chess_rule_monitor))
        tmp = ""
        for p in ans:
            tmp += '{} {}\n'.format(p[0], p[1])
        writeout += '{}_{}\n{}\n'.format(file_tag, i,tmp)

    # The sixth problem: find all the postion which can place a white chess pieces
    problem_tag = "Problem {}: all possible position".format(5)
    go_arr = read_go('{}_{}.txt'.format(file_tag, 5))
    plot_go(go_arr, problem_tag)
    chess_rule_monitor = go_judege(go_arr)
    ans = user_setp_possible(go_arr)  # need finish
    print("{}:{}".format(problem_tag, ans))
    plot_go(go_arr, '{}=>{}'.format(problem_tag, chess_rule_monitor))
    tmp = ""
    for p in ans:
        tmp += '{} {}\n'.format(p[0], p[1])
    writeout += '{}_{}\n{}'.format(file_tag, 5,tmp)

    fileid = open("answer.txt", mode='w')
    try:
        fileid.write(writeout)
    except IOError as identifier:
        print("Error writing the file.!")
    fileid.close()
