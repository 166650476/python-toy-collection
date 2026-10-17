import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import openpyxl

# 中文显示配置
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False


class AccountingSystem(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("会计学习仿真综合系统")
        self.geometry("1280x780")
        self.resizable(False, False)

        # 顶部标题
        tk.Label(self, text="会计专业学习仿真综合系统",
                 font=("微软雅黑", 16, "bold"), fg="#1a56db").pack(pady=8)

        # 全局学习数据
        self.study_data = {
            "chapter_scores": {},
            "done_questions": 0,
            "correct_questions": 0
        }

        # 多标签页容器
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=5)

        # 9大核心模块
        self.build_entry_page()       # 1.会计分录仿真
        self.build_taccount_page()    # 2.T型账与科目汇总
        self.build_bank_page()        # 3.银行存款余额调节表 ✅新增
        self.build_correction_page()  # 4.错账更正方法 ✅新增
        self.build_report_page()      # 5.财务报表生成
        self.build_cost_page()        # 6.成本核算仿真
        self.build_depreciation_page() # 7.折旧摊销计算
        self.build_exam_page()        # 8.会计章节题库
        self.build_analysis_page()    # 9.学习数据可视化

    # ===================== 1. 会计分录仿真模块 =====================
    def build_entry_page(self):
        page = ttk.Frame(self.notebook)
        self.notebook.add(page, text="会计分录仿真")

        left = tk.Frame(page, padx=20, pady=20)
        left.pack(side="left", fill="y")

        tk.Label(left, text="会计业务类型", font=("微软雅黑", 12, "bold")).pack(anchor="w", pady=(0,10))

        self.biz_type = ttk.Combobox(left, state="readonly", width=28, values=[
            "【基础】收到投资款",
            "【基础】购入原材料（赊购）",
            "【基础】生产领用原材料",
            "【基础】销售商品（赊销）",
            "【基础】计提工资",
            "【基础】计提折旧",
            "【进阶】计提存货跌价准备",
            "【进阶】交易性金融资产购入",
            "【进阶】确认投资收益",
            "【进阶】计提法定盈余公积"
        ])
        self.biz_type.current(0)
        self.biz_type.pack(pady=5)
        self.biz_type.bind("<<ComboboxSelected>>", self.show_entry_params)

        self.param_frame = tk.Frame(left)
        self.param_frame.pack(pady=10, fill="x")
        self.entry_params = {}

        tk.Button(left, text="生成标准会计分录", command=self.generate_entry,
                  width=22, bg="#1a56db", fg="white").pack(pady=15)

        tk.Label(left, text="记账凭证", font=("微软雅黑", 11, "bold")).pack(anchor="w")
        self.entry_text = tk.Text(left, width=42, height=18, font=("微软雅黑", 10))
        self.entry_text.pack(pady=5)

        # 右侧科目金额图
        self.entry_fig = plt.Figure(figsize=(6, 5), dpi=100)
        self.entry_canvas = FigureCanvasTkAgg(self.entry_fig, master=page)
        self.entry_canvas.get_tk_widget().pack(side="right", padx=10, pady=10)
        self.show_entry_params()

    def show_entry_params(self, e=None):
        for widget in self.param_frame.winfo_children():
            widget.destroy()
        self.entry_params.clear()

        biz = self.biz_type.get()
        params_map = {
            "【基础】收到投资款": [("投资金额(元)", "amount", "100000")],
            "【基础】购入原材料（赊购）": [("价款(元)", "price", "50000"), ("增值税(元)", "tax", "6500")],
            "【基础】生产领用原材料": [("领用材料成本(元)", "cost", "30000")],
            "【基础】销售商品（赊销）": [("不含税收入(元)", "revenue", "80000"), ("增值税(元)", "tax", "10400")],
            "【基础】计提工资": [("生产工人工资(元)", "prod", "20000"), ("车间管理工资(元)", "workshop", "8000"), ("行政工资(元)", "mgmt", "12000")],
            "【基础】计提折旧": [("车间折旧(元)", "workshop", "5000"), ("行政折旧(元)", "mgmt", "3000")],
            "【进阶】计提存货跌价准备": [("成本(元)", "cost", "20000"), ("可变现净值(元)", "nrv", "17000")],
            "【进阶】交易性金融资产购入": [("成本(元)", "cost", "50000"), ("交易费用(元)", "fee", "2000")],
            "【进阶】确认投资收益": [("宣告股利(元)", "dividend", "8000")],
            "【进阶】计提法定盈余公积": [("净利润(元)", "profit", "100000"), ("提取比例(%)", "rate", "10")]
        }

        for label, key, default in params_map[biz]:
            row = tk.Frame(self.param_frame)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label, width=20, anchor="w").pack(side="left")
            entry = tk.Entry(row, width=12)
            entry.insert(0, default)
            entry.pack(side="right")
            self.entry_params[key] = entry

    def generate_entry(self):
        biz = self.biz_type.get()
        entries = []
        amounts = {}

        try:
            if biz == "【基础】收到投资款":
                amount = float(self.entry_params["amount"].get())
                entries = [("借：银行存款", amount), ("贷：实收资本", amount)]
                amounts = {"银行存款": amount, "实收资本": amount}

            elif biz == "【基础】购入原材料（赊购）":
                price = float(self.entry_params["price"].get())
                tax = float(self.entry_params["tax"].get())
                entries = [("借：原材料", price), ("借：应交税费-进项税额", tax), ("贷：应付账款", price+tax)]
                amounts = {"原材料": price, "应交税费": tax, "应付账款": price+tax}

            elif biz == "【基础】生产领用原材料":
                cost = float(self.entry_params["cost"].get())
                entries = [("借：生产成本", cost), ("贷：原材料", cost)]
                amounts = {"生产成本": cost, "原材料": cost}

            elif biz == "【基础】销售商品（赊销）":
                revenue = float(self.entry_params["revenue"].get())
                tax = float(self.entry_params["tax"].get())
                entries = [("借：应收账款", revenue+tax), ("贷：主营业务收入", revenue), ("贷：应交税费-销项税额", tax)]
                amounts = {"应收账款": revenue+tax, "主营业务收入": revenue, "应交税费": tax}

            elif biz == "【基础】计提工资":
                prod = float(self.entry_params["prod"].get())
                workshop = float(self.entry_params["workshop"].get())
                mgmt = float(self.entry_params["mgmt"].get())
                total = prod + workshop + mgmt
                entries = [("借：生产成本", prod), ("借：制造费用", workshop), ("借：管理费用", mgmt), ("贷：应付职工薪酬", total)]
                amounts = {"生产成本": prod, "制造费用": workshop, "管理费用": mgmt, "应付职工薪酬": total}

            elif biz == "【基础】计提折旧":
                workshop = float(self.entry_params["workshop"].get())
                mgmt = float(self.entry_params["mgmt"].get())
                total = workshop + mgmt
                entries = [("借：制造费用", workshop), ("借：管理费用", mgmt), ("贷：累计折旧", total)]
                amounts = {"制造费用": workshop, "管理费用": mgmt, "累计折旧": total}

            elif biz == "【进阶】计提存货跌价准备":
                cost = float(self.entry_params["cost"].get())
                nrv = float(self.entry_params["nrv"].get())
                loss = cost - nrv
                if loss <= 0:
                    messagebox.showinfo("提示", "可变现净值高于成本，无需计提减值")
                    return
                entries = [("借：资产减值损失", loss), ("贷：存货跌价准备", loss)]
                amounts = {"资产减值损失": loss, "存货跌价准备": loss}

            elif biz == "【进阶】交易性金融资产购入":
                cost = float(self.entry_params["cost"].get())
                fee = float(self.entry_params["fee"].get())
                entries = [("借：交易性金融资产-成本", cost), ("借：投资收益", fee), ("贷：银行存款", cost+fee)]
                amounts = {"交易性金融资产": cost, "投资收益": fee, "银行存款": cost+fee}

            elif biz == "【进阶】确认投资收益":
                div = float(self.entry_params["dividend"].get())
                entries = [("借：应收股利", div), ("贷：投资收益", div)]
                amounts = {"应收股利": div, "投资收益": div}

            elif biz == "【进阶】计提法定盈余公积":
                profit = float(self.entry_params["profit"].get())
                rate = float(self.entry_params["rate"].get())/100
                reserve = profit * rate
                entries = [("借：利润分配-提取盈余公积", reserve), ("贷：盈余公积-法定盈余公积", reserve)]
                amounts = {"利润分配": reserve, "盈余公积": reserve}

            # 显示分录
            self.entry_text.delete("1.0", "end")
            self.entry_text.insert("end", f"摘要：{biz}\n")
            self.entry_text.insert("end", "="*45 + "\n")
            for subject, amount in entries:
                if "借：" in subject:
                    self.entry_text.insert("end", f"{subject:<28} {amount:>12,.2f}\n")
                else:
                    self.entry_text.insert("end", f"    {subject:<24} {amount:>12,.2f}\n")

            # 绘制金额图
            self.entry_fig.clear()
            ax = self.entry_fig.add_subplot(111)
            subjects = list(amounts.keys())
            values = [abs(v) for v in amounts.values()]
            colors = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"]
            bars = ax.bar(subjects, values, color=colors[:len(subjects)])
            for bar, val in zip(bars, values):
                ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+max(values)*0.01,
                        f"{val:,.0f}", ha="center", fontsize=9)
            ax.set_title("业务涉及科目金额")
            ax.set_ylabel("金额(元)")
            ax.grid(axis="y", alpha=0.3)
            plt.setp(ax.get_xticklabels(), rotation=15)
            self.entry_canvas.draw()

        except ValueError:
            messagebox.showerror("错误", "请输入有效数字！")

    # ===================== 2. T型账与科目汇总 =====================
    def build_taccount_page(self):
        page = ttk.Frame(self.notebook)
        self.notebook.add(page, text="T型账与科目汇总")

        left = tk.Frame(page, padx=20, pady=20)
        left.pack(side="left", fill="y")

        tk.Label(left, text="输入本期业务分录", font=("微软雅黑", 12, "bold")).pack(anchor="w", pady=(0,10))
        tk.Label(left, text="格式：科目名,借方金额,贷方金额\n每行一笔分录", fg="#666", font=("微软雅黑",9)).pack(anchor="w")

        self.entry_input = tk.Text(left, width=35, height=12, font=("微软雅黑", 10))
        self.entry_input.insert("end", """银行存款,100000,0
原材料,50000,0
应交税费,6500,0
应付账款,0,56500
生产成本,30000,0
原材料,0,30000
应收账款,90400,0
主营业务收入,0,80000
应交税费,0,10400""")
        self.entry_input.pack(pady=5)

        tk.Button(left, text="生成T型账与科目汇总", command=self.generate_taccount,
                  width=22, bg="#0a8f4a", fg="white").pack(pady=15)

        tk.Label(left, text="科目汇总表", font=("微软雅黑", 11, "bold")).pack(anchor="w")
        self.summary_text = tk.Text(left, width=35, height=10, font=("微软雅黑", 10))
        self.summary_text.pack(pady=5)

        # 右侧T型账展示
        right = tk.Frame(page, padx=10, pady=10)
        right.pack(side="right", fill="both", expand=True)
        tk.Label(right, text="T型账户", font=("微软雅黑", 11, "bold")).pack(anchor="w")
        self.taccount_text = tk.Text(right, width=55, height=30, font=("Consolas", 10))
        self.taccount_text.pack(fill="both", expand=True)

    def generate_taccount(self):
        raw = self.entry_input.get("1.0", "end").strip().split("\n")
        accounts = {}

        try:
            for line in raw:
                if not line.strip():
                    continue
                name, debit, credit = line.split(",")
                name = name.strip()
                debit = float(debit.strip())
                credit = float(credit.strip())
                if name not in accounts:
                    accounts[name] = {"debit": [], "credit": []}
                if debit > 0:
                    accounts[name]["debit"].append(debit)
                if credit > 0:
                    accounts[name]["credit"].append(credit)

            # 生成T型账
            self.taccount_text.delete("1.0", "end")
            summary = {}
            for name, data in accounts.items():
                total_debit = sum(data["debit"])
                total_credit = sum(data["credit"])
                balance = total_debit - total_credit
                summary[name] = (total_debit, total_credit, balance)

                # T型账格式
                self.taccount_text.insert("end", f"\n{'='*20} {name} {'='*20}\n")
                self.taccount_text.insert("end", f"{'借方':^24}|{'贷方':^24}\n")
                self.taccount_text.insert("end", "-"*50 + "\n")
                
                max_rows = max(len(data["debit"]), len(data["credit"]))
                for i in range(max_rows):
                    d = f"{data['debit'][i]:,.2f}" if i < len(data["debit"]) else ""
                    c = f"{data['credit'][i]:,.2f}" if i < len(data["credit"]) else ""
                    self.taccount_text.insert("end", f"{d:^24}|{c:^24}\n")
                
                self.taccount_text.insert("end", "-"*50 + "\n")
                bal_text = f"期末余额: {balance:,.2f}"
                self.taccount_text.insert("end", f"{bal_text:^50}\n")

            # 科目汇总表
            self.summary_text.delete("1.0", "end")
            self.summary_text.insert("end", f"{'科目':<12}{'借方合计':>12}{'贷方合计':>12}{'余额':>12}\n")
            self.summary_text.insert("end", "-"*48 + "\n")
            for name, (d, c, b) in summary.items():
                self.summary_text.insert("end", f"{name:<12}{d:>12,.2f}{c:>12,.2f}{b:>12,.2f}\n")

        except Exception as e:
            messagebox.showerror("错误", f"格式错误：{str(e)}\n请按「科目,借方,贷方」每行一笔输入")

    # ===================== 3. 银行存款余额调节表 ✅新增 =====================
    def build_bank_page(self):
        page = ttk.Frame(self.notebook)
        self.notebook.add(page, text="银行余额调节表")

        left = tk.Frame(page, padx=20, pady=20)
        left.pack(side="left", fill="y")

        tk.Label(left, text="未达账项与余额", font=("微软雅黑", 12, "bold")).pack(anchor="w", pady=(0,10))

        self.bank_inputs = {}
        items = [
            ("企业银行存款日记账余额", "book_balance", "80000"),
            ("银行对账单余额", "bank_balance", "82000"),
            ("企业已收，银行未收", "ent_not_bank", "5000"),
            ("企业已付，银行未付", "pay_not_bank", "3000"),
            ("银行已收，企业未收", "bank_not_ent", "6000"),
            ("银行已付，企业未付", "bank_not_pay", "2000"),
        ]
        for label, key, default in items:
            row = tk.Frame(left)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, width=20, anchor="w").pack(side="left")
            entry = tk.Entry(row, width=12)
            entry.insert(0, default)
            entry.pack(side="right")
            self.bank_inputs[key] = entry

        tk.Button(left, text="生成银行存款余额调节表", command=self.generate_bank_reconcile,
                  width=22, bg="#0ea5e9", fg="white").pack(pady=15)

        self.bank_result = tk.Label(left, text="", font=("微软雅黑", 10, "bold"))
        self.bank_result.pack(pady=5)

        # 右侧调节表展示
        right = tk.Frame(page, padx=10, pady=10)
        right.pack(side="right", fill="both", expand=True)
        self.bank_text = tk.Text(right, width=60, height=30, font=("微软雅黑", 10))
        self.bank_text.pack(fill="both", expand=True)

    def generate_bank_reconcile(self):
        try:
            book = float(self.bank_inputs["book_balance"].get())
            bank = float(self.bank_inputs["bank_balance"].get())
            ent_not_bank = float(self.bank_inputs["ent_not_bank"].get())
            pay_not_bank = float(self.bank_inputs["pay_not_bank"].get())
            bank_not_ent = float(self.bank_inputs["bank_not_ent"].get())
            bank_not_pay = float(self.bank_inputs["bank_not_pay"].get())

            # 调节后余额
            adjusted_book = book + bank_not_ent - bank_not_pay
            adjusted_bank = bank + ent_not_bank - pay_not_bank

            # 生成调节表
            self.bank_text.delete("1.0", "end")
            self.bank_text.insert("end", "="*60 + "\n")
            self.bank_text.insert("end", f"{'银行存款余额调节表':^60}\n")
            self.bank_text.insert("end", "="*60 + "\n\n")

            self.bank_text.insert("end", f"{'项目':<30}{'金额':>15}    {'项目':<30}{'金额':>15}\n")
            self.bank_text.insert("end", "-"*60 + "\n")

            self.bank_text.insert("end", f"企业银行存款日记账余额：{book:>15,.2f}    银行对账单余额：      {bank:>15,.2f}\n")
            self.bank_text.insert("end", f"加：银行已收企业未收：{bank_not_ent:>15,.2f}    加：企业已收银行未收：{ent_not_bank:>15,.2f}\n")
            self.bank_text.insert("end", f"减：银行已付企业未付：{bank_not_pay:>15,.2f}    减：企业已付银行未付：{pay_not_bank:>15,.2f}\n")
            self.bank_text.insert("end", "-"*60 + "\n")
            self.bank_text.insert("end", f"调节后的存款余额：  {adjusted_book:>15,.2f}    调节后的存款余额：  {adjusted_bank:>15,.2f}\n")
            self.bank_text.insert("end", "="*60 + "\n\n")

            if abs(adjusted_book - adjusted_bank) < 0.01:
                self.bank_result.config(text="✅ 调节后余额相等，记账基本正确", fg="#0a8f4a")
                self.bank_text.insert("end", "调节说明：调节后双方余额相等，说明双方记账基本正确，\n未达账项是造成余额不一致的主要原因。\n")
            else:
                self.bank_result.config(text="❌ 调节后余额不相等，请检查记账错误", fg="#d92d20")
                self.bank_text.insert("end", "调节说明：调节后双方余额不相等，说明存在记账错误，\n需进一步检查企业日记账或银行对账单记录。\n")

        except ValueError:
            messagebox.showerror("错误", "请输入有效数字！")

    # ===================== 4. 错账更正方法 ✅新增 =====================
    def build_correction_page(self):
        page = ttk.Frame(self.notebook)
        self.notebook.add(page, text="错账更正方法")

        left = tk.Frame(page, padx=20, pady=20)
        left.pack(side="left", fill="y")

        tk.Label(left, text="错账类型选择", font=("微软雅黑", 12, "bold")).pack(anchor="w", pady=(0,10))

        self.corr_type = ttk.Combobox(left, state="readonly", width=28, values=[
            "划线更正法（凭证正确，账簿文字/数字错误）",
            "红字更正法1（会计科目使用错误）",
            "红字更正法2（所记金额大于应记金额）",
            "补充登记法（所记金额小于应记金额）"
        ])
        self.corr_type.current(0)
        self.corr_type.pack(pady=5)
        self.corr_type.bind("<<ComboboxSelected>>", self.show_corr_params)

        self.corr_param_frame = tk.Frame(left)
        self.corr_param_frame.pack(pady=10, fill="x")
        self.corr_params = {}

        tk.Button(left, text="生成更正分录与说明", command=self.generate_correction,
                  width=22, bg="#f59e0b", fg="white").pack(pady=15)

        tk.Label(left, text="更正说明与分录", font=("微软雅黑", 11, "bold")).pack(anchor="w")
        self.corr_text = tk.Text(left, width=42, height=18, font=("微软雅黑", 10))
        self.corr_text.pack(pady=5)

        # 右侧方法对比
        right = tk.Frame(page, padx=10, pady=10)
        right.pack(side="right", fill="both", expand=True)
        tk.Label(right, text="错账更正方法适用场景", font=("微软雅黑", 11, "bold")).pack(anchor="w")
        self.corr_info = tk.Text(right, width=50, height=30, font=("微软雅黑", 10))
        self.corr_info.pack(fill="both", expand=True)
        
        # 预置方法说明
        info = """
【划线更正法】
适用场景：结账前，发现账簿记录
有文字或数字错误，而记账凭
证没有错误。
更正方法：在错误的文字或数
字上划一条红线，在红线的上方
填写正确的文字或数字，并由记
账人员在更正处盖章。

【红字更正法】
适用场景1：记账后，发现记账
凭证中的会计科目错误。
更正方法：先用红字金额填制一
张与原错误凭证完全相同的记账
凭证，冲销原错误记录；再用蓝
字填制一张正确的记账凭证。

适用场景2：记账后，发现记账凭
证和账簿中所记金额大于应记
金额，会计科目无误。
更正方法：按多记的金额，用红
字填制一张与原凭证科目相同的
记账凭证，冲销多记金额。

【补充登记法】
适用场景：记账后，发现记账凭
证和账簿中所记金额小于应记
金额，会计科目无误。
更正方法：按少记的金额，用蓝
字填制一张与原凭证科目相同的
记账凭证，补充登记少记金额。
"""
        self.corr_info.insert("end", info)
        self.show_corr_params()

    def show_corr_params(self, e=None):
        for widget in self.corr_param_frame.winfo_children():
            widget.destroy()
        self.corr_params.clear()

        ctype = self.corr_type.get()
        params_map = {
            "划线更正法（凭证正确，账簿文字/数字错误）": [("错误内容", "wrong", "管理费用3000写成管理费用300"),
                                                       ("正确内容", "right", "管理费用3000")],
            "红字更正法1（会计科目使用错误）": [("错误借方科目", "wrong_dr", "制造费用"),
                                                          ("错误贷方科目", "wrong_cr", "原材料"),
                                                          ("金额(元)", "amount", "5000"),
                                                          ("正确借方科目", "right_dr", "生产成本"),
                                                          ("正确贷方科目", "right_cr", "原材料")],
            "红字更正法2（所记金额大于应记金额）": [("会计科目", "subject", "原材料"),
                                                          ("错误金额(元)", "wrong_amt", "8000"),
                                                          ("正确金额(元)", "right_amt", "5000")],
            "补充登记法（所记金额小于应记金额）": [("会计科目", "subject", "原材料"),
                                                          ("错误金额(元)", "wrong_amt", "5000"),
                                                          ("正确金额(元)", "right_amt", "8000")]
        }

        for label, key, default in params_map[ctype]:
            row = tk.Frame(self.corr_param_frame)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label, width=18, anchor="w").pack(side="left")
            entry = tk.Entry(row, width=14)
            entry.insert(0, default)
            entry.pack(side="right")
            self.corr_params[key] = entry

    def generate_correction(self):
        ctype = self.corr_type.get()
        self.corr_text.delete("1.0", "end")

        try:
            if ctype.startswith("划线更正法"):
                wrong = self.corr_params["wrong"].get()
                right = self.corr_params["right"].get()
                self.corr_text.insert("end", "【划线更正法】\n\n")
                self.corr_text.insert("end", f"错误记录：{wrong}\n")
                self.corr_text.insert("end", f"正确记录：{right}\n\n")
                self.corr_text.insert("end", "更正方法：\n")
                self.corr_text.insert("end", "1. 在错误文字/数字上划红线注销\n")
                self.corr_text.insert("end", "2. 在上方填写正确内容\n")
                self.corr_text.insert("end", "3. 更正处加盖记账人员印章\n\n")
                self.corr_text.insert("end", "注意：不得涂改、刮擦、挖补。")

            elif ctype.startswith("红字更正法1"):
                wd = self.corr_params["wrong_dr"].get()
                wc = self.corr_params["wrong_cr"].get()
                amt = float(self.corr_params["amount"].get())
                rd = self.corr_params["right_dr"].get()
                rc = self.corr_params["right_cr"].get()

                self.corr_text.insert("end", "【红字更正法 - 科目错误】\n\n")
                self.corr_text.insert("end", "原错误分录：\n")
                self.corr_text.insert("end", f"借：{wd}    {amt:,.2f}\n")
                self.corr_text.insert("end", f"贷：{wc}    {amt:,.2f}\n\n")

                self.corr_text.insert("end", "第一步：红字冲销原错误分录\n")
                self.corr_text.insert("end", f"借：{wd}    {amt:,.2f}（红字）\n")
                self.corr_text.insert("end", f"贷：{wc}    {amt:,.2f}（红字）\n\n")

                self.corr_text.insert("end", "第二步：蓝字填制正确分录\n")
                self.corr_text.insert("end", f"借：{rd}    {amt:,.2f}\n")
                self.corr_text.insert("end", f"贷：{rc}    {amt:,.2f}\n")

            elif ctype.startswith("红字更正法2"):
                sub = self.corr_params["subject"].get()
                wrong = float(self.corr_params["wrong_amt"].get())
                right = float(self.corr_params["right_amt"].get())
                diff = wrong - right

                self.corr_text.insert("end", "【红字更正法 - 金额多记】\n\n")
                self.corr_text.insert("end", f"原记录金额：{wrong:,.2f} 元\n")
                self.corr_text.insert("end", f"正确金额：{right:,.2f} 元\n")
                self.corr_text.insert("end", f"多记金额：{diff:,.2f} 元\n\n")

                self.corr_text.insert("end", "更正分录（冲销多记金额）：\n")
                self.corr_text.insert("end", f"借：{sub}    {diff:,.2f}（红字）\n")
                self.corr_text.insert("end", f"贷：对应科目    {diff:,.2f}（红字）\n\n")
                self.corr_text.insert("end", "注：科目与原凭证一致，仅金额用红字。")

            elif ctype.startswith("补充登记法"):
                sub = self.corr_params["subject"].get()
                wrong = float(self.corr_params["wrong_amt"].get())
                right = float(self.corr_params["right_amt"].get())
                diff = right - wrong

                self.corr_text.insert("end", "【补充登记法 - 金额少记】\n\n")
                self.corr_text.insert("end", f"原记录金额：{wrong:,.2f} 元\n")
                self.corr_text.insert("end", f"正确金额：{right:,.2f} 元\n")
                self.corr_text.insert("end", f"少记金额：{diff:,.2f} 元\n\n")

                self.corr_text.insert("end", "更正分录（补充少记金额）：\n")
                self.corr_text.insert("end", f"借：{sub}    {diff:,.2f}\n")
                self.corr_text.insert("end", f"贷：对应科目    {diff:,.2f}\n\n")
                self.corr_text.insert("end", "注：科目与原凭证一致，用蓝字补记。")

        except ValueError:
            messagebox.showerror("错误", "请输入有效数字！")

    # ===================== 5. 财务报表生成 =====================
    def build_report_page(self):
        page = ttk.Frame(self.notebook)
        self.notebook.add(page, text="财务报表生成")

        left = tk.Frame(page, padx=20, pady=20)
        left.pack(side="left", fill="y")

        tk.Label(left, text="科目期末余额（元）", font=("微软雅黑", 12, "bold")).pack(anchor="w", pady=(0,10))

        self.report_inputs = {}
        items = [
            ("货币资金", "cash", "80000"),
            ("应收账款", "ar", "50000"),
            ("存货", "inventory", "60000"),
            ("固定资产", "fa", "200000"),
            ("累计折旧", "dep", "50000"),
            ("短期借款", "short_loan", "40000"),
            ("应付账款", "ap", "35000"),
            ("实收资本", "capital", "200000"),
            ("盈余公积", "reserve", "15000"),
            ("未分配利润", "retained", "50000"),
            ("营业收入", "revenue", "300000"),
            ("营业成本", "cost", "180000"),
            ("税金及附加", "tax_add", "3000"),
            ("管理费用", "mgmt_exp", "40000"),
            ("销售费用", "sell_exp", "20000"),
            ("财务费用", "fin_exp", "10000"),
            ("所得税费用", "tax_exp", "12000"),
        ]
        for label, key, default in items:
            row = tk.Frame(left)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=label, width=14, anchor="w").pack(side="left")
            entry = tk.Entry(row, width=12)
            entry.insert(0, default)
            entry.pack(side="right")
            self.report_inputs[key] = entry

        tk.Button(left, text="生成财务报表", command=self.generate_report,
                  width=20, bg="#b45309", fg="white").pack(pady=15)

        # 右侧报表展示
        right = tk.Frame(page, padx=10, pady=10)
        right.pack(side="right", fill="both", expand=True)
        self.report_text = tk.Text(right, width=60, height=35, font=("微软雅黑", 10))
        self.report_text.pack(fill="both", expand=True)

    def generate_report(self):
        try:
            # 读取数据
            cash = float(self.report_inputs["cash"].get())
            ar = float(self.report_inputs["ar"].get())
            inv = float(self.report_inputs["inventory"].get())
            fa = float(self.report_inputs["fa"].get())
            dep = float(self.report_inputs["dep"].get())
            short_loan = float(self.report_inputs["short_loan"].get())
            ap = float(self.report_inputs["ap"].get())
            capital = float(self.report_inputs["capital"].get())
            reserve = float(self.report_inputs["reserve"].get())
            retained = float(self.report_inputs["retained"].get())
            revenue = float(self.report_inputs["revenue"].get())
            cost = float(self.report_inputs["cost"].get())
            tax_add = float(self.report_inputs["tax_add"].get())
            mgmt = float(self.report_inputs["mgmt_exp"].get())
            sell = float(self.report_inputs["sell_exp"].get())
            fin = float(self.report_inputs["fin_exp"].get())
            tax_exp = float(self.report_inputs["tax_exp"].get())

            # 计算
            current_assets = cash + ar + inv
            non_current_assets = fa - dep
            total_assets = current_assets + non_current_assets

            total_liab = short_loan + ap
            total_equity = capital + reserve + retained

            gross_profit = revenue - cost
            op_profit = gross_profit - tax_add - mgmt - sell - fin
            net_profit = op_profit - tax_exp

            # 生成报表
            self.report_text.delete("1.0", "end")
            
            # 资产负债表
            self.report_text.insert("end", "="*55 + "\n")
            self.report_text.insert("end", f"{'资产负债表':^55}\n")
            self.report_text.insert("end", "="*55 + "\n\n")
            
            self.report_text.insert("end", "【资产】\n")
            self.report_text.insert("end", f"  流动资产：\n")
            self.report_text.insert("end", f"    货币资金：{cash:>15,.2f}  短期借款：{short_loan:>15,.2f}\n")
            self.report_text.insert("end", f"    应收账款：{ar:>15,.2f}  应付账款：{ap:>15,.2f}\n")
            self.report_text.insert("end", f"    存    货：{inv:>15,.2f}\n")
            self.report_text.insert("end", f"  流动资产合计：{current_assets:>13,.2f}  流动负债合计：{total_liab:>13,.2f}\n\n")
            
            self.report_text.insert("end", f"  非流动资产：\n")
            self.report_text.insert("end", f"    固定资产净值：{fa-dep:>13,.2f}\n")
            self.report_text.insert("end", f"  非流动资产合计：{non_current_assets:>11,.2f}\n\n")
            
            self.report_text.insert("end", f"  资产总计：{total_assets:>15,.2f}  所有者权益合计：{total_equity:>13,.2f}\n")
            self.report_text.insert("end", "="*55 + "\n\n")

            # 利润表
            self.report_text.insert("end", "="*55 + "\n")
            self.report_text.insert("end", f"{'利润表':^55}\n")
            self.report_text.insert("end", "="*55 + "\n\n")
            
            self.report_text.insert("end", f"  一、营业收入：{revenue:>18,.2f}\n")
            self.report_text.insert("end", f"    减：营业成本：{cost:>16,.2f}\n")
            self.report_text.insert("end", f"        税金及附加：{tax_add:>12,.2f}\n")
            self.report_text.insert("end", f"        销售费用：{sell:>14,.2f}\n")
            self.report_text.insert("end", f"        管理费用：{mgmt:>14,.2f}\n")
            self.report_text.insert("end", f"        财务费用：{fin:>14,.2f}\n")
            self.report_text.insert("end", f"  二、营业利润：{op_profit:>18,.2f}\n")
            self.report_text.insert("end", f"    减：所得税费用：{tax_exp:>14,.2f}\n")
            self.report_text.insert("end", f"  三、净利润：{net_profit:>20,.2f}\n")
            self.report_text.insert("end", "="*55 + "\n")

        except ValueError:
            messagebox.showerror("错误", "请输入有效数字！")

    # ===================== 6. 成本核算仿真 =====================
    def build_cost_page(self):
        page = ttk.Frame(self.notebook)
        self.notebook.add(page, text="成本核算仿真")

        left = tk.Frame(page, padx=20, pady=20)
        left.pack(side="left", fill="y")

        tk.Label(left, text="品种法成本计算", font=("微软雅黑", 12, "bold")).pack(anchor="w", pady=(0,10))

        self.cost_inputs = {}
        items = [
            ("本月直接材料(元)", "material", "80000"),
            ("本月直接人工(元)", "labor", "50000"),
            ("本月制造费用(元)", "overhead", "30000"),
            ("月初在产品成本(元)", "begin_wip", "20000"),
            ("本月完工产品数量(件)", "finish_qty", "1000"),
            ("月末在产品数量(件)", "wip_qty", "200"),
            ("在产品完工程度(%)", "completion", "50"),
        ]
        for label, key, default in items:
            row = tk.Frame(left)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, width=18, anchor="w").pack(side="left")
            entry = tk.Entry(row, width=12)
            entry.insert(0, default)
            entry.pack(side="right")
            self.cost_inputs[key] = entry

        tk.Button(left, text="计算完工产品成本", command=self.calc_cost,
                  width=20, bg="#7c3aed", fg="white").pack(pady=15)

        self.cost_result = tk.Text(left, width=38, height=16, font=("微软雅黑", 10))
        self.cost_result.pack(pady=5)

        # 右侧成本构成图
        self.cost_fig = plt.Figure(figsize=(6, 5), dpi=100)
        self.cost_canvas = FigureCanvasTkAgg(self.cost_fig, master=page)
        self.cost_canvas.get_tk_widget().pack(side="right", padx=10, pady=10)
        self.calc_cost()

    def calc_cost(self):
        try:
            material = float(self.cost_inputs["material"].get())
            labor = float(self.cost_inputs["labor"].get())
            overhead = float(self.cost_inputs["overhead"].get())
            begin_wip = float(self.cost_inputs["begin_wip"].get())
            finish_qty = int(self.cost_inputs["finish_qty"].get())
            wip_qty = int(self.cost_inputs["wip_qty"].get())
            completion = float(self.cost_inputs["completion"].get())/100

            # 约当产量
            equivalent_qty = finish_qty + wip_qty * completion
            # 生产费用合计
            total_cost = begin_wip + material + labor + overhead
            # 单位成本
            unit_cost = total_cost / equivalent_qty
            # 完工产品成本
            finish_cost = finish_qty * unit_cost
            # 在产品成本
            wip_cost = wip_qty * completion * unit_cost

            self.cost_result.delete("1.0", "end")
            result = f"""
【成本计算单】
月初在产品成本：  {begin_wip:,.2f} 元
本月生产费用：    {material+labor+overhead:,.2f} 元
  直接材料：      {material:,.2f} 元
  直接人工：      {labor:,.2f} 元
  制造费用：      {overhead:,.2f} 元
生产费用合计：    {total_cost:,.2f} 元

【产量计算】
完工产品数量：  {finish_qty} 件
在产品约当产量：{wip_qty * completion:.0f} 件
约当总产量：    {equivalent_qty:.0f} 件

【成本分配】
单位成本：      {unit_cost:.2f} 元/件
完工产品总成本：{finish_cost:,.2f} 元
月末在产品成本：{wip_cost:,.2f} 元

完工产品单位成本：
  直接材料：{material/equivalent_qty:.2f} 元
  直接人工：{labor/equivalent_qty:.2f} 元
  制造费用：{overhead/equivalent_qty:.2f} 元
"""
            self.cost_result.insert("end", result)

            # 成本构成饼图
            self.cost_fig.clear()
            ax = self.cost_fig.add_subplot(111)
            items = ["直接材料", "直接人工", "制造费用", "月初在产品"]
            values = [material, labor, overhead, begin_wip]
            colors = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444"]
            ax.pie(values, labels=items, autopct="%1.1f%%", colors=colors, startangle=90)
            ax.set_title("完工产品成本构成")
            self.cost_canvas.draw()

        except ValueError:
            messagebox.showerror("错误", "请输入有效数字！")

    # ===================== 7. 折旧摊销计算 =====================
    def build_depreciation_page(self):
        page = ttk.Frame(self.notebook)
        self.notebook.add(page, text="折旧摊销计算")

        left = tk.Frame(page, padx=20, pady=20)
        left.pack(side="left", fill="y")

        tk.Label(left, text="固定资产折旧计算", font=("微软雅黑", 12, "bold")).pack(anchor="w", pady=(0,10))

        self.dep_inputs = {}
        items = [
            ("固定资产原值(元)", "cost", "100000"),
            ("预计净残值(元)", "salvage", "5000"),
            ("预计使用年限(年)", "years", "5"),
        ]
        for label, key, default in items:
            row = tk.Frame(left)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, width=18, anchor="w").pack(side="left")
            entry = tk.Entry(row, width=12)
            entry.insert(0, default)
            entry.pack(side="right")
            self.dep_inputs[key] = entry

        tk.Button(left, text="计算三种方法对比", command=self.calc_depreciation,
                  width=20, bg="#0ea5e9", fg="white").pack(pady=15)

        self.dep_result = tk.Text(left, width=38, height=16, font=("微软雅黑", 10))
        self.dep_result.pack(pady=5)

        # 右侧折旧曲线对比图
        self.dep_fig = plt.Figure(figsize=(6, 5), dpi=100)
        self.dep_canvas = FigureCanvasTkAgg(self.dep_fig, master=page)
        self.dep_canvas.get_tk_widget().pack(side="right", padx=10, pady=10)
        self.calc_depreciation()

    def calc_depreciation(self):
        try:
            cost = float(self.dep_inputs["cost"].get())
            salvage = float(self.dep_inputs["salvage"].get())
            years = int(self.dep_inputs["years"].get())
            depreciable = cost - salvage

            # 1.直线法
            straight = [depreciable / years] * years

            # 2.双倍余额递减法
            double_rate = 2 / years
            double = []
            carry = cost
            for i in range(years):
                if i < years - 2:
                    d = carry * double_rate
                else:
                    d = (carry - salvage) / 2
                double.append(d)
                carry -= d

            # 3.年数总和法
            sum_years = years * (years + 1) / 2
            sum_year = []
            for i in range(years):
                d = depreciable * (years - i) / sum_years
                sum_year.append(d)

            self.dep_result.delete("1.0", "end")
            result = f"""
【折旧方法对比】
原值：{cost:,.2f} 元  净残值：{salvage:,.2f} 元  年限：{years}年

【年折旧额对比】
年份  直线法      双倍余额递减  年数总和法
"""
            for i in range(years):
                result += f" {i+1:2d}   {straight[i]:>8,.2f}   {double[i]:>8,.2f}   {sum_year[i]:>8,.2f}\n"

            result += f"""
年折旧额合计：
直线法：{sum(straight):,.2f} 元
双倍余额递减法：{sum(double):,.2f} 元
年数总和法：{sum(sum_year):,.2f} 元
"""
            self.dep_result.insert("end", result)

            # 折旧曲线对比
            self.dep_fig.clear()
            ax = self.dep_fig.add_subplot(111)
            x = np.arange(1, years+1)
            ax.plot(x, straight, marker="o", label="直线法", linewidth=2)
            ax.plot(x, double, marker="s", label="双倍余额递减法", linewidth=2)
            ax.plot(x, sum_year, marker="^", label="年数总和法", linewidth=2)
            
            ax.set_xlabel("年份")
            ax.set_ylabel("年折旧额(元)")
            ax.set_title("三种折旧方法年折旧额对比")
            ax.legend()
            ax.grid(alpha=0.3)
            self.dep_canvas.draw()

        except ValueError:
            messagebox.showerror("错误", "请输入有效数字！")

    # ===================== 8. 会计章节题库 =====================
    def build_exam_page(self):
        page = ttk.Frame(self.notebook)
        self.notebook.add(page, text="会计章节题库")

        left = tk.Frame(page, padx=20, pady=20)
        left.pack(side="left", fill="y")

        tk.Label(left, text="会计基础习题", font=("微软雅黑", 12, "bold")).pack(anchor="w", pady=(0,10))

        # 内置题库
        self.question_bank = [
            {"chapter": "基础会计", "q": "会计的基本职能是：",
             "options": ["A.核算和监督", "B.预测和决策", "C.控制和分析", "D.核算和决策"],
             "answer": "A"},
            {"chapter": "基础会计", "q": "下列各项中，属于流动资产的是：",
             "options": ["A.固定资产", "B.应收账款", "C.无形资产", "D.长期股权投资"],
             "answer": "B"},
            {"chapter": "基础会计", "q": "借贷记账法下，负债类账户的结构是：",
             "options": ["A.借方记增加，贷方记减少", "B.贷方记增加，借方记减少",
                        "C.借方记增加，贷方记增加", "D.贷方记减少，借方记减少"],
             "answer": "B"},
            {"chapter": "财务会计", "q": "下列各项中，应计入存货成本的是：",
             "options": ["A.非正常消耗的直接材料", "B.采购入库后的仓储费用",
                        "C.生产过程中为达到下一个生产阶段所必需的仓储费用", "D.不能归属于使存货达到目前场所的其他支出"],
             "answer": "C"},
            {"chapter": "财务会计", "q": "交易性金融资产的交易费用计入：",
             "options": ["A.初始成本", "B.投资收益", "C.财务费用", "D.管理费用"],
             "answer": "B"},
            {"chapter": "财务会计", "q": "下列各项中，属于收入准则确认的收入是：",
             "options": ["A.出售固定资产净收益", "B.出售无形资产净收益",
                        "C.销售商品收入", "D.接受捐赠收入"],
             "answer": "C"},
            {"chapter": "成本会计", "q": "下列各项中，属于产品成本项目的是：",
             "options": ["A.管理费用", "B.制造费用", "C.销售费用", "D.财务费用"],
             "answer": "B"},
            {"chapter": "成本会计", "q": "品种法适用于：",
             "options": ["A.大量大批单步骤生产", "B.单件小批生产",
                        "C.大量大批多步骤生产", "D.分批生产"],
             "answer": "A"}
        ]

        self.current_q = 0
        self.q_var = tk.StringVar()

        self.q_chapter = tk.Label(left, text="", font=("微软雅黑", 10), fg="#666")
        self.q_chapter.pack(anchor="w")

        self.q_text = tk.Label(left, text="", font=("微软雅黑", 10, "bold"), wraplength=300, justify="left")
        self.q_text.pack(pady=8, anchor="w")

        self.q_opts = []
        for i in range(4):
            rb = tk.Radiobutton(left, text="", variable=self.q_var, value=chr(65+i), anchor="w")
            rb.pack(fill="x", pady=2)
            self.q_opts.append(rb)

        btn_row = tk.Frame(left)
        btn_row.pack(pady=15)
        tk.Button(btn_row, text="提交答案", command=self.check_question, width=10, bg="#0a8f4a", fg="white").pack(side="left", padx=3)
        tk.Button(btn_row, text="下一题", command=self.next_question, width=10, bg="#1a56db", fg="white").pack(side="left", padx=3)

        tk.Button(left, text="📥 导入Excel题库", command=self.import_excel_bank,
                  width=22, bg="#229954", fg="white").pack(pady=3)

        self.q_result = tk.Label(left, text="", font=("微软雅黑", 11, "bold"))
        self.q_result.pack(pady=5)

        # 右侧章节正确率
        self.exam_fig = plt.Figure(figsize=(6, 5), dpi=100)
        self.exam_canvas = FigureCanvasTkAgg(self.exam_fig, master=page)
        self.exam_canvas.get_tk_widget().pack(side="right", padx=10, pady=10)

        self.chapter_correct = {}
        self.chapter_total = {}
        self.load_question()
        self.update_exam_chart()

    def import_excel_bank(self):
        fp = filedialog.askopenfilename(filetypes=[("Excel题库", "*.xlsx")])
        if not fp:
            return
        try:
            wb = openpyxl.load_workbook(fp, data_only=True)
            ws = wb.active
            add_count = 0
            for row in ws.iter_rows(min_row=2, values_only=True):
                if len(row) < 7:
                    continue
                chapter, q, a, b, c, d, answer = row[:7]
                if not chapter or not q:
                    continue
                self.question_bank.append({
                    "chapter": str(chapter).strip(),
                    "q": str(q).strip(),
                    "options": [str(a).strip(), str(b).strip(), str(c).strip(), str(d).strip()],
                    "answer": str(answer).strip().upper()
                })
                add_count += 1
            messagebox.showinfo("导入成功", f"成功导入 {add_count} 道题目！\n当前总量：{len(self.question_bank)} 道")
            self.load_question()
            self.update_exam_chart()
        except Exception as e:
            messagebox.showerror("失败", f"格式错误：{str(e)}\n格式：A列章节 B列题目 C-F选项 G答案")

    def load_question(self):
        q = self.question_bank[self.current_q]
        self.q_chapter.config(text=f"章节：{q['chapter']}  （第{self.current_q+1}/{len(self.question_bank)}题）")
        self.q_text.config(text=q["q"])
        for i, opt in enumerate(q["options"]):
            self.q_opts[i].config(text=opt)
        self.q_var.set("")
        self.q_result.config(text="")

    def check_question(self):
        if not self.q_var.get():
            messagebox.showwarning("提示", "请先选择答案！")
            return
        q = self.question_bank[self.current_q]
        ch = q["chapter"]
        self.chapter_total[ch] = self.chapter_total.get(ch, 0) + 1
        self.study_data["done_questions"] += 1

        if self.q_var.get() == q["answer"]:
            self.chapter_correct[ch] = self.chapter_correct.get(ch, 0) + 1
            self.q_result.config(text="✅ 回答正确", fg="#0a8f4a")
            self.study_data["correct_questions"] += 1
        else:
            self.q_result.config(text=f"❌ 正确答案：{q['answer']}", fg="#d92d20")

        self.update_exam_chart()

    def next_question(self):
        self.current_q = (self.current_q + 1) % len(self.question_bank)
        self.load_question()

    def update_exam_chart(self):
        self.exam_fig.clear()
        ax = self.exam_fig.add_subplot(111)
        chapters = list(set(q["chapter"] for q in self.question_bank))
        rates = []
        for ch in chapters:
            total = self.chapter_total.get(ch, 0)
            correct = self.chapter_correct.get(ch, 0)
            rate = correct/total*100 if total > 0 else 0
            rates.append(rate)
            self.study_data["chapter_scores"][ch] = rate

        bars = ax.bar(chapters, rates, color=["#3b82f6", "#10b981", "#f59e0b", "#ef4444"])
        for bar, val in zip(bars, rates):
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+1, f"{val:.0f}%", ha="center")
        ax.set_title(f"各章节正确率（共{len(self.question_bank)}题）")
        ax.set_ylabel("正确率(%)")
        ax.set_ylim(0, 100)
        ax.grid(axis="y", alpha=0.3)
        self.exam_canvas.draw()

    # ===================== 9. 学习数据可视化 =====================
    def build_analysis_page(self):
        page = ttk.Frame(self.notebook)
        self.notebook.add(page, text="学习数据分析")

        left = tk.Frame(page, padx=20, pady=20)
        left.pack(side="left", fill="y")

        tk.Label(left, text="学习数据总览", font=("微软雅黑", 12, "bold")).pack(anchor="w", pady=(0,10))

        self.stats_text = tk.Text(left, width=30, height=16, font=("微软雅黑", 10))
        self.stats_text.pack(pady=5)

        tk.Button(left, text="刷新数据", command=self.refresh_stats, width=18, bg="#1a56db", fg="white").pack(pady=10)

        # 右侧章节掌握度雷达图
        self.analysis_fig = plt.Figure(figsize=(6, 5), dpi=100)
        self.analysis_canvas = FigureCanvasTkAgg(self.analysis_fig, master=page)
        self.analysis_canvas.get_tk_widget().pack(side="right", padx=10, pady=10)
        self.refresh_stats()

    def refresh_stats(self):
        scores = self.study_data["chapter_scores"]
        done = self.study_data["done_questions"]
        correct = self.study_data["correct_questions"]
        total_rate = correct/done*100 if done > 0 else 0

        stats = f"""
【会计学习统计】

已完成题目：{done} 道
正确题目：  {correct} 道
总正确率：  {total_rate:.1f}%

【章节掌握度】
"""
        for ch, rate in scores.items():
            stats += f"  {ch}：{rate:.1f}%\n"

        avg = sum(scores.values())/len(scores) if scores else 0
        stats += f"\n综合掌握度：{avg:.1f} 分"
        
        self.stats_text.delete("1.0", "end")
        self.stats_text.insert("end", stats)

        # 雷达图
        self.analysis_fig.clear()
        ax = self.analysis_fig.add_subplot(111, polar=True)
        categories = list(scores.keys())
        values = list(scores.values())
        if not categories:
            ax.text(0.5, 0.5, "暂无答题数据", ha="center", va="center", transform=ax.transAxes)
        else:
            values += values[:1]
            angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False)
            angles = np.append(angles, angles[0])

            ax.plot(angles, values, 'o-', color="#1a56db", linewidth=2)
            ax.fill(angles, values, alpha=0.25, color="#1a56db")
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories)
            ax.set_ylim(0, 100)
            ax.set_title("会计章节掌握度雷达图", pad=15, fontsize=12)
        self.analysis_canvas.draw()


if __name__ == "__main__":
    app = AccountingSystem()
    app.mainloop()
