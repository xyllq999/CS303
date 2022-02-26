chessboard = [[0 for i in range(15)]for i in range(15)]
print(chessboard)
f = open('in.txt', 'r')
for line in f:
    a, b, c = line.split(',')
    a = int(a)
    b = int(b)
    c = int(c)
    chessboard[a][b] = c
print(chessboard)