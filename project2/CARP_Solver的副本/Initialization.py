import time

INF = 0x3f3f3f3f


class Pre_work:
    def __init__(self, filename):
        self.info_map = {}
        self.dis = None
        self.pure_dis = None
        self.demand = None
        self.V = 0
        self.R_E = 0
        self.NR_E = 0
        self.file_name = filename
        self.avg_require_cost = 0
        self.avg_total_cost = 0
        self.scan_graph()
        self.floyd()

    # marked cannot reach edge as INF = 0x3f3f3f3f
    # marked demand of edge cannot reach as -1
    def scan_graph(self):
        # print('file start time: %f' % time.time())
        with open(self.file_name) as f:
            for line in f.readlines():
                line = line.strip()
                if len(line.split(' : ')) == 2:
                    if line.split(' : ')[1].isdigit():
                        self.info_map[line.split(' : ')[0]] = int(line.split(' : ')[1])
                    else:
                        self.info_map[line.split(' : ')[0]] = line.split(' : ')[1]
                    if line.split(' : ')[0] == 'VERTICES':
                        self.V = int(line.split(':')[1])
                        self.dis = [[INF for i in range(self.V + 1)] for i in range(self.V + 1)]
                        self.pure_dis = [[INF for i in range(self.V + 1)] for i in range(self.V + 1)]
                        self.demand = [[0 for i in range(self.V + 1)] for i in range(self.V + 1)]
                    if line.split(' : ')[0] == 'REQUIRED EDGES':
                        self.R_E = int(line.split(' : ')[1])
                    if line.split(' : ')[0] == 'NON-REQUIRED EDGES':
                        self.NR_E = int(line.split(' : ')[1])
                    if line.split(' : ')[0] == 'TOTAL COST OF REQUIRED EDGES':
                        self.avg_require_cost = int(line.split(' : ')[1]) // self.R_E
                elif line[0].isalpha():
                    continue
                else:
                    a, b, c, d = map(int, line.split())
                    # print(a, b, c, d)
                    self.dis[a][b] = c
                    self.dis[b][a] = c
                    self.pure_dis[a][b] = c
                    self.pure_dis[b][a] = c
                    self.demand[a][b] = d
                    self.demand[b][a] = d
                    self.avg_require_cost += c
            self.avg_require_cost = self.avg_require_cost // (self.R_E + self.NR_E)
        # print('file end time: %f' % time.time())

    def floyd(self):
        for k in range(1, self.V + 1):
            for i in range(1, self.V + 1):
                for j in range(1, self.V + 1):
                    if self.dis[i][k] + self.dis[k][j] < self.dis[i][j]:
                        self.dis[i][j] = self.dis[i][k] + self.dis[k][j]
        for i in range(1, self.V + 1):
            self.dis[i][i] = 0

# if __name__ == '__main__':
#     p = Pre_work('egl-e1-A.dat')
#     p.scan_graph()
#     p.floyd()
# print(p.info_map)
# print(p.dis)
# print(p.demand)
