import pygame
import math
import random

pygame.init()
WIDTH, HEIGHT = 900, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("炫彩粒子玫瑰")
clock = pygame.time.Clock()
center_x, center_y = WIDTH // 2, HEIGHT // 2

# 颜色
PINK = (255, 180, 220)
LIGHT_PINK = (255, 220, 240)
PURPLE = (200, 120, 255)
WHITE = (255,255,255)

# 粒子类（拖尾流光粒子、爱心碎片粒子）
class Particle:
    def __init__(self, is_heart=False):
        self.is_heart = is_heart
        # 玫瑰中心发射
        self.x = center_x
        self.y = center_y
        angle = random.random() * math.pi * 2
        speed = random.uniform(1.2, 3.2)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = 255
        self.decay = random.uniform(0.8,1.6)
        self.size = random.uniform(1,4)
        self.color = random.choice([PINK, LIGHT_PINK, PURPLE])
        self.trail = [] # 拖尾轨迹

    def update(self):
        self.trail.append((self.x,self.y))
        if len(self.trail) > 12:
            self.trail.pop(0)
        self.x += self.vx
        self.y += self.vy
        self.life -= self.decay
        # 空气阻力
        self.vx *= 0.98
        self.vy *= 0.98

    def draw(self, surf):
        # 画拖尾
        for i, (px, py) in enumerate(self.trail):
            alpha = int((i / len(self.trail)) * self.life)
            c = (*self.color, alpha)
            s = pygame.Surface((int(self.size),int(self.size)), pygame.SRCALPHA)
            pygame.draw.circle(s, c, (int(self.size/2), int(self.size/2)), self.size*0.5)
            surf.blit(s, (px, py))
        # 画粒子本体
        s = pygame.Surface((int(self.size*2),int(self.size*2)), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, int(self.life)), (int(self.size), int(self.size)), self.size)
        surf.blit(s, (self.x, self.y))

# 生成玫瑰轮廓点（玫瑰极坐标公式）
def rose_points(scale=220):
    pts = []
    for t in range(0, 628, 2):
        theta = t / 100
        r = scale * (0.3 + 0.6 * math.sin(4*theta) * math.cos(5*theta))
        x = center_x + r * math.cos(theta)
        y = center_y - r * math.sin(theta)
        pts.append((x,y))
    return pts

rose_pts = rose_points()
particles = []
angle_rotate = 0

running = True
while running:
    # 半透明黑色遮罩，制造拖尾残影效果（核心！）
    screen.fill((0,0,0))
    bg_surf = pygame.Surface((WIDTH,HEIGHT))
    bg_surf.set_alpha(22)
    bg_surf.fill((0,0,0))
    screen.blit(bg_surf,(0,0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    angle_rotate += 0.008

    # 持续生成粒子
    if random.random() < 0.35:
        particles.append(Particle(is_heart=False))
    if random.random() < 0.06:
        particles.append(Particle(is_heart=True))

    # 更新粒子
    new_particles = []
    for p in particles:
        p.update()
        if p.life > 0:
            new_particles.append(p)
            p.draw(screen)
    particles = new_particles

    # 绘制旋转玫瑰主线轮廓
    rotated_rose = []
    for (x,y) in rose_pts:
        dx = x - center_x
        dy = y - center_y
        nx = dx * math.cos(angle_rotate) - dy * math.sin(angle_rotate)
        ny = dx * math.sin(angle_rotate) + dy * math.cos(angle_rotate)
        rotated_rose.append( (center_x+nx, center_y+ny) )
    pygame.draw.lines(screen, LIGHT_PINK, True, rotated_rose, 2)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
