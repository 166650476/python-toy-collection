import tkinter as tk
import random

# ========== 游戏参数 ==========
CELL = 20          # 每个格子像素大小
WIDTH = 600        # 窗口宽度
HEIGHT = 400       # 窗口高度
SPEED = 150        # 移动速度（毫秒，数值越小越快）

class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("贪吃蛇")
        self.root.resizable(False, False)

        # 游戏画布
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#1e1e1e")
        self.canvas.pack()

        # 绑定按键
        self.root.bind("<Up>", lambda e: self.set_dir(0, -1))
        self.root.bind("<Down>", lambda e: self.set_dir(0, 1))
        self.root.bind("<Left>", lambda e: self.set_dir(-1, 0))
        self.root.bind("<Right>", lambda e: self.set_dir(1, 0))
        self.root.bind("<space>", lambda e: self.toggle_pause())
        self.root.bind("r", lambda e: self.reset())

        self.reset()
        self.loop()

    # 重置游戏
    def reset(self):
        # 蛇身坐标列表，第一个为蛇头
        self.snake = [(100, 200), (80, 200), (60, 200)]
        self.dx, self.dy = 1, 0  # 初始方向向右
        self.food = self.new_food()
        self.score = 0
        self.over = False
        self.pause = False

    # 生成食物
    def new_food(self):
        while True:
            x = random.randrange(0, WIDTH, CELL)
            y = random.randrange(0, HEIGHT, CELL)
            if (x, y) not in self.snake:
                return (x, y)

    # 改变方向（禁止180°掉头）
    def set_dir(self, x, y):
        if self.dx + x != 0 or self.dy + y != 0:
            self.dx, self.dy = x, y

    # 暂停/继续
    def toggle_pause(self):
        if not self.over:
            self.pause = not self.pause

    # 游戏主循环
    def loop(self):
        if self.over:
            self.canvas.delete("all")
            self.canvas.create_text(WIDTH//2, HEIGHT//2 - 20,
                                    text=f"游戏结束  得分：{self.score}",
                                    fill="#ff4757", font=("微软雅黑", 22, "bold"))
            self.canvas.create_text(WIDTH//2, HEIGHT//2 + 20,
                                    text="按 R 重新开始",
                                    fill="#aaa", font=("微软雅黑", 14))
            return

        if self.pause:
            self.canvas.create_text(WIDTH//2, HEIGHT//2,
                                    text="已暂停，按空格继续",
                                    fill="white", font=("微软雅黑", 16))
            self.root.after(SPEED, self.loop)
            return

        self.canvas.delete("all")

        # 画蛇
        for i, (x, y) in enumerate(self.snake):
            color = "#2ed573" if i == 0 else "#7bed9f"
            self.canvas.create_rectangle(x, y, x+CELL, y+CELL, fill=color, outline="")

        # 画食物
        fx, fy = self.food
        self.canvas.create_oval(fx, fy, fx+CELL, fy+CELL, fill="#ff4757", outline="")

        # 画分数
        self.canvas.create_text(50, 20, text=f"得分：{self.score}",
                                fill="white", font=("微软雅黑", 12))

        # 计算新蛇头
        hx, hy = self.snake[0]
        new_head = (hx + self.dx * CELL, hy + self.dy * CELL)

        # 撞墙检测
        if (new_head[0] < 0 or new_head[0] >= WIDTH or
            new_head[1] < 0 or new_head[1] >= HEIGHT):
            self.over = True

        # 撞自己检测
        if new_head in self.snake:
            self.over = True

        # 移动蛇
        self.snake.insert(0, new_head)

        # 吃到食物
        if new_head == self.food:
            self.score += 10
            self.food = self.new_food()
        else:
            self.snake.pop()  # 没吃到则去掉尾巴

        self.root.after(SPEED, self.loop)

if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()
