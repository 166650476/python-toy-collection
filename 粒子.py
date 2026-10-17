import os
import sys
import colorsys
# ==================== 配置 ====================
RECORD = False                       #True导出False实时
OUTPUT = "galaxy.mp4"
FPS = 60
RECORD_SECONDS = 30
if RECORD:
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    os.environ["SDL_AUDIODRIVER"] = "dummy"
import pygame
import numpy as np
import subprocess
# ==================== 参数 ====================
WIDTH, HEIGHT = 1600, 900
BG = (3, 6, 22)
DISK_FLATTEN = 0.62
rng = np.random.default_rng(20240607)
CAM_MIN, CAM_MAX = 0.85, 1.45
CAM_PERIOD = 60.0
FIXED_DT = 1.0 / FPS
pygame.init()
flags = 0 if RECORD else pygame.RESIZABLE
screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
pygame.display.set_caption("粒子效果特辑一")
clock = pygame.time.Clock()
trail_surf = pygame.Surface((WIDTH, HEIGHT)).convert()
trail_surf.fill(BG)
fade_overlay = pygame.Surface((WIDTH, HEIGHT)).convert()
fade_overlay.fill(BG)
fade_overlay.set_alpha(20)
def make_glow(diameter, color, levels=6, power=2.2):
    c = (diameter - 1) / 2.0
    yy, xx = np.ogrid[:diameter, :diameter]
    dist = np.sqrt((xx - c) ** 2 + (yy - c) ** 2) / c
    falloff = np.clip(1.0 - dist, 0.0, 1.0) ** power
    sprites = []
    for i in range(levels):
        k = (i + 1) / levels
        rgb = np.empty((diameter, diameter, 3), dtype=np.uint8)
        for ch in range(3):
            rgb[..., ch] = np.clip(falloff * color[ch] * k, 0, 255).astype(np.uint8)
        surf = pygame.image.frombuffer(
            rgb.tobytes(), (diameter, diameter), "RGB"
        ).convert()
        sprites.append(surf)
    return sprites, diameter // 2
def make_glow_palette(diameter, hues, levels=6, power=2.2, sat=1.0, val=1.0):
    pack = []
    for h in hues:
        r, g, b = colorsys.hsv_to_rgb(h, sat, val)
        color = (int(r * 255), int(g * 255), int(b * 255))
        sprites, _ = make_glow(diameter, color, levels, power)
        pack.append(sprites)
    return pack, diameter // 2
# ================== 发光 ==================
GLOW_STAR,  OFF_STAR  = make_glow(3,  (200, 225, 255), 4, 3.8)
GLOW_NEB_A, OFF_NEB   = make_glow(11, (95, 55, 170),   5, 3.2)
GLOW_NEB_B, _         = make_glow(11, (55, 105, 195),  5, 3.2)
N_SW_HUES = 24
sw_hues = [i / N_SW_HUES for i in range(N_SW_HUES)]
SW_PACK, OFF_SWIRL = make_glow_palette(
    7, sw_hues, levels=5, power=3.0, sat=0.95)
N_EN_HUES = 12
en_hues = [i / N_EN_HUES for i in range(N_EN_HUES)]
EN_PACK, OFF_ENER = make_glow_palette(
    5, en_hues, levels=5, power=2.8, sat=1.0)
N_CORE_HUES = N_SW_HUES
CORE_SIZE = 180
CORE_LEVELS = 6
CORE_PACK = []
for i in range(N_CORE_HUES):
    h = i / N_CORE_HUES
    r, g, b = colorsys.hsv_to_rgb(h, 0.72, 1.0)
    color = (int(r * 255), int(g * 255), int(b * 255))
    sprites, _ = make_glow(CORE_SIZE, color, CORE_LEVELS, 2.4)
    CORE_PACK.append(sprites)
