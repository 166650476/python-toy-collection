import tkinter as tk
import math
import random

WIDTH = 600
HEIGHT = 600
CENTER_X = WIDTH // 2
CENTER_Y = HEIGHT // 2
ROSE_SIZE = 220
PARTICLE_NUM = 4200
BEAT_SPEED = 0.04
BG_COLOR = "black"

COLOR_CORE = "#880e2f"
COLOR_MID = "#d81b60"
COLOR_EDGE = "#ff80ab"


def rose_point(theta, size):
    r = size * math.cos(4 * theta)
    return r * math.cos(theta), r * math.sin(theta)


def point_in_rose(x, y):
    dx = x / ROSE_SIZE
    dy = y / ROSE_SIZE
    return (dx**2 + dy**2 - 1)**3 - dx**2 * dy**3 < 0


def rose_outline(scale):
    points = []
    for i in range(360):
        theta = math.radians(i)
        points.append(rose_point(theta, ROSE_SIZE * scale))
    return points


def create_particles():
    particles = []

    while len(particles) < PARTICLE_NUM * 0.7:
        x = random.uniform(-1.1, 1.1) * ROSE_SIZE
        y = random.uniform(-1.1, 1.1) * ROSE_SIZE
        if point_in_rose(x, y):
            dist = math.hypot(x, y)
            color = COLOR_CORE if dist < 0.4 * ROSE_SIZE else COLOR_MID
            particles.append({
                "bx": x, "by": y, "color": color,
                "shake": random.uniform(0.2, 1.0), "size": 1
            })

    outline = rose_outline(1.0)
    for _ in range(int(PARTICLE_NUM * 0.2)):
        idx = random.randint(0, len(outline) - 1)
        ox, oy = outline[idx]
        particles.append({
            "bx": ox + random.uniform(-1.5, 1.5),
            "by": oy + random.uniform(-1.5, 1.5),
            "color": COLOR_EDGE,
            "shake": random.uniform(0.4, 1.2), "size": 1.2
        })

    while len(particles) < PARTICLE_NUM:
        angle = random.uniform(0, 2 * math.pi)
        r = random.uniform(1.0, 1.25) * ROSE_SIZE
        particles.append({
            "bx": r * math.cos(angle), "by": r * math.sin(angle),
            "color": COLOR_EDGE,
            "shake": random.uniform(1.0, 2.5), "size": 1
        })

    return particles


def animate():
    global scale, scale_dir
    canvas.delete("all")

    scale += BEAT_SPEED * scale_dir
    if scale >= 1.1 or scale <= 0.92:
        scale_dir *= -1

    base_pts = []
    for x, y in rose_outline(scale):
        base_pts.append(CENTER_X + x)
        base_pts.append(CENTER_Y + y)
    canvas.create_polygon(base_pts, fill="#2a0510", outline="")

    for p in particles:
        ox = random.uniform(-p["shake"], p["shake"]) * 0.3
        oy = random.uniform(-p["shake"], p["shake"]) * 0.3
        x = CENTER_X + (p["bx"] + ox) * scale
        y = CENTER_Y + (p["by"] + oy) * scale
        s = p["size"]
        canvas.create_oval(x - s, y - s, x + s, y + s, fill=p["color"], outline="")

    root.after(30, animate)


root = tk.Tk()
root.title("红色粒子玫瑰")
root.resizable(False, False)
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=BG_COLOR)
canvas.pack()

particles = create_particles()
scale = 1.0
scale_dir = 1
animate()
root.mainloop()
