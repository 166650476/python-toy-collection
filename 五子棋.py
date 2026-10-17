import tkinter as tk
from tkinter import messagebox

class Gomoku:
    def __init__(self, root):
        self.root = root
        self.root.title("五子棋")
        self.root.resizable(False, False)

        # ========== 棋盘参数 ==========
        self.BOARD_SIZE = 15    # 标准15路棋盘
        self.CELL = 32          # 格子间距
        self.MARGIN = 30        # 棋盘边距

        canvas_size = (self.BOARD_SIZE - 1) * self.CELL + self.MARGIN * 2
        self.canvas = tk.Canvas(root, width=canvas_size, height=canvas_size, bg="#deb887")
        self.canvas.pack()

        # 鼠标左键落子，右键重新开始
        self.canvas.bind("<Button-1>", self.drop_piece)
        self.canvas.bind("<Button-3>", lambda e: self.reset_game())

        self.init_game()
        self.draw_board()

    # 初始化游戏
    def init_game(self):
        # 0=空 1=黑棋 2=白棋
        self.board = [[0]*self.BOARD_SIZE for _ in range(self.BOARD_SIZE)]
        self.current = 1  # 黑棋先行
        self.game_over = False

    # 绘制棋盘
    def draw_board(self):
        self.canvas.delete("all")
        # 画网格线
        for i in range(self.BOARD_SIZE):
            # 横线
            y = self.MARGIN + i * self.CELL
            self.canvas.create_line(self.MARGIN, y, self.MARGIN + (self.BOARD_SIZE-1)*self.CELL, y)
            # 竖线
            x = self.MARGIN + i * self.CELL
            self.canvas.create_line(x, self.MARGIN, x, self.MARGIN + (self.BOARD_SIZE-1)*self.CELL)

        # 画星位（天元+四个角星）
        stars = [(3,3), (3,11), (7,7), (11,3), (11,11)]
        for r, c in stars:
            x = self.MARGIN + c * self.CELL
            y = self.MARGIN + r * self.CELL
            self.canvas.create_oval(x-3, y-3, x+3, y+3, fill="black")

        # 画所有棋子
        for r in range(self.BOARD_SIZE):
            for c in range(self.BOARD_SIZE):
                if self.board[r][c] != 0:
                    self.draw_piece(r, c, self.board[r][c])

    # 绘制单个棋子
    def draw_piece(self, r, c, player):
        x = self.MARGIN + c * self.CELL
        y = self.MARGIN + r * self.CELL
        color = "black" if player == 1 else "white"
        self.canvas.create_oval(x-12, y-12, x+12, y+12, fill=color, outline="#333")

    # 落子
    def drop_piece(self, event):
        if self.game_over:
            return

        # 计算点击位置对应的行列
        c = round((event.x - self.MARGIN) / self.CELL)
        r = round((event.y - self.MARGIN) / self.CELL)

        # 边界判断
        if not (0 <= r < self.BOARD_SIZE and 0 <= c < self.BOARD_SIZE):
            return
        # 已有棋子
        if self.board[r][c] != 0:
            return

        # 落子
        self.board[r][c] = self.current
        self.draw_board()

        # 判断胜负
        if self.check_win(r, c, self.current):
            self.game_over = True
            winner = "黑棋" if self.current == 1 else "白棋"
            messagebox.showinfo("游戏结束", f"{winner}获胜！\n右键点击棋盘重新开始")
            return

        # 切换玩家
        self.current = 2 if self.current == 1 else 1

    # 胜负判断
    def check_win(self, r, c, player):
        # 四个方向：横、竖、左斜、右斜
        directions = [(0,1), (1,0), (1,1), (1,-1)]
        for dr, dc in directions:
            count = 1
            # 正方向数
            nr, nc = r + dr, c + dc
            while 0 <= nr < self.BOARD_SIZE and 0 <= nc < self.BOARD_SIZE and self.board[nr][nc] == player:
                count += 1
                nr += dr
                nc += dc
            # 反方向数
            nr, nc = r - dr, c - dc
            while 0 <= nr < self.BOARD_SIZE and 0 <= nc < self.BOARD_SIZE and self.board[nr][nc] == player:
                count += 1
                nr -= dr
                nc -= dc
            if count >= 5:
                return True
        return False

    # 重置游戏
    def reset_game(self):
        self.init_game()
        self.draw_board()

if __name__ == "__main__":
    root = tk.Tk()
    game = Gomoku(root)
    root.mainloop()
