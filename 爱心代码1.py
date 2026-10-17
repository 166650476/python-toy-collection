import tkinter as tk
import math
import random

# ========== 可调参数 ==========
WIDTH = 500
HEIGHT = 500
CENTER = (WIDTH // 2, HEIGHT // 2)
BASE_SIZE = 11        # 爱心基础大小
BEAT_STEP = 0.018     # 心跳缩放步长
ROTATE_SPEED = 0.025  # 旋转角速度
PARTICLE_NUM = 70     # 环绕粒子数量
BG_COLOR = "#0a0a0f"  # 深空背景

# 三层爱心颜色（从外到内：虚→半实→实）
HEART_LAYERS = [
    {"color": "#ffb3c1", "scale": 1.12},  # 外层虚化光晕
    {"color": "#ff5c7a", "scale": 1.03},  # 中层半透
    {"color": "#ff1744", "scale": 1.0},   # 内层实体核心
]

# 生成爱心原始坐标点
def get_heart_points(scale):
    points = []
    for angle in range(360):
        t = math.radians(angle)
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)
        points.append((x * scale, -y * scale))
    return points

# 坐标旋转变换
def rotate_points(points, angle):
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    rotated = []
    for x, y in points:
        rx = x * cos_a - y * sin_a
        ry = x * sin_a + y * cos_a
        rotated.append((rx, ry))
    return rotated

# 初始化环绕粒子
def init_particles():
    particles = []
    for _ in range(PARTICLE_NUM):
        particles.append({
            "angle": random.uniform(0, math.pi * 2),
            "radius": random.randint(80, 160),
            "size": random.randint(1, 3),
            "speed": random.uniform(0.8, 1.5),
            "bright": random.choice(["#ff8fa3", "#ffc2d1", "#ffffff"])
        })
    return particles

# 动画主循环
def animate():
    global beat_scale, beat_dir, rotate_angle, particles
    
    canvas.delete("all")
    
    # 1. 心跳缩放逻辑
    beat_scale += beat_step * beat_dir
    if beat_scale >= 1.15 or beat_scale <= 0.9:
        beat_dir *= -1
    
    # 2. 更新旋转角度
    rotate_angle += ROTATE_SPEED
    
    # 3. 绘制三层虚实爱心
    base_heart = get_heart_points(BASE_SIZE * beat_scale)
    rotated_heart = rotate_points(base_heart, rotate_angle)
    
    for layer in HEART_LAYERS:
        draw_pts = []
        layer_scale = layer["scale"]
        for x, y in rotated_heart:
            draw_pts.append(CENTER[0] + x * layer_scale)
            draw_pts.append(CENTER[1] + y * layer_scale)
        canvas.create_polygon(draw_pts, fill=layer["color"], outline="")
    
    # 4. 更新并绘制环绕粒子
    for p in particles:
        p["angle"] += ROTATE_SPEED * p["speed"]
        px = CENTER[0] + math.cos(p["angle"]) * p["radius"] * beat_scale
        py = CENTER[1] + math.sin(p["angle"]) * p["radius"] * beat_scale
        s = p["size"]
        canvas.create_oval(px-s, py-s, px+s, py+s, fill=p["bright"], outline="")
    
    root.after(40, animate)

# ========== 初始化窗口 ==========
root = tk.Tk()
root.title("旋转粒子爱心")
root.resizable(False, False)

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=BG_COLOR)
canvas.pack()

# 初始状态
beat_scale = 1.0
beat_dir = 1
beat_step = BEAT_STEP
rotate_angle = 0
particles = init_particles()

animate()
root.mainloop()