CORE_SCALES = np.linspace(CAM_MIN, CAM_MAX, 9)
# ==================== 粒子数据 ====================
N_STAR = 8000
star_x     = rng.uniform(0, WIDTH,  N_STAR).astype(np.float32)
star_y     = rng.uniform(0, HEIGHT, N_STAR).astype(np.float32)
star_phase = rng.uniform(0, 2 * np.pi, N_STAR).astype(np.float32)
star_freq  = rng.uniform(0.5, 2.0,     N_STAR).astype(np.float32)
N_NEB = 3200
neb_x     = rng.uniform(0, WIDTH,  N_NEB).astype(np.float32)
neb_y     = rng.uniform(0, HEIGHT, N_NEB).astype(np.float32)
neb_vx    = rng.normal(0, 1.2,      N_NEB).astype(np.float32)
neb_vy    = rng.normal(0, 0.8,      N_NEB).astype(np.float32)
neb_phase = rng.uniform(0, 2 * np.pi, N_NEB).astype(np.float32)
neb_blue  = rng.random(N_NEB) < 0.5
N_SWIRL   = 6500
sw_r      = rng.uniform(70, 560, N_SWIRL).astype(np.float32)
sw_arm    = rng.integers(0, 3, N_SWIRL) * (2 * np.pi / 3)
sw_a      = (sw_r * 0.010 + sw_arm
- rng.normal(0, 0.25, N_SWIRL)).astype(np.float32)
sw_phase  = rng.uniform(0, 2 * np.pi, N_SWIRL).astype(np.float32)
sw_jitter = rng.normal(0, 5.0, N_SWIRL).astype(np.float32)
SW_ROT    = 0.22
r_norm = np.clip((sw_r - 70.0) / (560.0 - 70.0), 0.0, 1.0).astype(np.float32)
# 色相：从内到外流动速度
HUE_RADIAL_SPAN = 1.0        # 半径 0→1 跨几圈色
HUE_FLOW_SPEED  = 0.30       # 色带向外推移的速度
N_ENERGY  = 1600
en_angle  = rng.uniform(0, 2 * np.pi, N_ENERGY).astype(np.float32)
en_r      = rng.uniform(30, 760,      N_ENERGY).astype(np.float32)
en_speed  = rng.uniform(80, 220,      N_ENERGY).astype(np.float32)
EN_RMAX   = 780.0
en_hue_idx = ((en_angle / (2 * np.pi)) * N_EN_HUES).astype(np.int32) % N_EN_HUES
def draw_frame(t, dt):
    global neb_x, neb_y, sw_a, en_r, en_angle, en_speed, en_hue_idx
    cx, cy = WIDTH * 0.5, HEIGHT * 0.5
    cam_t = 0.5 - 0.5 * np.cos(2 * np.pi * t / CAM_PERIOD)
    cam_zoom = CAM_MIN + (CAM_MAX - CAM_MIN) * cam_t
    trail_surf.blit(fade_overlay, (0, 0))
    # ---------- 星空 ----------
    star_zoom = 1.0 + (cam_zoom - 1.0) * 0.35
    b = 0.5 + 0.5 * np.sin(t * star_freq + star_phase)
    lvl = np.minimum((b * len(GLOW_STAR)).astype(np.int32), len(GLOW_STAR) - 1)
    sx = ((star_x - cx) * star_zoom + cx).astype(np.int32)
    sy = ((star_y - cy) * star_zoom + cy).astype(np.int32)
    for px, py, k in zip(sx.tolist(), sy.tolist(), lvl.tolist()):
        trail_surf.blit(GLOW_STAR[k], (px - OFF_STAR, py - OFF_STAR),
                        special_flags=pygame.BLEND_RGB_ADD)
    # ---------- 星云 ----------
    neb_x += neb_vx * dt
    neb_y += neb_vy * dt
    np.mod(neb_x, WIDTH,  out=neb_x)
    np.mod(neb_y, HEIGHT, out=neb_y)
    neb_zoom = 1.0 + (cam_zoom - 1.0) * 0.7
    nb = 0.45 + 0.35 * np.sin(t * 0.9 + neb_phase)
    nb_lvl = np.clip((nb * len(GLOW_NEB_A)).astype(np.int32),
                     0, len(GLOW_NEB_A) - 1)
    sx = ((neb_x - cx) * neb_zoom + cx).astype(np.int32)
    sy = ((neb_y - cy) * neb_zoom + cy).astype(np.int32)
    for px, py, k, is_blue in zip(sx.tolist(), sy.tolist(),
                                  nb_lvl.tolist(), neb_blue.tolist()):
        sprite = GLOW_NEB_B[k] if is_blue else GLOW_NEB_A[k]
        trail_surf.blit(sprite, (px - OFF_NEB, py - OFF_NEB),
                        special_flags=pygame.BLEND_RGB_ADD)
    # ---------- 旋涡星系 ----------
    sw_a += SW_ROT * dt
    r = sw_r + 6.0 * np.sin(t * 1.3 + sw_phase)
    sx_f = cx + r * np.cos(sw_a)
    sy_f = cy + r * np.sin(sw_a) * DISK_FLATTEN + sw_jitter
    sw_hue_float = (r_norm * HUE_RADIAL_SPAN - t * HUE_FLOW_SPEED) % 1.0
    sw_hue_idx = np.clip((sw_hue_float * N_SW_HUES).astype(np.int32),
                         0, N_SW_HUES - 1)
    sb = (0.30 + 0.70 * (1.0 - sw_r / 620.0)) \
         * (0.80 + 0.20 * np.sin(t * 2.0 + sw_phase))
    sw_lvl = np.clip((sb * len(SW_PACK[0])).astype(np.int32),
                     0, len(SW_PACK[0]) - 1)
    sx = ((sx_f - cx) * cam_zoom + cx).astype(np.int32)
    sy = ((sy_f - cy) * cam_zoom + cy).astype(np.int32)
    for px, py, k, hi in zip(sx.tolist(), sy.tolist(),
                             sw_lvl.tolist(), sw_hue_idx.tolist()):
        trail_surf.blit(SW_PACK[hi][k], (px - OFF_SWIRL, py - OFF_SWIRL),
                        special_flags=pygame.BLEND_RGB_ADD)
    # ---------- 喷流 ----------
    en_r += en_speed * dt
    dead = en_r > EN_RMAX
    nd = int(dead.sum())
    if nd:
        en_r[dead]     = rng.uniform(20, 60, nd)
        en_angle[dead] = rng.uniform(0, 2 * np.pi, nd)
        en_speed[dead] = rng.uniform(80, 220, nd)
        en_hue_idx[dead] = ((en_angle[dead] / (2 * np.pi))
                            * N_EN_HUES).astype(np.int32) % N_EN_HUES
    ea = en_angle + t * 0.35
    ex_f = cx + np.cos(ea) * en_r
    ey_f = cy + np.sin(ea) * en_r * DISK_FLATTEN
    ef = 1.0 - en_r / EN_RMAX
    en_lvl = np.clip((ef * len(EN_PACK[0])).astype(np.int32),
                     0, len(EN_PACK[0]) - 1)
    sx = ((ex_f - cx) * cam_zoom + cx).astype(np.int32)
    sy = ((ey_f - cy) * cam_zoom + cy).astype(np.int32)
    for px, py, k, hi in zip(sx.tolist(), sy.tolist(),
                             en_lvl.tolist(), en_hue_idx.tolist()):
        trail_surf.blit(EN_PACK[hi][k], (px - OFF_ENER, py - OFF_ENER),
                        special_flags=pygame.BLEND_RGB_ADD)
    # ---------- 核心光晕 ----------
    core_hue_float = (-t * HUE_FLOW_SPEED) % 1.0
    core_hue_idx = int(core_hue_float * N_CORE_HUES) % N_CORE_HUES
    pulse = 0.5 + 0.5 * np.sin(t * 1.4)
    ck = min(int(pulse * CORE_LEVELS), CORE_LEVELS - 1)
    s_idx = int(np.argmin(np.abs(CORE_SCALES - cam_zoom)))
    s = CORE_SCALES[s_idx]
    base = CORE_PACK[core_hue_idx][ck]
    core_surf = pygame.transform.smoothscale(
        base, (int(CORE_SIZE * s), int(CORE_SIZE * s)))
    cs = core_surf.get_width() // 2
    trail_surf.blit(core_surf, (int(cx) - cs, int(cy) - cs),
                    special_flags=pygame.BLEND_RGB_ADD)
    screen.blit(trail_surf, (0, 0))
