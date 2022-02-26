import os
import time

file_list = []
for i in os.listdir(os.getcwd()):
    if str(i).endswith('.dat'):
        file_list.append(i)

if __name__ == '__main__':
    for i in file_list:
        start_time = time.time()
        print(i)
        os.system("python Init_Solution_generator.py %s -t 1 -s 19" % i)
        print(time.time() - start_time)


