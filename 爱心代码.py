import tkinter as tk
import math

# ========== 可调整参数 ==========
HEART_SIZE = 12      # 爱心整体大小
BEAT_SPEED = 40      # 跳动速度（毫秒，数值越小跳得越快）
HEART_COLOR = "#ff4d6d"  # 爱心颜色
BG_COLOR = "black"   # 背景颜色

# 计算爱心曲线上的点（经典爱心参数方程）
def heart_points(scale):
    points = []
    for angle in range(360):
        t = math.radians(angle)
        # 爱心参数方程
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)
        # 缩放 + 翻转Y轴
        points.append((x * scale, -y * scale))
    return points

# 动画主逻辑
def animate():
    global scale, step
    canvas.delete("all")
    
    # 生成爱心坐标并居中
    pts = heart_points(scale * HEART_SIZE)
    draw_pts = []
    for x, y in pts:
        draw_pts.append(250 + x)
        draw_pts.append(250 + y)
    
    # 绘制爱心
    canvas.create_polygon(draw_pts, fill=HEART_COLOR, outline=HEART_COLOR)
    canvas.create_text(250, 250, text="张义丰", fill="white", font=("微软雅黑", 16, "bold"))

    
    # 心跳缩放逻辑：放大到峰值后缩小，循环往复
    scale += step
    if scale >= 1.15 or scale <= 0.9:
        step = -step
    
    root.after(BEAT_SPEED, animate)

# ========== 初始化窗口 ==========
root = tk.Tk()
root.title("动态爱心")
root.resizable(False, False)

canvas = tk.Canvas(root, width=500, height=500, bg=BG_COLOR)
canvas.pack()

scale = 1.0   # 初始缩放比例
step = 0.02   # 每帧缩放步长

animate()
root.mainloop()
