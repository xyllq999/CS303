# -*- coding: utf-8 -*-
"""

@project: ai_proj3
@author: yi
@e-mail: 11612917@mail.sustc.edu.cn
@file: a.py
@time: 18-12-10 下午2:57
"""

if __name__ == '__main__':
    for i in range(5):
        if i == 3:
            z = i
            for i in range(z, 5):
                print(i)
            break
        print(i)