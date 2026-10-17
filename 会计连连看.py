import tkinter as tk
from tkinter import messagebox
import random

# ========== 游戏参数 ==========
ROWS = 6
COLS = 8
CELL_SIZE = 70
MARGIN = 30

# 会计科目（12个，每个4次，共48格）
ACCOUNT_SUBJECTS = [
    "库存现金", "银行存款", "应收账款", "原材料",
    "固定资产", "累计折旧", "应付账款", "应交税费",
    "实收资本", "主营业务收入", "主营业务成本", "管理费用"
]

# 科目对应背景色
BG_COLORS = [
    "#FFE4E1", "#FFF0D4", "#FFFFD4", "#E0FFE0",
    "#E0F0FF", "#E8E0FF", "#FFE0F0", "#D4F5FF",
    "#E5FFE5", "#FFF5E0", "#FFE8E8", "#F0F0FF"
]

# ========== 生成地图 ==========
def generate_map():
    patterns = []
    for i in range(len(ACCOUNT_SUBJECTS)):
        for _ in range(4):
            patterns.append(i)
    random.shuffle(patterns)
    
    game_map = []
    idx = 0
    for r in range(ROWS):
        row = []
        for c in range(COLS):
            row.append(patterns[idx])
            idx += 1
        game_map.append(row)
    return game_map

# ========== 连通判断（最多2拐点） ==========
def can_connect(map_data, r1, c1, r2, c2):
    if r1 == r2 and c1 == c2:
        return False
    if map_data[r1][c1] != map_data[r2][c2]:
        return False
    if map_data[r1][c1] == -1:
        return False
    
    if check_straight(map_data, r1, c1, r2, c2):
        return True
    
    if map_data[r1][c2] == -1 and check_straight(map_data, r1, c1, r1, c2) and check_straight(map_data, r1, c2, r2, c2):
        return True
    if map_data[r2][c1] == -1 and check_straight(map_data, r1, c1, r2, c1) and check_straight(map_data, r2, c1, r2, c2):
        return True
    
    for c in range(-1, COLS + 1):
        if c == c1 or c == c2:
            continue
        pass1 = (c < 0 or c >= COLS or map_data[r1][c] == -1)
        pass2 = (c < 0 or c >= COLS or map_data[r2][c] == -1)
        if pass1 and pass2 and check_straight(map_data, r1, c1, r1, c) and check_straight(map_data, r1, c, r2, c) and check_straight(map_data, r2, c, r2, c2):
            return True
    for r in range(-1, ROWS + 1):
        if r == r1 or r == r2:
            continue
        pass1 = (r < 0 or r >= ROWS or map_data[r][c1] == -1)
        pass2 = (r < 0 or r >= ROWS or map_data[r][c2] == -1)
        if pass1 and pass2 and check_straight(map_data, r1, c1, r, c1) and check_straight(map_data, r, c1, r, c2) and check_straight(map_data, r, c2, r2, c2):
            return True
    return False

def check_straight(map_data, r1, c1, r2, c2):
    if r1 == r2:
        min_c, max_c = min(c1, c2), max(c1, c2)
        for c in range(min_c + 1, max_c):
            if 0 <= c < COLS and map_data[r1][c] != -1:
                return False
        return True
    elif c1 == c2:
        min_r, max_r = min(r1, r2), max(r1, r2)
        for r in range(min_r + 1, max_r):
            if 0 <= r < ROWS and map_data[r][c1] != -1:
                return False
        return True
    return False

# ========== 主游戏类 ==========
class LianLianKan:
    def __init__(self, root):
        self.root = root
        self.root.title("会计科目连连看")
        self.game_map = generate_map()
        self.first_select = None
        self.remain = ROWS * COLS
        self.buttons = []
        
        # 创建网格按钮
        for r in range(ROWS):
            row_btns = []
            for c in range(COLS):
                idx = self.game_map[r][c]
                btn = tk.Button(root, text=ACCOUNT_SUBJECTS[idx], bg=BG_COLORS[idx],
                                width=8, height=3, font=("微软雅黑", 10),
                                command=lambda r=r, c=c: self.on_click(r, c))
                btn.place(x=MARGIN + c * CELL_SIZE, y=MARGIN + r * CELL_SIZE,
                         width=CELL_SIZE-2, height=CELL_SIZE-2)
                row_btns.append(btn)
            self.buttons.append(row_btns)
    
    def on_click(self, r, c):
        if self.game_map[r][c] == -1:
            return
        
        if self.first_select is None:
            self.first_select = (r, c)
            self.buttons[r][c].config(relief="sunken", bd=3)
        else:
            r1, c1 = self.first_select
            r2, c2 = r, c
            self.buttons[r1][c1].config(relief="raised", bd=1)
            
            if can_connect(self.game_map, r1, c1, r2, c2):
                # 消除
                self.game_map[r1][c1] = -1
                self.game_map[r2][c2] = -1
                self.buttons[r1][c1].destroy()
                self.buttons[r2][c2].destroy()
                self.remain -= 2
                
                if self.remain == 0:
                    messagebox.showinfo("恭喜", "全部消除，通关成功！")
                    self.root.destroy()
            
            self.first_select = None

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry(f"{COLS*CELL_SIZE + MARGIN*2}x{ROWS*CELL_SIZE + MARGIN*2}")
    game = LianLianKan(root)
    root.mainloop()
