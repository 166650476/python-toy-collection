import random

# 麻将牌：万子 1~9，每种4张
def build_tiles():
    tiles = []
    for num in range(1,10):
        for _ in range(4):
            tiles.append(num)
    random.shuffle(tiles)
    return tiles

# 判断是否可以组成顺子
def is_shunzi(a,b,c):
    lst = sorted([a,b,c])
    return lst[0]+1 == lst[1] and lst[1]+1 == lst[2]

# 递归判断胡牌核心：13张牌，去掉一对将，剩下全部组成顺子/刻子
def check_hu(hand):
    hand = sorted(hand)
    # 尝试每一张当将牌（一对）
    for i in range(len(hand)):
        if i+1 < len(hand) and hand[i]==hand[i+1]:
            new_hand = hand.copy()
            # 移除这一对将
            del new_hand[i+1]
            del new_hand[i]
            if dfs(new_hand):
                return True
    return False

def dfs(tiles):
    if len(tiles)==0:
        return True
    first = tiles[0]
    # 优先判断刻子（三张一样）
    if tiles.count(first)>=3:
        new_t = tiles.copy()
        new_t.remove(first)
        new_t.remove(first)
        new_t.remove(first)
        if dfs(new_t):
            return True
    # 判断顺子
    if (first+1) in tiles and (first+2) in tiles:
        new_t = tiles.copy()
        new_t.remove(first)
        new_t.remove(first+1)
        new_t.remove(first+2)
        if dfs(new_t):
            return True
    return False

# 游戏主逻辑
def main():
    print("====简易麻将（万子）====")
    tile_pool = build_tiles()
    player_hand = []
    # 发13张手牌
    for _ in range(13):
        player_hand.append(tile_pool.pop())
    player_hand.sort()
    print(f"你的初始手牌：{player_hand}")

    while True:
        if check_hu(player_hand):
            print("🎉恭喜！你胡牌了！")
            break
        input("\n按回车摸一张牌>>>")
        new_tile = tile_pool.pop()
        player_hand.append(new_tile)
        player_hand.sort()
        print(f"摸到：{new_tile}，当前手牌：{player_hand}")

        # 选牌丢弃
        while True:
            try:
                drop = int(input("输入要丢弃的牌(数字)："))
                if drop in player_hand:
                    player_hand.remove(drop)
                    break
                else:
                    print("你的手牌没有这张牌！")
            except ValueError:
                print("请输入数字！")

if __name__ == "__main__":
    main()
