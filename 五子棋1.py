import tkinter as tk
from tkinter import messagebox, Frame, Button, Label
import random

# 音效兼容（Windows 有效，其他系统自动跳过）
try:
    import winsound
    HAS_SOUND = True
except ImportError:
    HAS_SOUND = False


class Gomoku:
    def __init__(self, root):
        self.root = root
        self.root.title("五子棋 - 完整版")
        self.root.resizable(False, False)

        # ========== 棋盘参数 ==========
        self.BOARD_SIZE = 15
        self.CELL = 32
        self.MARGIN = 30
        canvas_size = (self.BOARD_SIZE - 1) * self.CELL + self.MARGIN * 2

        # ========== 顶部控制栏 ==========
        top_bar = Frame(root)
        top_bar.pack(fill="x", padx=10, pady=8)

        self.mode_btn = Button(top_bar, text="切换人机模式", command=self.toggle_mode)
        self.mode_btn.pack(side="left", padx=2)

        self.undo_btn = Button(top_bar, text="悔棋", command=self.undo_move)
        self.undo_btn.pack(side="left", padx=2)

        self.reset_btn = Button(top_bar, text="重新开始", command=self.reset_game)
        self.reset_btn.pack(side="left", padx=2)

        self.time_black = Label(top_bar, text="黑方: 00:00", font=("Arial", 10))
        self.time_black.pack(side="right", padx=8)

        self.time_white = Label(top_bar, text="白方: 00:00", font=("Arial", 10))
        self.time_white.pack(side="right", padx=8)

        # ========== 棋盘 ==========
        self.canvas = tk.Canvas(root, width=canvas_size, height=canvas_size, bg="#deb887")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.drop_piece)

        # 数字颜色、星位
        self.stars = [(3, 3), (3, 11), (7, 7), (11, 3), (11, 11)]

        # 游戏模式：1=双人对战，2=人机对战（玩家黑，AI白）
        self.mode = 1
        self.init_game()
        self.draw_board()
        self.start_timer()

    # 初始化游戏状态
    def init_game(self):
        self.board = [[0] * self.BOARD_SIZE for _ in range(self.BOARD_SIZE)]
        self.current = 1  # 1=黑棋，2=白棋
        self.game_over = False
        self.history = []  # 悔棋记录：(行, 列, 玩家)
        self.black_time = 0
        self.white_time = 0
        self.timer_running = False

    # 绘制棋盘+棋子
    def draw_board(self):
        self.canvas.delete("all")
        # 网格线
        for i in range(self.BOARD_SIZE):
            y = self.MARGIN + i * self.CELL
            self.canvas.create_line(self.MARGIN, y,
                                    self.MARGIN + (self.BOARD_SIZE - 1) * self.CELL, y)
            x = self.MARGIN + i * self.CELL
            self.canvas.create_line(x, self.MARGIN,
                                    x, self.MARGIN + (self.BOARD_SIZE - 1) * self.CELL)
        # 星位
        for r, c in self.stars:
            x = self.MARGIN + c * self.CELL
            y = self.MARGIN + r * self.CELL
            self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="black")
        # 棋子
        for r in range(self.BOARD_SIZE):
            for c in range(self.BOARD_SIZE):
                if self.board[r][c] != 0:
                    self.draw_piece(r, c, self.board[r][c])

    def draw_piece(self, r, c, player):
        x = self.MARGIN + c * self.CELL
        y = self.MARGIN + r * self.CELL
        color = "black" if player == 1 else "white"
        self.canvas.create_oval(x - 12, y - 12, x + 12, y + 12, fill=color, outline="#333")

    # 落子音效
    def play_sound(self):
        if HAS_SOUND:
            winsound.Beep(650, 40)

    # 左键落子
    def drop_piece(self, event):
        if self.game_over:
            return
        # 人机模式下，AI回合禁止点击
        if self.mode == 2 and self.current == 2:
            return

        c = round((event.x - self.MARGIN) / self.CELL)
        r = round((event.y - self.MARGIN) / self.CELL)
        if not (0 <= r < self.BOARD_SIZE and 0 <= c < self.BOARD_SIZE):
            return
        if self.board[r][c] != 0:
            return

        self.do_drop(r, c, self.current)

    # 执行落子
    def do_drop(self, r, c, player):
        self.board[r][c] = player
        self.history.append((r, c, player))
        self.play_sound()
        self.draw_board()

        if self.check_win(r, c, player):
            self.game_over = True
            self.timer_running = False
            winner = "黑棋" if player == 1 else "白棋"
            messagebox.showinfo("游戏结束", f"{winner}获胜！")
            return

        self.current = 2 if self.current == 1 else 1

        # 人机模式：AI 回合
        if self.mode == 2 and self.current == 2 and not self.game_over:
            self.root.after(300, self.ai_move)

    # ========== 人机AI ==========
    def ai_move(self):
        if self.game_over:
            return
        best_score = -1
        best_pos = None

        # 遍历所有空位计算评分
        for r in range(self.BOARD_SIZE):
            for c in range(self.BOARD_SIZE):
                if self.board[r][c] != 0:
                    continue
                # 进攻分 + 防守分
                attack = self.evaluate(r, c, 2)
                defend = self.evaluate(r, c, 1)
                score = attack + defend * 0.9
                if score > best_score:
                    best_score = score
                    best_pos = (r, c)

        if best_pos:
            self.do_drop(best_pos[0], best_pos[1], 2)

    # 位置评分函数
    def evaluate(self, r, c, player):
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        total = 0
        for dr, dc in directions:
            count = 1
            block = 0
            # 正方向
            nr, nc = r + dr, c + dc
            while 0 <= nr < self.BOARD_SIZE and 0 <= nc < self.BOARD_SIZE and self.board[nr][nc] == player:
                count += 1
                nr += dr
                nc += dc
            if not (0 <= nr < self.BOARD_SIZE and 0 <= nc < self.BOARD_SIZE) or self.board[nr][nc] != 0:
                block += 1
            # 反方向
            nr, nc = r - dr, c - dc
            while 0 <= nr < self.BOARD_SIZE and 0 <= nc < self.BOARD_SIZE and self.board[nr][nc] == player:
                count += 1
                nr -= dr
                nc -= dc
            if not (0 <= nr < self.BOARD_SIZE and 0 <= nc < self.BOARD_SIZE) or self.board[nr][nc] != 0:
                block += 1

            # 棋型评分
            if count >= 5:
                total += 100000
            elif count == 4:
                if block == 0:
                    total += 10000
                elif block == 1:
                    total += 1000
            elif count == 3:
                if block == 0:
                    total += 1000
                elif block == 1:
                    total += 100
            elif count == 2:
                if block == 0:
                    total += 100
                elif block == 1:
                    total += 10
        return total

    # ========== 胜负判断 ==========
    def check_win(self, r, c, player):
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            nr, nc = r + dr, c + dc
            while 0 <= nr < self.BOARD_SIZE and 0 <= nc < self.BOARD_SIZE and self.board[nr][nc] == player:
                count += 1
                nr += dr
                nc += dc
            nr, nc = r - dr, c - dc
            while 0 <= nr < self.BOARD_SIZE and 0 <= nc < self.BOARD_SIZE and self.board[nr][nc] == player:
                count += 1
                nr -= dr
                nc -= dc
            if count >= 5:
                return True
        return False

    # ========== 悔棋 ==========
    def undo_move(self):
        if self.game_over or len(self.history) == 0:
            return

        if self.mode == 1:
            # 双人：悔一步
            r, c, p = self.history.pop()
            self.board[r][c] = 0
            self.current = p
        else:
            # 人机：悔两步（玩家+AI），回到玩家回合
            if len(self.history) >= 2:
                for _ in range(2):
                    r, c, p = self.history.pop()
                    self.board[r][c] = 0
                self.current = 1
            else:
                return

        self.draw_board()

    # ========== 计时器 ==========
    def start_timer(self):
        self.timer_running = True
        self.update_timer()

    def update_timer(self):
        if not self.timer_running or self.game_over:
            return
        if self.current == 1:
            self.black_time += 1
        else:
            self.white_time += 1
        self.update_time_label()
        self.root.after(1000, self.update_timer)

    def update_time_label(self):
        def fmt(sec):
            m, s = divmod(sec, 60)
            return f"{m:02d}:{s:02d}"
        self.time_black.config(text=f"黑方: {fmt(self.black_time)}")
        self.time_white.config(text=f"白方: {fmt(self.white_time)}")

    # ========== 模式切换 & 重置 ==========
    def toggle_mode(self):
        self.mode = 2 if self.mode == 1 else 1
        text = "切换双人模式" if self.mode == 2 else "切换人机模式"
        self.mode_btn.config(text=text)
        self.reset_game()

    def reset_game(self):
        self.timer_running = False
        self.init_game()
        self.draw_board()
        self.update_time_label()
        self.start_timer()


if __name__ == "__main__":
    root = tk.Tk()
    game = Gomoku(root)
    root.mainloop()
