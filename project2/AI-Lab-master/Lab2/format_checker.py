import argparse
import ast
from typing import List, Tuple

RouteList = List[List[Tuple[int, int]]]


def parse_output(output: List[str]) -> (RouteList, int):
    res: RouteList = []
    output, cost = output[0], output[1]
    # print(output)
    # print(cost)
    output = output.removeprefix('s ').replace('),(', ')|(')
    # print(output)
    output = list(filter(lambda x: x != "", output.split(',0,0,')))
    # print(output)
    output = [x.removeprefix('0,').removesuffix(',0\n').split('|') for x in output]
    # print(output)
    # print(len(output))
    for route in output:
        res.append([])
        # print(res)
        # print(route)
        for i, pair in enumerate(route):
            # print(pair.removesuffix(','))
            # print(ast.literal_eval(pair.removesuffix(',')))
            res[-1].append(ast.literal_eval(pair.removesuffix(',')))
            # print('success')
    # print(cost.removeprefix('q '))
    # print(int("173", 10))
    return res, int(cost.removeprefix('q '))


if __name__ == '__main__':
    parser = argparse \
        .ArgumentParser(description='Accept a CARP a student output, validate it.')
    parser.add_argument('output', metavar='OUTPUT', type=str, help='path to the output file')
    args = parser.parse_args()
    # print(open(args.output).readlines())
    try:
        carp_output = parse_output(open(args.output).readlines())
        print(carp_output)
        print("Congratulation!")
    except:
        print("Nope!")
