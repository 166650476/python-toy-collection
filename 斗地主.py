import tkinter as tk
from tkinter import messagebox
import random

# ===================== 基础配置 =====================
CARD_RANK = {
    '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 11, 'Q': 12, 'K': 13, 'A': 14, '2': 15, '小王': 16, '大王': 17
}
SUITS = ['♠', '♥', '♣', '♦']
CARD_COLOR = {
    '♠': '#111', '♥': '#d92d20', '♣': '#111', '♦': '#d92d20'
}

def create_deck():
    deck = []
    for point in CARD_RANK:
        if point in ['小王', '大王']:
            continue
        for suit in SUITS:
            deck.append(f"{suit}{point}")
    deck.append('小王')
    deck.append('大王')
    return deck

def get_card_value(card):
    if card == '小王':
        return 16
    if card == '大王':
        return 17
    point = card[1:]
    return CARD_RANK[point]

def sort_cards(cards):
    return sorted(cards, key=lambda x: get_card_value(x), reverse=True)

def get_points_list(cards):
    return sorted([get_card_value(c) for c in cards])

# ===================== 牌型判定（严格官方规则） =====================
def get_card_type(cards):
    n = len(cards)
    points = get_points_list(cards)
    point_count = {}
    for p in points:
        point_count[p] = point_count.get(p, 0) + 1
    counts = sorted(point_count.values(), reverse=True)
    unique_points = sorted(point_count.keys())

    # 1. 王炸
    if n == 2 and set(points) == {16, 17}:
        return ('王炸', 17)

    # 2. 炸弹
    if n == 4 and counts[0] == 4:
        return ('炸弹', unique_points[0])

    # 3. 单张
    if n == 1:
        return ('单张', points[0])

    # 4. 对子
    if n == 2 and counts[0] == 2:
        return ('对子', unique_points[0])

    # 5. 三张
    if n == 3 and counts[0] == 3:
        return ('三张', unique_points[0])

    # 6. 三带一
    if n == 4 and counts[0] == 3 and counts[1] == 1:
        main = [p for p, cnt in point_count.items() if cnt == 3][0]
        return ('三带一', main)

    # 7. 三带二
    if n == 5 and counts[0] == 3 and counts[1] == 2:
        main = [p for p, cnt in point_count.items() if cnt == 3][0]
        return ('三带二', main)

    # 8. 顺子
    if n >= 5 and counts[0] == 1:
        if max(points) <= 14 and points[-1] - points[0] == n - 1:
            return ('顺子', points[-1])

    # 9. 连对
    if n >= 6 and n % 2 == 0 and counts[0] == 2 and len(counts) == n//2:
        if max(unique_points) <= 14 and unique_points[-1] - unique_points[0] == len(unique_points) - 1:
            return ('连对', unique_points[-1])

    # 10. 飞机（不带翅膀）
    if n % 3 == 0 and n >= 6 and counts[0] == 3 and len(counts) == n//3:
        if max(unique_points) <= 14 and unique_points[-1] - unique_points[0] == len(unique_points) - 1:
            return ('飞机', unique_points[-1])

    # 11. 四带二
    if n == 6 and counts[0] == 4:
        main = [p for p, cnt in point_count.items() if cnt == 4][0]
        return ('四带二', main)

    # 12. 飞机带单
    if n >= 8 and n % 4 == 0:
        group = n // 4
        if counts.count(3) == group and counts.count(1) == group:
            three_points = sorted([p for p, cnt in point_count.items() if cnt == 3])
            if max(three_points) <= 14 and three_points[-1] - three_points[0] == group - 1:
                return ('飞机带单', three_points[-1])

    # 13. 飞机带对
    if n >= 10 and n % 5 == 0:
        group = n // 5
        if counts.count(3) == group and counts.count(2) == group:
            three_points = sorted([p for p, cnt in point_count.items() if cnt == 3])
            if max(three_points) <= 14 and three_points[-1] - three_points[0] == group - 1:
                return ('飞机带对', three_points[-1])

    return (None, 0)

