import tkinter as tk
import random
import math

# =========================
# 基础设置
# =========================
WIDTH = 1000
HEIGHT = 760

root = tk.Tk()
root.title("NEON HEART")
root.resizable(False, False)

canvas = tk.Canvas(
    root,
    width=WIDTH,
    height=HEIGHT,
    bg="#070711",
    highlightthickness=0
)
canvas.pack()

CX = WIDTH // 2
CY = 350

random.seed()

NEON_COLORS = [
    "#ff2d75",
    "#ff4f9a",
    "#b832ff",
    "#743cff",
    "#28d7fe",
    "#62f3ff",
]

DARK_GLOW = [
    "#160c2d",
    "#21103d",
    "#2d124a",
    "#35144e",
]

# =========================
# 背景渐变感色块
# =========================
for _ in range(80):
    x = random.randint(-100, WIDTH + 100)
    y = random.randint(-100, HEIGHT + 100)
    radius = random.randint(50, 170)

    color = random.choice([
        "#0d1026",
        "#100c2b",
        "#160d31",
        "#0b1930",
        "#1a0e2c",
    ])

    canvas.create_oval(
        x - radius,
        y - radius,
        x + radius,
        y + radius,
        fill=color,
        outline=""
    )

# =========================
# 背景细小星尘
# =========================
for _ in range(220):
    x = random.randint(20, WIDTH - 20)
    y = random.randint(20, HEIGHT - 20)
    size = random.choice([1, 1, 1, 2])

    canvas.create_oval(
        x - size,
        y - size,
        x + size,
        y + size,
        fill=random.choice([
            "#30245a",
            "#4d2770",
            "#623578",
            "#25618a",
            "#713457",
        ]),
        outline=""
    )

# =========================
# 爱心方程
# =========================
def heart_function(x, y):
    return (x * x + y * y - 1) ** 3 - x * x * y ** 3


def create_heart_targets(amount):
    targets = []

    while len(targets) < amount:
        x = random.uniform(-1.38, 1.38)
        y = random.uniform(-1.22, 1.35)

        if heart_function(x, y) <= 0:
            # 让边缘粒子更多，形成清晰轮廓
            center_distance = math.sqrt(x * x + y * y)

            if center_distance < 0.45 and random.random() < 0.42:
                continue

            px = CX + x * 245
            py = CY - y * 225

            targets.append((px, py))

    return targets


# =========================
# 粒子
# =========================
class Particle:
    def __init__(self, target_x, target_y):
        self.target_x = target_x
        self.target_y = target_y

        # 从四周飞入爱心
        self.x = random.choice([
            random.uniform(-100, WIDTH + 100),
            random.uniform(-100, WIDTH + 100),
        ])
        self.y = random.choice([
            random.uniform(-100, -20),
            random.uniform(HEIGHT + 20, HEIGHT + 100),
        ])

        self.size = random.choice([1, 1, 1.5, 2, 2])
        self.speed = random.uniform(0.025, 0.075)
        self.phase = random.uniform(0, math.pi * 2)
        self.twinkle = random.uniform(0.04, 0.1)
        self.color = random.choice(NEON_COLORS)

        self.glow_large = canvas.create_oval(
            0, 0, 0, 0,
            fill=random.choice(DARK_GLOW),
            outline=""
        )

        self.glow_small = canvas.create_oval(
            0, 0, 0, 0,
            fill="#37154c",
            outline=""
        )

        self.dot = canvas.create_oval(
            0, 0, 0, 0,
            fill=self.color,
            outline=""
        )

    def update(self, frame, beat):
        scale = 1 + beat * 0.045

        target_x = CX + (self.target_x - CX) * scale
        target_y = CY + (self.target_y - CY) * scale

        self.x += (target_x - self.x) * self.speed
        self.y += (target_y - self.y) * self.speed

        # 粒子漂浮
        drift_x = math.sin(frame * 0.025 + self.phase) * 2.2
        drift_y = math.cos(frame * 0.031 + self.phase) * 2.2

        x = self.x + drift_x
        y = self.y + drift_y

        brightness = (
            math.sin(frame * self.twinkle + self.phase) + 1
        ) / 2

        radius = self.size + brightness * 1.3

        # 外层光晕
        large_radius = radius * 5.5
        canvas.coords(
            self.glow_large,
            x - large_radius,
            y - large_radius,
            x + large_radius,
            y + large_radius
        )

        # 内层光晕
        small_radius = radius * 2.5
        canvas.coords(
            self.glow_small,
            x - small_radius,
            y - small_radius,
            x + small_radius,
            y + small_radius
        )

        # 粒子主体
        canvas.coords(
            self.dot,
            x - radius,
            y - radius,
            x + radius,
            y + radius
        )

        # 偶尔切换颜色，产生流动感
        if random.random() < 0.008:
            self.color = random.choice(NEON_COLORS)
            canvas.itemconfig(self.dot, fill=self.color)


# =========================
# 创建爱心粒子
# =========================
targets = create_heart_targets(1100)
particles = [Particle(x, y) for x, y in targets]

# =========================
# 霓虹装饰线
# =========================
line_color = "#24174d"

for y in range(80, HEIGHT - 70, 32):
    canvas.create_line(
        0, y, WIDTH, y,
        fill=line_color,
        width=1
    )

# =========================
# 标题和界面文字
# =========================
title = canvas.create_text(
    CX,
    635,
    text="NEON HEART",
    fill="#ff4f9a",
    font=("Arial", 28, "bold")
)

subtitle = canvas.create_text(
    CX,
    675,
    text="LOVE.exe  /  ONLINE",
    fill="#58dfff",
    font=("Consolas", 12, "bold")
)

status = canvas.create_text(
    35,
    35,
    anchor="w",
    text="●  SYSTEM ONLINE",
    fill="#58dfff",
    font=("Consolas", 11, "bold")
)

version = canvas.create_text(
    WIDTH - 35,
    35,
    anchor="e",
    text="v2.026",
    fill="#754caa",
    font=("Consolas", 11)
)

# =========================
# 动画
# =========================
frame = 0


def animate():
    global frame

    frame += 1

    # 更自然的心跳节奏
    heartbeat = math.sin(frame * 0.065) ** 18 * 6

    for particle in particles:
        particle.update(frame, heartbeat)

    # 标题呼吸闪烁
    if frame % 8 == 0:
        canvas.itemconfig(
            title,
            fill=random.choice([
                "#ff2d75",
                "#ff4f9a",
                "#ff82ba",
                "#c832ff",
            ])
        )

    # 状态灯闪烁
    if frame % 20 == 0:
        canvas.itemconfig(
            status,
            fill=random.choice([
                "#58dfff",
                "#62f3ff",
                "#b832ff",
            ])
        )

    root.after(25, animate)


animate()
root.mainloop()