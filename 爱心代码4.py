import random
from math import sin, cos, pi, log
from tkinter import *

# ========== 基础配置 ==========
CANVAS_WIDTH = 840
CANVAS_HEIGHT = 680
CANVAS_CENTER_X = CANVAS_WIDTH / 2
CANVAS_CENTER_Y = CANVAS_HEIGHT / 2
IMAGE_ENLARGE = 11
HEART_COLOR = "#e86184"


# ========== 工具函数 ==========
def heart_function(t, shrink_ratio: float = IMAGE_ENLARGE):
    """爱心标准参数方程，生成轮廓坐标"""
    x = 17 * (sin(t) ** 3)
    y = -(16 * cos(t) - 5 * cos(2 * t) - 2 * cos(3 * t) - cos(3 * t))
    x *= IMAGE_ENLARGE
    y *= IMAGE_ENLARGE
    x += CANVAS_CENTER_X
    y += CANVAS_CENTER_Y
    return int(x), int(y)


def scatter_inside(x, y, beta=0.15):
    """粒子向内扩散，填充爱心内部"""
    ratio_x = - beta * log(random.random())
    ratio_y = - beta * log(random.random())
    dx = ratio_x * (x - CANVAS_CENTER_X)
    dy = ratio_y * (y - CANVAS_CENTER_Y)
    return x - dx, y - dy


def shrink(x, y, ratio):
    """粒子收缩力计算"""
    force = -1 / (((x - CANVAS_CENTER_X) ** 2 + (y - CANVAS_CENTER_Y) ** 2) ** 0.6)
    dx = ratio * force * (x - CANVAS_CENTER_X)
    dy = ratio * force * (y - CANVAS_CENTER_Y)
    return x - dx, y - dy


def curve(p):
    """跳动曲线函数，控制心跳节奏"""
    return 2 * (2 * sin(4 * p)) / (2 * pi)


# ========== 爱心核心类 ==========
class Heart:
    def __init__(self, generate_frame=20):
        self._points = set()                  # 爱心轮廓点
        self._edge_diffusion_points = set()   # 边缘扩散粒子
        self._center_diffusion_points = set() # 中心填充粒子
        self.all_points = {}                  # 每帧所有粒子缓存
        self.build(2000)
        self.random_halo = 1000               # 随机光晕粒子数
        self.generate_frame = generate_frame  # 动画总帧数
        # 预计算所有帧的粒子位置
        for frame in range(generate_frame):
            self.calc(frame)

    def build(self, number):
        """生成三层粒子：轮廓+边缘扩散+中心填充"""
        # 1. 生成爱心轮廓点
        for _ in range(number):
            t = random.uniform(0, 2 * pi)
            x, y = heart_function(t)
            self._points.add((x, y))
        # 2. 边缘扩散粒子
        for _x, _y in list(self._points):
            for _ in range(3):
                x, y = scatter_inside(_x, _y, beta=0.05)
                self._edge_diffusion_points.add((x, y))
        # 3. 中心填充粒子
        point_list = list(self._points)
        for _ in range(10000):
            x, y = random.choice(point_list)
            x, y = scatter_inside(x, y, beta=0.27)
            self._center_diffusion_points.add((x, y))

    @staticmethod
    def calc_position(x, y, ratio):
        """计算每帧粒子偏移位置，实现跳动效果"""
        force = 1 / (((x - CANVAS_CENTER_X) ** 2 + (y - CANVAS_CENTER_Y) ** 2) ** 0.420)
        dx = ratio * force * (x - CANVAS_CENTER_X) + random.randint(-1, 1)
        dy = ratio * force * (y - CANVAS_CENTER_Y) + random.randint(-1, 1)
        return x - dx, y - dy

    def calc(self, frame):
        """计算单帧所有粒子坐标"""
        ratio = 10 * curve(frame / 10 * pi)
        all_points = []

        # 随机光晕粒子
        for _ in range(self.random_halo):
            x, y = random.choice(list(self._points))
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 2)
            all_points.append((x, y, size))
        # 轮廓粒子
        for x, y in self._points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 3)
            all_points.append((x, y, size))
        # 边缘扩散粒子
        for x, y in self._edge_diffusion_points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 2)
            all_points.append((x, y, size))
        # 中心填充粒子
        for x, y in self._center_diffusion_points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 2)
            all_points.append((x, y, size))

        self.all_points[frame] = all_points

    def render(self, render_canvas, render_frame):
        """渲染单帧画面"""
        for x, y, size in self.all_points[render_frame % self.generate_frame]:
            render_canvas.create_rectangle(x, y, x + size, y + size, width=0, fill=HEART_COLOR)


# ========== 动画主循环 ==========
def draw(main: Tk, render_canvas: Canvas, render_heart: Heart, render_frame=0):
    render_canvas.delete('all')
    render_heart.render(render_canvas, render_frame)
    main.after(1, draw, main, render_canvas, render_heart, render_frame + 1)


if __name__ == '__main__':
    root = Tk()
    root.title("李峋同款爱心")
    canvas = Canvas(root, bg='black', height=CANVAS_HEIGHT, width=CANVAS_WIDTH)
    canvas.pack()
    heart = Heart()
    draw(root, canvas, heart)
    root.mainloop()