def can_beat(curr_cards, last_cards):
    curr_type, curr_main = get_card_type(curr_cards)
    last_type, last_main = get_card_type(last_cards)

    if curr_type is None:
        return False

    if curr_type == '王炸':
        return True

    if curr_type == '炸弹' and last_type not in ['炸弹', '王炸']:
        return True

    if curr_type == '炸弹' and last_type == '炸弹':
        return curr_main > last_main

    if curr_type == last_type and len(curr_cards) == len(last_cards):
        return curr_main > last_main

    return False

# ===================== 玩家类 =====================
class Player:
    def __init__(self, name, position):
        self.name = name
        self.position = position  # 0=玩家1 1=玩家2 2=玩家3
        self.cards = []
        self.is_landlord = False
        self.played_cards = []

    def add_cards(self, new_cards):
        self.cards.extend(new_cards)
        self.cards = sort_cards(self.cards)

    def remove_cards(self, cards):
        for c in cards:
            self.cards.remove(c)
            self.played_cards.append(c)

# ===================== GUI 主游戏 =====================
class LandlordGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("斗地主 - 全手动版")
        self.geometry("1120x780")
        self.resizable(False, False)
        self.configure(bg='#0a6b2c')

        # 游戏状态
        self.players = [
            Player('玩家1（下家）', 0),
            Player('玩家2（上家）', 1),
            Player('玩家3（地主位）', 2),
        ]
        self.bottom_cards = []
        self.landlord_idx = -1
        self.last_cards = []
        self.last_player = -1
        self.pass_count = 0
        self.turn = 0
        self.selected_cards = []
        self.game_over = False
        self.bid_phase = False

        self.build_ui()
        self.start_new_game()

    def build_ui(self):
        # 顶部底牌+当前回合提示
        top_frame = tk.Frame(self, bg='#0a6b2c', height=70)
        top_frame.pack(fill='x', pady=8)
        self.bottom_label = tk.Label(top_frame, text="底牌：等待叫地主", 
                                    font=('微软雅黑', 12, 'bold'), bg='#0a6b2c', fg='#ffd700')
        self.bottom_label.pack()
        self.turn_label = tk.Label(top_frame, text="", 
                                  font=('微软雅黑', 11, 'bold'), bg='#0a6b2c', fg='white')
        self.turn_label.pack(pady=2)

        # 中间主区域
        main_frame = tk.Frame(self, bg='#0a6b2c')
        main_frame.pack(fill='both', expand=True)

        # 左边玩家2
        left_frame = tk.Frame(main_frame, bg='#0a6b2c', width=170)
        left_frame.pack(side='left', fill='y', padx=15)
        tk.Label(left_frame, text="玩家2（上家）", font=('微软雅黑', 11, 'bold'), 
                bg='#0a6b2c', fg='#fff').pack()
        self.left_count = tk.Label(left_frame, text="17张", 
                                   font=('微软雅黑', 10), bg='#0a6b2c', fg='#e0e0e0')
        self.left_count.pack(pady=5)
        self.left_play = tk.Label(left_frame, text="", 
                                  font=('微软雅黑', 10), bg='#0a6b2c', fg='#fff')
        self.left_play.pack(pady=15)

        # 中央信息区
        center_frame = tk.Frame(main_frame, bg='#0a6b2c')
        center_frame.pack(side='left', fill='both', expand=True)
        self.info_text = tk.Text(center_frame, height=13, font=('微软雅黑', 9),
                                 bg='#074e1f', fg='#f0f0f0', relief='flat')
        self.info_text.pack(fill='both', expand=True, padx=10, pady=10)

        # 右边玩家3
        right_frame = tk.Frame(main_frame, bg='#0a6b2c', width=170)
        right_frame.pack(side='right', fill='y', padx=15)
        tk.Label(right_frame, text="玩家3", font=('微软雅黑', 11, 'bold'), 
                bg='#0a6b2c', fg='#fff').pack()
        self.right_count = tk.Label(right_frame, text="17张", 
                                    font=('微软雅黑', 10), bg='#0a6b2c', fg='#e0e0e0')
        self.right_count.pack(pady=5)
        self.right_play = tk.Label(right_frame, text="", 
                                   font=('微软雅黑', 10), bg='#0a6b2c', fg='#fff')
        self.right_play.pack(pady=15)

        # 底部当前玩家手牌区
        bottom_frame = tk.Frame(self, bg='#0a6b2c', height=230)
        bottom_frame.pack(fill='x', side='bottom')
        self.player_title = tk.Label(bottom_frame, text="当前玩家：玩家1", 
                                     font=('微软雅黑', 11, 'bold'), 
                                     bg='#0a6b2c', fg='#ffd700')
        self.player_title.pack(pady=5)

        self.card_frame = tk.Frame(bottom_frame, bg='#0a6b2c')
        self.card_frame.pack(pady=5)

        # 按钮区
        btn_frame = tk.Frame(bottom_frame, bg='#0a6b2c')
        btn_frame.pack(pady=8)

        self.play_btn = tk.Button(btn_frame, text="出牌", command=self.play_card,
                                  width=10, bg='#d92d20', fg='white', font=('微软雅黑', 10, 'bold'))
        self.play_btn.pack(side='left', padx=8)

        self.pass_btn = tk.Button(btn_frame, text="过牌", command=self.pass_card,
                                  width=10, bg='#555', fg='white', font=('微软雅黑', 10, 'bold'))
        self.pass_btn.pack(side='left', padx=8)

        self.restart_btn = tk.Button(btn_frame, text="重新开始", command=self.start_new_game,
                                     width=10, bg='#1a56db', fg='white', font=('微软雅黑', 10, 'bold'))
        self.restart_btn.pack(side='left', padx=8)

    def log(self, msg):
        self.info_text.insert('end', msg + '\n')
        self.info_text.see('end')

    def start_new_game(self):
        self.game_over = False
        self.last_cards = []
        self.last_player = -1
        self.pass_count = 0
        self.selected_cards = []
        self.info_text.delete('1.0', 'end')
        self.log("===== 新一局开始 =====")

        for p in self.players:
            p.cards = []
            p.is_landlord = False
            p.played_cards = []

        # 发牌
        deck = create_deck()
        random.shuffle(deck)
        for i in range(17):
            for j in range(3):
                self.players[j].add_cards([deck.pop()])
        self.bottom_cards = deck

        self.update_counts()
        self.bottom_label.config(text="底牌：???  叫地主阶段")
        self.left_play.config(text="")
        self.right_play.config(text="")
        self.log("开始叫地主，按顺序叫分")

        # 进入叫地主阶段
        self.bid_phase = True
        self.bid_order = [0, 1, 2]
        self.bid_index = 0
        self.bids = [0, 0, 0]
        self.max_bid = 0
        self.turn = 0
        self.show_current_player()
        self.do_bid_step()

    def do_bid_step(self):
        idx = self.bid_order[self.bid_index]
        self.turn = idx
        self.show_current_player()
        p = self.players[idx]
        
        bid = messagebox.askyesnocancel(f"叫地主 - {p.name}", 
                                       f"{p.name} 是否叫地主？\n是：叫3分\n否：不叫\n取消：退出叫分")
        if bid is None:
            self.bids[idx] = 0
        elif bid:
            self.bids[idx] = 3
            self.max_bid = 3
            self.log(f"{p.name} 叫 3 分")
        else:
            self.bids[idx] = 0
            self.log(f"{p.name} 不叫")

        self.bid_index += 1
        if self.bid_index < 3:
            self.after(200, self.do_bid_step)
        else:
            self.finish_bid()

    def finish_bid(self):
        if self.max_bid == 0:
            self.log("无人叫地主，重新发牌！")
            self.after(1000, self.start_new_game)
            return

        self.landlord_idx = self.bids.index(self.max_bid)
        landlord = self.players[self.landlord_idx]
        landlord.is_landlord = True
        landlord.add_cards(self.bottom_cards)

        self.bottom_label.config(text=f"底牌：{'  '.join(self.bottom_cards)}  |  地主：{landlord.name}")
        self.log(f"\n{landlord.name} 成为地主！")
        self.update_counts()

        # 地主先出牌
        self.turn = self.landlord_idx
        self.last_player = -1
        self.pass_count = 0
        self.bid_phase = False
        self.show_current_player()
        self.log(f"\n轮到 {self.players[self.turn].name} 出牌")

    def update_counts(self):
        self.left_count.config(text=f"{len(self.players[1].cards)}张")
        self.right_count.config(text=f"{len(self.players[2].cards)}张")

    def show_current_player(self):
        """切换显示当前玩家的手牌"""
        p = self.players[self.turn]
        self.player_title.config(text=f"当前操作：{p.name}")
        self.selected_cards = []
        self.update_card_display()

    def update_card_display(self):
        # 清空旧牌
        for w in self.card_frame.winfo_children():
            w.destroy()

        current_cards = self.players[self.turn].cards

        # 生成手牌按钮
        for card in current_cards:
            if card in ['小王', '大王']:
                color = '#d92d20' if card == '大王' else '#111'
                text = card
            else:
                color = CARD_COLOR.get(card[0], '#111')
                text = card

            selected = card in self.selected_cards
            bg = '#fff3cd' if selected else 'white'
            relief = 'sunken' if selected else 'raised'

            btn = tk.Button(self.card_frame, text=text, width=4, height=2,
                            font=('微软雅黑', 9, 'bold'),
                            bg=bg, fg=color, relief=relief,
                            command=lambda c=card: self.toggle_card(c))
            btn.pack(side='left', padx=1)

    def toggle_card(self, card):
        if self.game_over or self.bid_phase:
            return
        if card in self.selected_cards:
            self.selected_cards.remove(card)
        else:
            self.selected_cards.append(card)
        self.update_card_display()

    def play_card(self):
        if self.game_over or self.bid_phase:
            return
        if not self.selected_cards:
            messagebox.showwarning("提示", "请先选择要出的牌！")
            return

        cards = self.selected_cards.copy()
        card_type, _ = get_card_type(cards)
        if card_type is None:
            messagebox.showerror("错误", "非法牌型！")
            return

        if self.last_player != -1 and self.pass_count < 2:
            if not can_beat(cards, self.last_cards):
                messagebox.showerror("错误", "压不住上家的牌！")
                return

        # 出牌成功
        p = self.players[self.turn]
        p.remove_cards(cards)
        self.last_cards = cards
        self.last_player = self.turn
        self.pass_count = 0
        self.selected_cards = []

        self.log(f"\n{p.name} 出牌：{'  '.join(cards)} ({card_type})")

        # 更新左右显示
        if self.turn == 1:
            self.left_play.config(text='  '.join(cards))
        elif self.turn == 2:
            self.right_play.config(text='  '.join(cards))

        self.update_counts()
        self.update_card_display()

        if self.check_win(self.turn):
            return

        # 下一家
        self.turn = (self.turn + 1) % 3
        self.show_current_player()
        self.log(f"\n轮到 {self.players[self.turn].name} 出牌")

    def pass_card(self):
        if self.game_over or self.bid_phase:
            return
        if self.last_player == -1 or self.pass_count == 2:
            messagebox.showwarning("提示", "你是首家，不能过牌！")
            return

        p = self.players[self.turn]
        self.log(f"\n{p.name} 选择过牌")
        self.pass_count += 1

        self.turn = (self.turn + 1) % 3
        self.show_current_player()
        self.log(f"\n轮到 {self.players[self.turn].name} 出牌")

    def check_win(self, idx):
        if len(self.players[idx].cards) == 0:
            self.game_over = True
            winner = self.players[idx]
            if winner.is_landlord:
                msg = f"🎉 {winner.name}（地主）获胜！"
            else:
                msg = f"🎉 农民方获胜！{winner.name} 先出完牌"
            self.log("\n" + "="*30)
            self.log(msg)
            messagebox.showinfo("游戏结束", msg)
            return True
        return False

if __name__ == "__main__":
    app = LandlordGUI()
    app.mainloop()
