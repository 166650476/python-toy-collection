import tkinter as tk

# ===================== 外观参数 =====================
CELL_SIZE = 60
BOARD_MARGIN = 40
PIECE_FONT = "楷体"

BOARD_BG = "#F0D9B5"
LINE_COLOR = "#5D3A1A"
PIECE_BG = "#F5DEB3"
PIECE_BORDER = "#8B4513"
RED_COLOR = "#C41E3A"
BLACK_COLOR = "#1A1A1A"
SELECT_COLOR = "#FFD700"
# ===================================================

root = tk.Tk()
root.title("中国象棋（带规则）")
canvas_w = CELL_SIZE * 8 + BOARD_MARGIN * 2
canvas_h = CELL_SIZE * 9 + BOARD_MARGIN * 2
canvas = tk.Canvas(root, bg=BOARD_BG, width=canvas_w, height=canvas_h)
canvas.pack()

board = []
selected = None

# ===================== 棋盘初始化 =====================
def init_board_data():
    global board
    board = [[None]*10 for _ in range(9)]
    
    # 黑方
    black_back = ["車","馬","象","士","將","士","象","馬","車"]
    for col in range(9):
        board[col][0] = {"text":black_back[col], "red":False}
    board[1][2] = {"text":"砲","red":False}
    board[7][2] = {"text":"砲","red":False}
    for col in [0,2,4,6,8]:
        board[col][3] = {"text":"卒","red":False}
    
    # 红方
    red_back = ["車","馬","相","仕","帥","仕","相","馬","車"]
    for col in range(9):
        board[col][9] = {"text":red_back[col], "red":True}
    board[1][7] = {"text":"炮","red":True}
    board[7][7] = {"text":"炮","red":True}
    for col in [0,2,4,6,8]:
        board[col][6] = {"text":"兵","red":True}

def draw_board():
    for i in range(10):
        y = BOARD_MARGIN + i * CELL_SIZE
        canvas.create_line(BOARD_MARGIN, y, BOARD_MARGIN+8*CELL_SIZE, y,
                           fill=LINE_COLOR, width=2, tags="board")
    for i in range(9):
        x = BOARD_MARGIN + i * CELL_SIZE
        canvas.create_line(x, BOARD_MARGIN, x, BOARD_MARGIN+4*CELL_SIZE,
                           fill=LINE_COLOR, width=2, tags="board")
        canvas.create_line(x, BOARD_MARGIN+5*CELL_SIZE, x, BOARD_MARGIN+9*CELL_SIZE,
                           fill=LINE_COLOR, width=2, tags="board")
    canvas.create_text(BOARD_MARGIN+2*CELL_SIZE, BOARD_MARGIN+4.5*CELL_SIZE,
                       text="楚 河", fill=LINE_COLOR, font=("楷体",20,"bold"), tags="board")
    canvas.create_text(BOARD_MARGIN+6*CELL_SIZE, BOARD_MARGIN+4.5*CELL_SIZE,
                       text="汉 界", fill=LINE_COLOR, font=("楷体",20,"bold"), tags="board")
    # 九宫斜线
    canvas.create_line(BOARD_MARGIN+3*CELL_SIZE, BOARD_MARGIN,
                       BOARD_MARGIN+5*CELL_SIZE, BOARD_MARGIN+2*CELL_SIZE,
                       fill=LINE_COLOR, width=2, tags="board")
    canvas.create_line(BOARD_MARGIN+5*CELL_SIZE, BOARD_MARGIN,
                       BOARD_MARGIN+3*CELL_SIZE, BOARD_MARGIN+2*CELL_SIZE,
                       fill=LINE_COLOR, width=2, tags="board")
    canvas.create_line(BOARD_MARGIN+3*CELL_SIZE, BOARD_MARGIN+7*CELL_SIZE,
                       BOARD_MARGIN+5*CELL_SIZE, BOARD_MARGIN+9*CELL_SIZE,
                       fill=LINE_COLOR, width=2, tags="board")
    canvas.create_line(BOARD_MARGIN+5*CELL_SIZE, BOARD_MARGIN+7*CELL_SIZE,
                       BOARD_MARGIN+3*CELL_SIZE, BOARD_MARGIN+9*CELL_SIZE,
                       fill=LINE_COLOR, width=2, tags="board")

def draw_one_piece(col, row, piece, is_selected=False):
    x = BOARD_MARGIN + col * CELL_SIZE
    y = BOARD_MARGIN + row * CELL_SIZE
    r = CELL_SIZE // 2 - 4
    
    if is_selected:
        canvas.create_oval(x-r-3, y-r-3, x+r+3, y+r+3,
                           outline=SELECT_COLOR, width=3, tags="pieces")
    canvas.create_oval(x-r+2, y-r+2, x+r+2, y+r+2,
                       fill="#A0826D", outline="", tags="pieces")
    canvas.create_oval(x-r, y-r, x+r, y+r,
                       fill=PIECE_BG, outline=PIECE_BORDER, width=2, tags="pieces")
    color = RED_COLOR if piece["red"] else BLACK_COLOR
    canvas.create_text(x, y, text=piece["text"], fill=color,
                       font=(PIECE_FONT, int(r*0.85), "bold"), tags="pieces")

def refresh_pieces():
    canvas.delete("pieces")
    for col in range(9):
        for row in range(10):
            if board[col][row]:
                draw_one_piece(col, row, board[col][row], selected == (col, row))

