Python 3.14.7 (tags/v3.14.7:823f032, Aug  5 2026, 10:51:32) [MSC v.1944 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
import tkinter as tk
from tkinter import messagebox
import random

# 配置
ROWS = 6
COLS = 8
CELL_SIZE = 60
# 图案列表（数字代表不同图案）
PATTERNS = [1,2,3,4,5,6,7,8]

class LianLianKan:
    def __init__(self, root):
        self.root = root
        self.root.title("Python连连看")
        self.canvas = tk.Canvas(root, width=COLS*CELL_SIZE, height=ROWS*CELL_SIZE, bg="#f0f0f0")
        self.canvas.pack()

        # 二维数组存地图
        self.map = []
        self.selected = None  # 记录选中格子 (row,col)
        self.colors = ["#ff6b6b","#4ecdc4","#ffe66d","#1a535c","#ff9f1c","#2ec4b6","#9b5de5","#f15bb5"]

        self.init_map()
        self.draw_map()
        self.canvas.bind("<Button-1>", self.on_click)

    def init_map(self):
        """初始化棋盘，成对生成图案"""
        total = ROWS * COLS
        pairs = total // 2
        lst = []
        for _ in range(pairs):
            p = random.choice(PATTERNS)
            lst.append(p)
            lst.append(p)
        random.shuffle(lst)
        idx = 0
        for r in range(ROWS):
            row = []
            for c in range(COLS):
                row.append(lst[idx])
                idx +=1
            self.map.append(row)

    def draw_map(self):
        """绘制棋盘"""
        self.canvas.delete("all")
        for r in range(ROWS):
            for c in range(COLS):
                x1 = c * CELL_SIZE
                y1 = r * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                val = self.map[r][c]
                if val != 0:
                    color = self.colors[val-1]
                    self.canvas.create_rectangle(x1,y1,x2,y2,fill=color,outline="white",width=2)
                    self.canvas.create_text((x1+x2)//2,(y1+y2)//2,text=str(val),font=("Arial",20,"bold"),fill="white")
                # 选中高亮
                if self.selected == (r,c):
                    self.canvas.create_rectangle(x1,y1,x2,y2,outline="#00ff00",width=4)

    def is_connect(self, r1,c1, r2,c2):
        """简单连通判断：直线/拐角连通（简化版连连看规则）"""
        if self.map[r1][c1] != self.map[r2][c2]:
            return False
        # 同一行，中间全部为空
        if r1 == r2:
            min_c = min(c1,c2)
            max_c = max(c1,c2)
            for c in range(min_c+1, max_c):
                if self.map[r1][c] !=0:
                    return False
            return True
...         # 同一列
...         if c1 == c2:
...             min_r = min(r1,r2)
...             max_r = max(r1,r2)
...             for r in range(min_r+1, max_r):
...                 if self.map[r][c1] !=0:
...                     return False
...             return True
...         # 一个拐角
...         if self.map[r1][c2]==0 and self.check_line(r1,c1,r1,c2) and self.check_line(r1,c2,r2,c2):
...             return True
...         if self.map[r2][c1]==0 and self.check_line(r2,c2,r2,c1) and self.check_line(r2,c1,r1,c1):
...             return True
...         return False
... 
...     def check_line(self, r1,c1,r2,c2):
...         """检查两点之间直线全部为空"""
...         if r1 == r2:
...             min_c = min(c1,c2)
...             max_c = max(c1,c2)
...             for c in range(min_c+1,max_c):
...                 if self.map[r1][c] !=0:
...                     return False
            return True
        if c1 == c2:
            min_r = min(r1,r2)
            max_r = max(r1,r2)
            for r in range(min_r+1,max_r):
                if self.map[r][c1] !=0:
                    return False
            return True
        return False

    def on_click(self, event):
        """鼠标点击事件"""
        c = event.x // CELL_SIZE
        r = event.y // CELL_SIZE
        if r >= ROWS or c >= COLS or self.map[r][c]==0:
            return

        if self.selected is None:
            self.selected = (r,c)
            self.draw_map()
        else:
            r1,c1 = self.selected
            if (r1,c1) == (r,c):
                self.selected = None
                self.draw_map()
                return
            # 判断是否可以消除
            if self.is_connect(r1,c1, r,c):
                self.map[r1][c1] = 0
                self.map[r][c] = 0
                self.selected = None
                self.draw_map()
                self.check_win()
            else:
                self.selected = (r,c)
                self.draw_map()

    def check_win(self):
        """判断游戏结束"""
        total = 0
        for row in self.map:
            total += sum(row)
        if total == 0:
            messagebox.showinfo("恭喜","游戏通关！")

if __name__ == "__main__":
    root = tk.Tk()
    app = LianLianKan(root)
    root.mainloop()
