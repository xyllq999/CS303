class EVALUATE 
list:
**positions** possible choose positions(candidate)
at the beginning, positions are the whole chessboard marked with
the level number
**result** 保存当前直线分析值
**line** 当前直线数据
**record** 初始化为15*15个[0, 0, 0, 0]
分别记录水平，垂直，左斜，右斜
**count** 对双方分别统计对应优胜棋型的个数