# ===================== 核心：走棋规则校验 =====================
def check_path_clear(c1, r1, c2, r2):
    """检查横竖路径上是否没有棋子（车、炮走棋用）"""
    if c1 == c2:
        for r in range(min(r1,r2)+1, max(r1,r2)):
            if board[c1][r]: return False
    else:
        for c in range(min(c1,c2)+1, max(c1,c2)):
            if board[c][r1]: return False
    return True

def count_path_pieces(c1, r1, c2, r2):
    """数路径上的棋子数（炮吃子用）"""
    count = 0
    if c1 == c2:
        for r in range(min(r1,r2)+1, max(r1,r2)):
            if board[c1][r]: count += 1
    else:
        for c in range(min(c1,c2)+1, max(c1,c2)):
            if board[c][r1]: count += 1
    return count

def check_jiangshuai(from_c, from_r, to_c, to_r, is_red):
    """模拟移动后，检查将帅是否照面（照面则不合法）"""
    old_from = board[from_c][from_r]
    old_to = board[to_c][to_r]
    board[to_c][to_r] = old_from
    board[from_c][from_r] = None
    
    jiang = shuai = None
    for c in range(9):
        for r in range(10):
            p = board[c][r]
            if p and p["text"] == "將" and not p["red"]: jiang = (c,r)
            if p and p["text"] == "帥" and p["red"]: shuai = (c,r)
    
    valid = True
    if jiang and shuai and jiang[0] == shuai[0]:
        col = jiang[0]
        for r in range(min(jiang[1],shuai[1])+1, max(jiang[1],shuai[1])):
            if board[col][r]: break
        else:
            valid = False
    
    board[from_c][from_r] = old_from
    board[to_c][to_r] = old_to
    return valid

def is_move_valid(from_col, from_row, to_col, to_row):
    """判断一步棋是否符合规则"""
    piece = board[from_col][from_row]
    target = board[to_col][to_row]
    
    if from_col == to_col and from_row == to_row: return False
    if target and target["red"] == piece["red"]: return False
    
    p_text = piece["text"]
    is_red = piece["red"]
    dc = abs(to_col - from_col)
    dr = abs(to_row - from_row)

    # 1. 将/帅：九宫內走一步横竖，不能照面
    if p_text in ["將", "帥"]:
        if is_red:
            if not (7 <= to_row <=9 and 3 <= to_col <=5): return False
        else:
            if not (0 <= to_row <=2 and 3 <= to_col <=5): return False
        if (dc == 1 and dr == 0) or (dc == 0 and dr == 1):
            return check_jiangshuai(from_col, from_row, to_col, to_row, is_red)
        return False

    # 2. 士/仕：九宫內斜走一步
    elif p_text in ["士", "仕"]:
        if is_red:
            if not (7 <= to_row <=9 and 3 <= to_col <=5): return False
        else:
            if not (0 <= to_row <=2 and 3 <= to_col <=5): return False
        return dc == 1 and dr == 1

    # 3. 象/相：走田，不能过河，塞象眼
    elif p_text in ["象", "相"]:
        if is_red and to_row < 5: return False
        if not is_red and to_row > 4: return False
        if dc == 2 and dr == 2:
            eye_c, eye_r = (from_col+to_col)//2, (from_row+to_row)//2
            if board[eye_c][eye_r]: return False
            return True
        return False

    # 4. 马：走日，蹩马腿
    elif p_text == "馬":
        if (dc == 1 and dr == 2) or (dc == 2 and dr == 1):
            if dc == 2:
                leg_c, leg_r = (from_col+to_col)//2, from_row
                if board[leg_c][leg_r]: return False
            else:
                leg_c, leg_r = from_col, (from_row+to_row)//2
                if board[leg_c][leg_r]: return False
            return True
        return False

    # 5. 车：横竖任意步，中间无子
    elif p_text == "車":
        if dc != 0 and dr != 0: return False
        return check_path_clear(from_col, from_row, to_col, to_row)

    # 6. 炮：走棋同车，吃子隔一个炮架
    elif p_text in ["炮", "砲"]:
        if dc != 0 and dr != 0: return False
        cnt = count_path_pieces(from_col, from_row, to_col, to_row)
        return cnt == 0 if not target else cnt == 1

    # 7. 兵/卒：未过河只能前，过河可左右，不能退
    elif p_text in ["兵", "卒"]:
        if dc + dr != 1: return False
        if is_red:
            if to_row > from_row: return False
            if from_row > 4 and dc != 0: return False
        else:
            if to_row < from_row: return False
            if from_row < 5 and dc != 0: return False
        return True

    return False

# ===================== 鼠标交互 =====================
def on_mouse_click(event):
    global selected
    col = round((event.x - BOARD_MARGIN) / CELL_SIZE)
    row = round((event.y - BOARD_MARGIN) / CELL_SIZE)
    if col < 0 or col > 8 or row < 0 or row > 9: return
    target = board[col][row]
    
    if not selected:
        if target:
            selected = (col, row)
            refresh_pieces()
        return
    
    sel_col, sel_row = selected
    sel_piece = board[sel_col][sel_row]
    
    if target and target["red"] == sel_piece["red"]:
        selected = (col, row)
        refresh_pieces()
        return
    
    # 规则校验通过才允许移动
    if is_move_valid(sel_col, sel_row, col, row):
        board[col][row] = sel_piece
        board[sel_col][sel_row] = None
        selected = None
        refresh_pieces()

# ===================== 启动 =====================
draw_board()
init_board_data()
refresh_pieces()
canvas.bind("<Button-1>", on_mouse_click)

root.mainloop()
