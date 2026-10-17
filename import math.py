import math
import time
import os

SIZE = 10
SPEED = 0.12

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

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
            
            for y in range(min_y, max_y + 1):
                xs = [p[0] for p in points if p[1] == y]
                if not xs:
                    print()
                    continue
                left, right = min(xs), max(xs)
                line = ''
                for x in range(min_x, max_x + 1):
                    line += '*' if left <= x <= right else ' '
                print(line.center(80))
            
            scale += step
            if scale >= 1.2 or scale <= 0.8:
                step = -step
            time.sleep(SPEED)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
