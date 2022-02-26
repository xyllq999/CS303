import argparse
import time
import numpy as np
from utils.gd import GD
# import check

np.set_printoptions(threshold=np.inf)

def parse():
    # parse args
    parser = argparse.ArgumentParser()
    parser.add_argument("train_data", help="train data")
    parser.add_argument("test_data", help="test data")
    parser.add_argument('-t', type=int, help="Time budget, the range is [60, 120].")
    return parser.parse_args()

def load_data_set(train_data_path, test_data_path):
    # read file
    with open(train_data_path, 'r') as f:
        lines = f.readlines()
        m = len(lines)
        n = len(lines[0].split()) - 1
        train_data = np.zeros((m, n))
        train_label = np.zeros(m)
        for l in range(m):
            lines[l] = [float(i) for i in lines[l].split()]
            train_data[l] = lines[l][:-1]
            train_label[l] = lines[l][-1]\

    with open(test_data_path, 'r') as f:
        lines = f.readlines()
        m = len(lines)
        n = len(lines[0].split())
        test_data = np.zeros((m, n))
        for l in range(m):
            lines[l] = [float(i) for i in lines[l].split()]
            test_data[l] = lines[l]
    return train_data, train_label, test_data

def output(result):
    for i in result:
        print(int(i))

if __name__ == "__main__":
#     start = time.time()
    args = parse()
    train_data, train_label, test_data = load_data_set(args.train_data, args.test_data)
#     print("train_data\n",train_data.shape)
#     print("train_label\n",train_label.shape)
    gd = GD(x=train_data, y=train_label)
    gd.train(args.t)
    result = gd.predict(test_data)
    output(result)
#     check.check(result)
#     print("T:", "%.2f" % (time.time() - start))
