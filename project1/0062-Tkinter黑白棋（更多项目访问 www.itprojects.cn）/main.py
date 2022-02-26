import random
from tkinter import *
from tkinter.messagebox import *

GAME_OVER = False
GAME_OVER_STR = 'Game Over Score '
IMAGES = None
MAIN_BOARD = None
CV = None
PLAYER_TITLE = None
COMPUTER_TITLE = None
TURN = None


def reset_board(board):
    """重置棋盘"""
    for x in range(8):
        for y in range(8):
            board[x][y] = 'none'
    # 开始时的棋子
    board[3][3] = 'black'
    board[3][4] = 'white'
    board[4][3] = 'white'
    board[4][4] = 'black'


def get_new_board():
    """开局时建立新棋盘"""
    board = []
    for i in range(8):
        board.append(['none'] * 8)
    return board


def is_valid_move(board, tile, xstart, ystart):
    """是否是合法走法，如果合法返回需要翻转的棋子列表"""
    # 如果该位置已经有棋子或者出界了，返回False
    if not is_on_board(xstart, ystart) or board[xstart][ystart] != 'none':
        return False
    # 临时将tile 放到指定的位置
    board[xstart][ystart] = tile
    if tile == 'black':
        otherTile = 'white'
    else:
        otherTile = 'black'
    # 要被翻转的棋子
    titles_to_flip = []
    for xdirection, ydirection in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
        x, y = xstart, ystart
        x += xdirection
        y += ydirection
        if is_on_board(x, y) and board[x][y] == otherTile:
            x += xdirection
            y += ydirection
            if not is_on_board(x, y):
                continue
            # 一直走到出界或不是对方棋子的位置
            while board[x][y] == otherTile:
                x += xdirection
                y += ydirection
                if not is_on_board(x, y):
                    break
            # 出界了，则没有棋子要翻转OXXXXX
            if not is_on_board(x, y):
                continue
            # 是自己的棋子OXXXXXXO
            if board[x][y] == tile:
                while True:
                    x -= xdirection
                    y -= ydirection
                    # 回到了起点则结束
                    if x == xstart and y == ystart:
                        break
                    # 需要翻转的棋子
                    titles_to_flip.append([x, y])
    # 将前面临时放上的棋子去掉，即还原棋盘
    board[xstart][ystart] = 'none'  # restore the empty space
    # 没有要被翻转的棋子，则走法非法。翻转棋的规则。
    if len(titles_to_flip) == 0:  # If no tiles were flipped, this is not a valid move.
        return False
    return titles_to_flip


def is_on_board(x, y):
    """是否出界"""
    return 0 <= x <= 7 and 0 <= y <= 7


def get_valid_moves(board, tile):
    """获取可落子的位置"""
    valid_moves = []
    for x in range(8):
        for y in range(8):
            if is_valid_move(board, tile, x, y):
                valid_moves.append([x, y])
    return valid_moves


def get_score_of_board(board):
    """获取棋盘上黑白双方的棋子数"""
    xscore = 0
    oscore = 0
    for x in range(8):
        for y in range(8):
            if board[x][y] == 'black':
                xscore += 1
            if board[x][y] == 'white':
                oscore += 1
    return {'black': xscore, 'white': oscore}


def who_goes_first():
    """决定谁先走"""
    if random.randint(0, 1) == 0:
        return 'computer'
    else:
        return 'player'


def make_move(board, tile, xstart, ystart):
    """将一个tile棋子放到(xstart, ystart)"""
    titles_to_flip = is_valid_move(board, tile, xstart, ystart)
    if titles_to_flip is False:
        return False
    board[xstart][ystart] = tile
    for x, y in titles_to_flip:  # titles_to_flip是需要翻转的棋子列表
        board[x][y] = tile  # 翻转棋子
    return True


def get_board_copy(board):
    """复制棋盘"""
    dupe_board = get_new_board()
    for x in range(8):
        for y in range(8):
            dupe_board[x][y] = board[x][y]
    return dupe_board


def is_on_corner(x, y):
    """是否在角上"""
    return (x == 0 and y == 0) or (x == 7 and y == 0) or (x == 0 and y == 7) or (x == 7 and y == 7)


def get_computer_move(board, computer_tile):
    """电脑走法，AI"""
    # 获取所以合法走法
    possible_moves = get_valid_moves(board, computer_tile)
    if not possible_moves:  # 如果没有合法走法
        print("电脑没有合法走法")
        return None

    # 打乱所有合法走法
    random.shuffle(possible_moves)
    # [x, y]在角上，则优先走，因为角上的不会被再次翻转
    for x, y in possible_moves:
        if is_on_corner(x, y):
            return [x, y]
    best_score = -1
    for x, y in possible_moves:
        dupe_board = get_board_copy(board)
        make_move(dupe_board, computer_tile, x, y)
        # 按照分数选择走法，优先选择翻转后分数最多的走法
        score = get_score_of_board(dupe_board)[computer_tile]
        if score > best_score:
            best_move = [x, y]
            best_score = score
    return best_move


