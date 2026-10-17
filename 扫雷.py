import tkinter as tk
from tkinter import messagebox
import random

class Minesweeper:
    def __init__(self, root):
        self.root = root
        self.root.title("扫雷")
        self.root.resizable(False, False)

        # ========== 难度参数 ==========
        self.ROWS = 10       # 行数
        self.COLS = 10       # 列数
        self.MINES = 15      # 地雷数量
        self.CELL = 32       # 格子像素大小

        self.width = self.COLS * self.CELL
        self.height = self.ROWS * self.CELL
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg="#f0f0f0")
        self.canvas.pack()

        # 绑定鼠标事件
        self.canvas.bind("<Button-1>", self.left_click)   # 左键翻开
        self.canvas.bind("<Button-3>", self.right_click)  # 右键插旗

        # 数字颜色（经典扫雷配色）
        self.num_colors = {
            1: "#0000ff", 2: "#008000", 3: "#ff0000",
            4: "#000080", 5: "#800000", 6: "#008080",
            7: "#000000", 8: "#808080"
        }

        self.init_game()
        self.draw_board()

    # 初始化游戏
    def init_game(self):
        # board: -1=地雷，0-8=周围地雷数
        self.board = [[0]*self.COLS for _ in range(self.ROWS)]
        self.revealed = [[False]*self.COLS for _ in range(self.ROWS)]  # 是否已翻开
        self.flagged = [[False]*self.COLS for _ in range(self.ROWS)]   # 是否已插旗
        self.first_click = True   # 首次点击标记（保证不踩雷）
        self.game_over = False
        self.flag_count = 0

    # 生成地雷（排除首次点击位置）
    def generate_mines(self, exclude_r, exclude_c):
        count = 0
        while count < self.MINES:
            r = random.randint(0, self.ROWS-1)
            c = random.randint(0, self.COLS-1)
            if self.board[r][c] != -1 and (r, c) != (exclude_r, exclude_c):
                self.board[r][c] = -1
                count += 1
        # 计算每个格子周围的地雷数
        for r in range(self.ROWS):
            for c in range(self.COLS):
                if self.board[r][c] == -1:
                    continue
                n = 0
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = r+dr, c+dc
                        if 0 <= nr < self.ROWS and 0 <= nc < self.COLS:
                            if self.board[nr][nc] == -1:
                                n += 1
                self.board[r][c] = n

    # 绘制棋盘
    def draw_board(self):
        self.canvas.delete("all")
        for r in range(self.ROWS):
            for c in range(self.COLS):
                x1, y1 = c * self.CELL, r * self.CELL
                x2, y2 = x1 + self.CELL, y1 + self.CELL

                if self.revealed[r][c]:
                    # 已翻开格子
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#d9d9d9", outline="#ffffff")
                    val = self.board[r][c]
                    if val == -1:
                        # 绘制地雷
                        self.canvas.create_oval(x1+6, y1+6, x2-6, y2-6, fill="#222222")
                    elif val > 0:
                        self.canvas.create_text(
                            (x1+x2)//2, (y1+y2)//2,
                            text=str(val), fill=self.num_colors[val],
                            font=("Arial", 12, "bold")
                        )
                else:
                    # 未翻开格子
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#c0c0c0", outline="#ffffff")
                    if self.flagged[r][c]:
                        # 绘制小红旗
                        self.canvas.create_polygon(
                            x1+8, y1+6, x1+8, y1+22, x1+22, y1+14,
                            fill="#ff2b2b", outline=""
                        )

    # 左键点击
    def left_click(self, event):
        if self.game_over:
            return
        c = event.x // self.CELL
        r = event.y // self.CELL
        if not (0 <= r < self.ROWS and 0 <= c < self.COLS):
            return
        if self.revealed[r][c] or self.flagged[r][c]:
            return

        # 首次点击生成地雷，保证不踩雷
        if self.first_click:
            self.generate_mines(r, c)
            self.first_click = False

        self.reveal_cell(r, c)
        self.draw_board()
        self.check_win()

    # 翻开格子（递归扩散空白）
    def reveal_cell(self, r, c):
        if self.revealed[r][c] or self.flagged[r][c]:
            return
        self.revealed[r][c] = True

        # 踩到地雷
        if self.board[r][c] == -1:
            self.end_game(False)
            return

        # 空白格子：自动翻开周围8格
        if self.board[r][c] == 0:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < self.ROWS and 0 <= nc < self.COLS:
                        self.reveal_cell(nr, nc)

    # 右键插旗
    def right_click(self, event):
        if self.game_over:
            return
        c = event.x // self.CELL
        r = event.y // self.CELL
        if not (0 <= r < self.ROWS and 0 <= c < self.COLS):
            return
        if self.revealed[r][c]:
            return

        self.flagged[r][c] = not self.flagged[r][c]
        self.flag_count += 1 if self.flagged[r][c] else -1
        self.draw_board()

    # 游戏结束
    def end_game(self, win):
        self.game_over = True
        # 显示所有地雷
        for r in range(self.ROWS):
            for c in range(self.COLS):
                if self.board[r][c] == -1:
                    self.revealed[r][c] = True
        self.draw_board()

        if win:
            messagebox.showinfo("胜利", "恭喜你，排雷成功！")
        else:
            messagebox.showinfo("游戏结束", "很遗憾，踩到地雷了！")

    # 检查是否胜利
    def check_win(self):
        for r in range(self.ROWS):
            for c in range(self.COLS):
                # 存在未翻开的非雷格子则未胜利
                if self.board[r][c] != -1 and not self.revealed[r][c]:
                    return
        self.end_game(True)

if __name__ == "__main__":
    root = tk.Tk()
    game = Minesweeper(root)
    root.mainloop()
