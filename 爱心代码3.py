import tkinter as tk
import random
import math

# 窗口设置
WIDTH, HEIGHT = 1200, 720
root = tk.Tk()
root.title("万朵玫瑰散落动画")
canvas = tk.Canvas(root, bg="#05050F", width=WIDTH, height=HEIGHT)
canvas.pack()

# 颜色组（和原版保持一致）
COLORS = [
    "#ff3232", "#ff6464", "#ff9696",        # 红色
    "#ff3296", "#ff64c8", "#ff96fa",        # 粉色
    "#9632ff", "#c864ff", "#fa96ff",        # 紫色
    "#3232ff", "#6464ff", "#9696ff",        # 蓝色
]


class Rose:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-500, -50)
        self.size = random.uniform(0.5, 2.5)
        self.color = random.choice(COLORS)
        self.petal_count = random.randint(5, 8)
        self.angle = 0
        self.rotation_speed = random.uniform(-0.02, 0.02)
        self.fall_speed = random.uniform(0.3, 1.5)
        self.swing_amplitude = random.uniform(0.5, 3)
        self.swing_frequency = random.uniform(0.01, 0.03)
        self.swing_phase = random.uniform(0, 2 * math.pi)
        self.x_offset = 0

    def update(self):
        self.y += self.fall_speed
        self.angle += self.rotation_speed
        self.swing_phase += self.swing_frequency
        self.x_offset = self.swing_amplitude * math.sin(self.swing_phase)
        # 超出屏幕底部重置到顶部
        if self.y > HEIGHT + 100:
            self.reset()

    def reset(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-500, -50)
        self.fall_speed = random.uniform(0.3, 1.5)

    def draw(self, cvs):
        cx = int(self.x + self.x_offset)
        cy = int(self.y)
        # 绘制每一片花瓣（贝塞尔曲线生成多边形点）
        for i in range(self.petal_count):
            angle = self.angle + i * (2 * math.pi / self.petal_count)
            petal_len = 15 * self.size
            # 控制点
            c1x = cx + 0.3 * petal_len * math.cos(angle - 0.3)
            c1y = cy + 0.3 * petal_len * math.sin(angle - 0.3)
            c2x = cx + petal_len * math.cos(angle + 0.3)
            c2y = cy + petal_len * math.sin(angle + 0.3)
            ex = cx + 0.7 * petal_len * math.cos(angle)
            ey = cy + 0.7 * petal_len * math.sin(angle)

            pts = []
            # 第一段贝塞尔
            for t in range(0, 101, 8):
                t = t / 100
                x = (1-t)**2 * cx + 2 * (1-t)*t * c1x + t**2 * c2x
                y = (1-t)**2 * cy + 2 * (1-t)*t * c1y + t**2 * c2y
                pts.append((x, y))
            # 第二段贝塞尔
            for t in range(0, 101, 8):
                t = t / 100
                x = (1-t)**2 * c2x + 2 * (1-t)*t * ex + t**2 * cx
                y = (1-t)**2 * c2y + 2 * (1-t)*t * ey + t**2 * cy
                pts.append((x, y))
            if len(pts) > 2:
                cvs.create_polygon(pts, fill=self.color, outline="")
        # 花蕊黄色小圆
        r = int(3 * self.size)
        cvs.create_oval(cx-r, cy-r, cx+r, cy+r, fill="#f0dc32", outline="")


# ========= 玫瑰数量，电脑卡顿就减小，比如改成 500 =========
rose_count = 500
roses = [Rose() for _ in range(rose_count)]

# FPS相关
import time
last_time = time.time()
frame_count = 0

def loop():
    global last_time, frame_count
    # 半透明黑色遮罩实现拖尾残影
    canvas.delete("trail")
    canvas.create_rectangle(0,0,WIDTH,HEIGHT, fill="#05050F", outline="", tags="trail")

    for rose in roses:
        rose.update()
        rose.draw(canvas)

    # 计算FPS
    frame_count += 1
    now = time.time()
    if now - last_time >= 1.0:
        fps = frame_count
        frame_count = 0
        last_time = now
    else:
        fps = ""

    # 绘制左上角文字：FPS + 玫瑰总数
    canvas.delete("info_text")
    canvas.create_text(15,15, text=f"FPS: {fps} | 玫瑰数量: {len(roses)}", fill="#ffffff", anchor="nw", font=("Arial", 16), tags="info_text")

    canvas.after(16, loop)

loop()
root.mainloop()
