# -*- coding: utf-8 -*-
"""

@project: SVM
@author: yi
@e-mail: 11612917@mail.sustc.edu.cn
@file: SVM.py
@time: 18-12-21 下午12:14
"""

import numpy as np
import sys


def pegasos(point_list, label_list, _lambda, T):
    point_list = np.mat(point_list)
    length, width = np.shape(point_list)
    w = np.zeros(width)
    t = 0
    for _ in range(1, T):
        for i in range(length):
            t += 1
            eta = 1.0 / (_lambda * t)
            if label_list[i] * w * point_list[i].transpose() < 1:
                w = (1.0 - 1 / t) * w + eta * label_list[i] * point_list[i]
            else:
                w = (1.0 - 1 / t) * w
    return w


if __name__ == '__main__':
    train_data = sys.argv[1]
    test_data = sys.argv[2]
    time_budget = int(sys.argv[4])
    point_list = []
    label_list = []
    with open(train_data) as file:
        for line in file:
            line = line.strip().split(' ')
            li = []
            for x in line:
                li.append(float(x))
            single_point = li[0:10]
            label = li[10]
            point_list.append(single_point)
            label_list.append(label)
    w = pegasos(point_list, label_list, 0.05, 100)
    # print(w[0])
    # total_cnt = 0
    # right_cnt = 0
    point_list = []
    label_list = []
    with open(test_data) as file:
        for line in file:
            line = line.strip().split(' ')
            li = []
            for x in line:
                li.append(float(x))
            single_point = li[0:10]
            label = li[10]
            point_list.append(single_point)
            label_list.append(label)
    for i in range(len(label_list)):
        # total_cnt += 1
        if w[0] * np.mat(point_list[i]).transpose() > 0:
            print(1)
            # if label_list[i] == 1:
            #     right_cnt += 1
        else:
            print(-1)
    #         if label_list[i] == -1:
    #             right_cnt += 1
    # print(right_cnt / total_cnt)
