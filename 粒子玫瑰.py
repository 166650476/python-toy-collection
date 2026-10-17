import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# 玫瑰线参数方程（k为花瓣数）
def rose_curve(t, k=5):
    r = np.sin(k * t)
    return r * np.cos(t), r * np.sin(t)

# 初始化粒子
num_particles = 800
particles = np.zeros((num_particles, 4))  # x,y,vx,vy
particles[:, :2] = np.random.uniform(-0.1, 0.1, (num_particles, 2))
particles[:, 2:] = np.random.uniform(-0.02, 0.02, (num_particles, 2))
lifetimes = np.random.randint(50, 150, num_particles)

# 创建画布
fig, ax = plt.subplots(figsize=(8, 8), facecolor='black')
ax.set_xlim(-1.2, 1.2)
ax.set_ylim(-1.2, 1.2)
ax.axis('off')
scat = ax.scatter(particles[:,0], particles[:,1], c='pink', s=15, alpha=0.6)

# 动画更新
def update(frame):
    global particles, lifetimes
    # 吸附到玫瑰线
    t = np.random.uniform(0, 2*np.pi, num_particles)
    target_x, target_y = rose_curve(t)
    particles[:,0] += (target_x - particles[:,0]) * 0.1
    particles[:,1] += (target_y - particles[:,1]) * 0.1
    # 更新生命周期
    lifetimes -= 1
    dead = lifetimes <= 0
    particles[dead, :2] = np.random.uniform(-0.1, 0.1, (np.sum(dead), 2))
    lifetimes[dead] = np.random.randint(50, 150, np.sum(dead))
    # 渲染
    scat.set_offsets(particles[:,:2])
    scat.set_alpha(np.clip(lifetimes/100, 0.1, 0.8))
    return scat,

ani = FuncAnimation(fig, update, frames=200, interval=30, blit=True)
plt.show()