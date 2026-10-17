import math
import time
import os
import sys

# ========== 参数设置 ==========
HEART_CHAR = '♥'
SIZE = 10
SPEED = 0.12
BG_CHAR = ' '

# 强制控制台UTF-8编码 + 启用Windows ANSI彩色支持
if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    os.system('')

# 清屏兼容
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# 生成爱心坐标
def get_heart_points(scale):
    points = set()
    for angle in range(360):
        t = math.radians(angle)
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)
        px = int(x * scale * 0.5)
        py = int(-y * scale)
        points.add((px, py))
    return points

def main():
    scale = 0.8
    step = 0.05
    
    try:
        while True:
            clear_screen()
            points = get_heart_points(scale * SIZE)
            
            min_x = min(p[0] for p in points)
            max_x = max(p[0] for p in points)
            min_y = min(p[1] for p in points)
            max_y = max(p[1] for p in points)
            
            output = []
            for y in range(min_y, max_y + 1):
                xs = [p[0] for p in points if p[1] == y]
                if not xs:
                    output.append('')
                    continue
                left, right = min(xs), max(xs)
                line = ''
                for x in range(min_x, max_x + 1):
                    line += HEART_CHAR if left <= x <= right else BG_CHAR
                output.append(line)
            
            heart_str = '\n'.join(output)
            # 先居中再加颜色（避免转义符破坏居中计算）
            centered = heart_str.center(80)
            print(f'\033[91m{centered}\033[0m')
            
            scale += step
            if scale >= 1.2 or scale <= 0.8:
                step = -step
            
            time.sleep(SPEED)
    
    except KeyboardInterrupt:
        clear_screen()
        print("\n动画结束".center(80))

if __name__ == "__main__":
    main()
