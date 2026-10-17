import tkinter as tk
import math
import random

# ========== 基础参数 ==========
WIDTH = 700
HEIGHT = 800
CENTER_X = WIDTH // 2
CENTER_Y = HEIGHT // 2 - 50

BG_COLOR = "#05070a"
STEM_COLOR = "#1f6b3a"
LEAF_COLOR = "#2ecc71"
PETAL_DEEP = "#9d0208"
PETAL_MID = "#dc2f02"
PETAL_LIGHT = "#ffba08"


# 单个椭圆花瓣粒子
def petal_point(tx, ty, angle, scale):
    a = 18 * scale
    b = 10 * scale
    x = a * math.cos(angle)
    y = b * math.sin(angle)
    return tx + x, ty + y


# 生成玫瑰花朵粒子
def create_flower_particles(bloom):
    particles = []

    # 1. 花心粒子
    for _ in range(300):
        a = random.uniform(0, 2 * math.pi)
        r = random.uniform(0, 18) * bloom
        x = CENTER_X + r * math.cos(a)
        y = CENTER_Y + r * math.sin(a)
        particles.append({
            "x": x, "y": y,
            "color": PETAL_DEEP,
            "size": random.uniform(1, 1.4),
            "shake": 0.3
        })

    # 2. 内层花瓣
    for i in range(6):
        base_angle = i * math.pi / 3
        for j in range(120):
            angle = base_angle + random.uniform(-0.4, 0.4)
            dist = random.uniform(20, 40) * bloom
            x = CENTER_X + dist * math.cos(angle)
            y = CENTER_Y + dist * math.sin(angle)
            particles.append({
                "x": x, "y": y,
                "color": PETAL_MID,
                "size": random.uniform(1.2, 1.6),
                "shake": 0.5
            })

    # 3. 外层花瓣
    for i in range(8):
        base_angle = i * math.pi / 4 + 0.2
        for j in range(140):
            angle = base_angle + random.uniform(-0.5, 0.5)
            dist = random.uniform(45, 78) * bloom
            x = CENTER_X + dist * math.cos(angle)
            y = CENTER_Y + dist * math.sin(angle)
            particles.append({
                "x": x, "y": y,
                "color": PETAL_LIGHT,
                "size": random.uniform(1.4, 1.8),
                "shake": 0.7
            })

    # 4. 飘散花瓣粒子
    for _ in range(200):
        angle = random.uniform(0, 2 * math.pi)
        r = random.uniform(80, 130) * bloom
        x = CENTER_X + r * math.cos(angle)
        y = CENTER_Y + r * math.sin(angle)
        particles.append({
            "x": x, "y": y,
            "color": random.choice([PETAL_MID, PETAL_LIGHT]),
            "size": random.uniform(1, 1.3),
            "shake": 1.2
        })

    return particles


# 花茎
def create_stem():
    particles = []
    for y in range(CENTER_Y + 60, HEIGHT - 60, 2):
        offset = math.sin((y - CENTER_Y) * 0.04) * 4
        particles.append({
            "x": CENTER_X + offset,
            "y": y,
            "color": STEM_COLOR,
            "size": 2.2,
            "shake": 0.15
        })
        if random.random() < 0.35:
            particles.append({
                "x": CENTER_X + offset + random.uniform(-1.5, 1.5),
                "y": y + random.uniform(-3, 3),
                "color": "#2ea855",
                "size": 1.4,
                "shake": 0.2
            })
    return particles


# 叶子
def create_leaf(x0, y0, angle, scale):
    particles = []
    for i in range(120):
        a = random.uniform(0, 2 * math.pi)
        r = random.uniform(0, 1)
        ex = 16 * scale * r * math.cos(a)
        ey = 9 * scale * r * math.sin(a)
        rx = ex * math.cos(angle) - ey * math.sin(angle)
        ry = ex * math.sin(angle) + ey * math.cos(angle)
        particles.append({
            "x": x0 + rx,
            "y": y0 + ry,
            "color": LEAF_COLOR,
            "size": random.uniform(1.2, 1.6),
            "shake": 0.25
        })
    return particles


# 主动画
def animate():
    global bloom, bloom_dir
    canvas.delete("all")

    # 绽放逻辑
    bloom += 0.006 * bloom_dir
    if bloom >= 1.08 or bloom <= 0.35:
        bloom_dir *= -1

    # 花朵
    flower = create_flower_particles(bloom)
    # 花茎
    stem = create_stem()
    # 叶子
    leaf1 = create_leaf(CENTER_X - 32, CENTER_Y + 110, -0.6, 1.1)
    leaf2 = create_leaf(CENTER_X + 28, CENTER_Y + 170, 2.4, 0.9)

    all_particles = flower + stem + leaf1 + leaf2

    for p in all_particles:
        ox = random.uniform(-p["shake"], p["shake"])
        oy = random.uniform(-p["shake"], p["shake"])
        x = p["x"] + ox
        y = p["y"] + oy
        s = p["size"]
        canvas.create_oval(x - s, y - s, x + s, y + s, fill=p["color"], outline="")

    root.after(35, animate)


# ========== 启动窗口 ==========
root = tk.Tk()
root.title("一枝玫瑰花绽放")
root.resizable(False, False)

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=BG_COLOR)
canvas.pack()

bloom = 0.4
bloom_dir = 1

animate()
root.mainloop()
