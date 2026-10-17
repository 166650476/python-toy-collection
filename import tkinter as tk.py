import tkinter as tk
import random

# 游戏基础设置
CELL_SIZE = 20
GAME_WIDTH = 400
GAME_HEIGHT = 400
SPEED = 120  # 数值越小速度越快

class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("贪吃蛇")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=GAME_WIDTH, height=GAME_HEIGHT, bg="#1a1a1a")
        self.canvas.pack()

        # 绑定方向键
        self.root.bind("<Up>", lambda e: self.change_dir(0, -1))
        self.root.bind("<Down>", lambda e: self.change_dir(0, 1))
        self.root.bind("<Left>", lambda e: self.change_dir(-1, 0))
        self.root.bind("<Right>", lambda e: self.change_dir(1, 0))

        self.reset_game()
        self.game_loop()

    def reset_game(self):
        # 蛇初始化：列表保存坐标，第一个是蛇头
        self.snake = [(100,100), (80,100), (60,100)]
        self.dir_x = 1
        self.dir_y = 0
        self.food = self.create_food()
        self.score = 0
        self.gameover = False

    def create_food(self):
        # 随机生成食物坐标，不能生成在蛇身上
        while True:
            x = random.randrange(0, GAME_WIDTH, CELL_SIZE)
            y = random.randrange(0, GAME_HEIGHT, CELL_SIZE)
            if (x,y) not in self.snake:
                return (x,y)

    def change_dir(self, dx, dy):
        # 禁止直接180度掉头（向右不能直接向左）
        if self.dir_x + dx != 0 or self.dir_y + dy !=0:
            self.dir_x = dx
            self.dir_y = dy

    def game_loop(self):
        if self.gameover:
            self.canvas.delete("all")
            self.canvas.create_text(GAME_WIDTH//2, GAME_HEIGHT//2,
                                    text=f"游戏结束！得分:{self.score}",
                                    fill="red", font=("Arial",20))
            return

        self.canvas.delete("all")
        # 画蛇
        for index, (x,y) in enumerate(self.snake):
            color = "#4cd964" if index ==0 else "#34c759"
            self.canvas.create_rectangle(x,y, x+CELL_SIZE,y+CELL_SIZE, fill=color)
        # 画食物
        fx, fy = self.food
        self.canvas.create_oval(fx, fy, fx+CELL_SIZE, fy+CELL_SIZE, fill="#ff3b30")
        # 绘制分数
        self.canvas.create_text(40,15, text=f"分数：{self.score}", fill="white", font=("Arial",12))

        # 新蛇头
        head_x, head_y = self.snake[0]
        new_head = (head_x + self.dir_x*CELL_SIZE, head_y + self.dir_y*CELL_SIZE)

        # 撞墙判断
        if new_head[0]<0 or new_head[0]>=GAME_WIDTH or new_head[1]<0 or new_head[1]>=GAME_HEIGHT:
            self.gameover = True
        # 撞到自己
        if new_head in self.snake:
            self.gameover = True

        # 添加蛇头
        self.snake.insert(0, new_head)

        # 判断吃到食物
        if new_head == self.food:
            self.score +=10
            self.food = self.create_food()
        else:
            self.snake.pop() # 没吃到食物，删掉尾巴

        self.root.after(SPEED, self.game_loop)

if __name__ == "__main__":
    window = tk.Tk()
    game = SnakeGame(window)
    window.mainloop()