def is_game_over(board):
    """是否游戏结束"""
    for x in range(8):
        for y in range(8):
            if board[x][y] == 'none':
                return False
    return True


def draw_chess_board():
    """画棋盘"""
    img1 = IMAGES[2]
    CV.create_image((360, 360), image=img1)
    CV.pack()


def call_back(event):
    """走棋"""
    global TURN
    # print ("clicked at", event.x, event.y,TURN)
    # x=(event.x)//40  #换算棋盘坐标
    # y=(event.y)//40
    if GAME_OVER is False and TURN == 'computer':  # 没轮到玩家走棋
        return
    col = int((event.x - 40) / 80)  # 换算棋盘坐标
    row = int((event.y - 40) / 80)
    if MAIN_BOARD[col][row] != "none":
        showinfo(title="提示", message="已有棋子")
    if make_move(MAIN_BOARD, PLAYER_TITLE, col, row):  # 将一个玩家棋子放到(col, row)
        if get_valid_moves(MAIN_BOARD, COMPUTER_TITLE):
            TURN = 'computer'
    # 电脑走棋
    if get_computer_move(MAIN_BOARD, COMPUTER_TITLE) is None:
        TURN = 'player'
        showinfo(title="玩家继续", message="玩家继续")
    else:
        computer_go()

    # 重画所有的棋子和棋盘
    draw_all()
    draw_can_go()
    if is_game_over(MAIN_BOARD):  # 游戏结束，显示双方棋子数量
        player_score = get_score_of_board(MAIN_BOARD)[PLAYER_TITLE]
        computer_score = get_score_of_board(MAIN_BOARD)[COMPUTER_TITLE]
        out_put_str = GAME_OVER_STR + "玩家:" + str(player_score) + ":" + "电脑:" + str(computer_score)
        showinfo(title="游戏结束提示", message=out_put_str)


def computer_go():
    """电脑走棋"""
    global TURN
    if GAME_OVER is False and TURN == 'computer':
        x, y = get_computer_move(MAIN_BOARD, COMPUTER_TITLE)  # 电脑AI走法
        make_move(MAIN_BOARD, COMPUTER_TITLE, x, y)
        # 玩家没有可行的走法了，则电脑继续，否则切换到玩家走
        if get_valid_moves(MAIN_BOARD, PLAYER_TITLE):
            TURN = 'player'
        else:
            if get_valid_moves(MAIN_BOARD, COMPUTER_TITLE):
                showinfo(title="电脑继续", message="电脑继续")
                computer_go()


def draw_all():
    """重画所有的棋子和棋盘"""
    draw_chess_board()
    for x in range(8):
        for y in range(8):
            if MAIN_BOARD[x][y] == 'black':
                CV.create_image((x * 80 + 80, y * 80 + 80), image=IMAGES[0])
                CV.pack()
            elif MAIN_BOARD[x][y] == 'white':
                CV.create_image((x * 80 + 80, y * 80 + 80), image=IMAGES[1])
                CV.pack()


def draw_can_go():
    """画提示位置"""
    temp_list = get_valid_moves(MAIN_BOARD, PLAYER_TITLE)
    for m in temp_list:
        x = m[0]
        y = m[1]
        CV.create_image((x * 80 + 80, y * 80 + 80), image=IMAGES[3])
        CV.pack()


def main():
    global IMAGES, MAIN_BOARD, CV, PLAYER_TITLE, COMPUTER_TITLE, TURN

    # 初始化
    root = Tk('黑白棋')
    root.title("黑白棋（更多项目实例请访问www.itprojects.cn）")
    # 加载图片
    IMAGES = [
        PhotoImage(file='images/black.png'),
        PhotoImage(file='images/white.png'),
        PhotoImage(file='images/board.png'),
        PhotoImage(file='images/Info2.png')
    ]

    # 创建棋盘数据
    MAIN_BOARD = get_new_board()
    reset_board(MAIN_BOARD)

    # 设置窗口
    CV = Canvas(root, bg='green', width=720, height=780)
    # 重画所有的棋子和棋盘
    draw_all()
    CV.pack()

    # 随机哪方先走
    TURN = who_goes_first()
    showinfo(title="游戏开始提示", message=TURN + "先走!")
    print(TURN, "先走!")

    if TURN == 'player':
        PLAYER_TITLE = 'black'
        COMPUTER_TITLE = 'white'
    else:
        PLAYER_TITLE = 'white'
        COMPUTER_TITLE = 'black'
        computer_go()

    # 重画所有的棋子和棋盘
    draw_all()
    draw_can_go()
    CV.bind("<Button-1>", call_back)
    CV.pack()

    root.mainloop()


if __name__ == '__main__':
    main()