def surface_to_bytes(surf):
    if hasattr(pygame.image, "tobytes"):
        return pygame.image.tobytes(surf, "RGB")
    return pygame.image.tostring(surf, "RGB")
def run_preview():
    running = True
    t = 0.0
    while running:
        dt = min(clock.tick(60) / 1000.0, 0.05)
        t += dt
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                running = False
        draw_frame(t, dt)
        pygame.display.flip()
    pygame.quit()
def run_record():
    try:
        subprocess.run(["ffmpeg", "-version"],
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL,
                       check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("错误：未检测到 ffmpeg，请先安装并加入 PATH")
        pygame.quit()
        sys.exit(1)
    total_frames = int(RECORD_SECONDS * FPS)
    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-pix_fmt", "rgb24",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-r", str(FPS),
        "-i", "-",
        "-an",
        "-vcodec", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "18",
        "-preset", "medium",
        OUTPUT,
    ]
    print(f"开始录制：{WIDTH}x{HEIGHT} @ {FPS}fps，共 {total_frames} 帧")
    print(f"输出文件：{OUTPUT}")
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(total_frames):
        t = i * FIXED_DT
        draw_frame(t, FIXED_DT)
        proc.stdin.write(surface_to_bytes(screen))
        if i % FPS == 0 or i == total_frames - 1:
            pct = (i + 1) / total_frames * 100
            print(f"  进度 {i+1}/{total_frames} 帧 ({pct:.1f}%)  时间 {t:.1f}s")
    proc.stdin.close()
    proc.wait()
    pygame.quit()
    print(f"✓ 完成：{OUTPUT}")
if _name_ == "_main_":
    if RECORD:
        run_record()
    else:
        run_preview()


