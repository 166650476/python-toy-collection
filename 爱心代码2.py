import tkinter as tk
import random
import math

# ========== 可调参数 ==========
WIDTH = 600
HEIGHT = 600
CENTER_X = WIDTH // 2
CENTER_Y = HEIGHT // 2
HEART_SIZE = 150      # 爱心整体大小
PARTICLE_NUM = 2800   # 粒子总数，越多越密集
BEAT_SPEED = 0.02     # 心跳速度
BG_COLOR = "black"    # 背景色
HEART_COLOR = "#ff4d6d"  # 粒子颜色

# 判断点是否在爱心内部（爱心隐函数方程）
def point_in_heart(x, y):
    x = x / HEART_SIZE
    y = -y / HEART_SIZE  # 翻转Y轴，让爱心正立
    return (x**2 + y**2 - 1)**3 - x**2 * y**3 < 0

# 生成所有粒子
def create_particles():
    particles = []
    # 1. 生成核心爱心粒子（85%的粒子，填充爱心内部）
    while len(particles) < PARTICLE_NUM * 0.85:
        x = random.uniform(-1.3, 1.3) * HEART_SIZE
        y = random.uniform(-1.3, 1.3) * HEART_SIZE
        if point_in_heart(x, y):
            particles.append({
                "bx": x, "by": y,    # 基础位置
                "shake": random.uniform(0.4, 1.8)  # 抖动幅度
            })
    # 2. 生成外围飘散粒子（15%的粒子，边缘散点效果）
    while len(particles) < PARTICLE_NUM:
        x = random.uniform(-1.7, 1.7) * HEART_SIZE
        y = random.uniform(-1.7, 1.7) * HEART_SIZE
        if not point_in_heart(x, y) and math.hypot(x, y) < 1.7 * HEART_SIZE:
            particles.append({
                "bx": x, "by": y,
                "shake": random.uniform(1.2, 4)
            })
    return particles

# 动画主循环
def animate():
    global scale, scale_dir
    canvas.delete("all")
    
    # 心跳缩放逻辑
    scale += BEAT_SPEED * scale_dir
    if scale >= 1.08 or scale <= 0.94:
        scale_dir *= -1
    
    # 更新并绘制每个粒子
    for p in particles:
        # 粒子随机微抖动
        ox = random.uniform(-p["shake"], p["shake"]) * 0.4
        oy = random.uniform(-p["shake"], p["shake"]) * 0.4
        
        # 计算最终坐标：基础位置 * 心跳缩放 + 抖动偏移
        x = CENTER_X + (p["bx"] + ox) * scale
        y = CENTER_Y + (p["by"] + oy) * scale
        
        # 绘制粒子点
        canvas.create_oval(x-1, y-1, x+1, y+1, fill=HEART_COLOR, outline="")
    
    root.after(30, animate)

# ========== 启动窗口 ==========
root = tk.Tk()
root.title("粒子爱心")
root.resizable(False, False)

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=BG_COLOR)
canvas.pack()

particles = create_particles()
scale = 1.0
scale_dir = 1

animate()
root.mainloop()
