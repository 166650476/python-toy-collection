import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import openpyxl

# 中文显示配置
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False


class CPAAccountingSim(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CPA会计科目仿真综合展示系统")
        self.geometry("1280x780")
        self.resizable(False, False)

        # 顶部标题
        tk.Label(self, text="CPA《会计》科目仿真综合工具",
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

        # 7大核心模块
        self.build_entry_page()       # 1.会计分录仿真系统
        self.build_taccount_page()    # 2.T型账与科目汇总
        self.build_report_page()      # 3.财务报表生成
        self.build_tax_page()         # 4.所得税会计仿真
        self.build_lease_page()       # 5.租赁负债计算
        self.build_exam_page()        # 6.会计章节题库
        self.build_analysis_page()    # 7.学习数据可视化

    # ===================== 1. 会计分录仿真系统 =====================
    def build_entry_page(self):
        page = ttk.Frame(self.notebook)
        self.notebook.add(page, text="会计分录仿真")

        left = tk.Frame(page, padx=20, pady=20)
        left.pack(side="left", fill="y")

        tk.Label(left, text="CPA会计高频业务（准则版）", font=("微软雅黑", 12, "bold")).pack(anchor="w", pady=(0,10))

        self.biz_type = ttk.Combobox(left, state="readonly", width=28, values=[
            "交易性金融资产购入",
            "债权投资-利息调整摊销",
            "其他权益工具投资公允价值变动",
            "长期股权投资权益法-确认投资收益",
            "长期股权投资权益法-其他综合收益",
            "收入确认-五步法（赊销）",
            "存货跌价准备计提",
            "固定资产减值计提",
            "无形资产摊销",
            "股份支付-权益结算",
            "计提法定盈余公积",
            "合并报表-内部存货交易抵消"
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
            "交易性金融资产购入": [("成本(元)", "cost", "100000"), ("交易费用(元)", "fee", "5000")],
            "债权投资-利息调整摊销": [("面值(元)", "face", "100000"), ("票面利率(%)", "coupon", "5"),
                                      ("实际利率(%)", "eff", "6"), ("期初摊余成本(元)", "carry", "98000")],
            "其他权益工具投资公允价值变动": [("账面价值(元)", "book", "80000"), ("公允价值(元)", "fair", "85000")],
            "长期股权投资权益法-确认投资收益": [("被投资方净利润(元)", "profit", "200000"), ("持股比例(%)", "rate", "30")],
            "长期股权投资权益法-其他综合收益": [("被投资方其他综合收益(元)", "oci", "50000"), ("持股比例(%)", "rate", "30")],
            "收入确认-五步法（赊销）": [("不含税收入(元)", "revenue", "200000"), ("增值税率(%)", "tax_rate", "13")],
            "存货跌价准备计提": [("存货成本(元)", "cost", "150000"), ("可变现净值(元)", "nrv", "120000")],
            "固定资产减值计提": [("账面价值(元)", "book", "300000"), ("可收回金额(元)", "recover", "240000")],
            "无形资产摊销": [("原值(元)", "cost", "120000"), ("月摊销额(元)", "amort", "1000")],
            "股份支付-权益结算": [("授予日公允价值(元)", "fair", "100000"), ("等待期年数", "period", "3")],
            "计提法定盈余公积": [("净利润(元)", "profit", "500000"), ("提取比例(%)", "rate", "10")],
            "合并报表-内部存货交易抵消": [("内部销售收入(元)", "sales", "100000"), ("销售成本(元)", "cost", "80000"),
                                      ("期末未实现内部销售利润(元)", "unreal", "20000")]
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
            if biz == "交易性金融资产购入":
                cost = float(self.entry_params["cost"].get())
                fee = float(self.entry_params["fee"].get())
                entries = [
                    ("借：交易性金融资产-成本", cost),
                    ("借：投资收益", fee),
                    ("贷：银行存款", cost + fee)
                ]
                amounts = {"交易性金融资产": cost, "投资收益": fee, "银行存款": cost+fee}

            elif biz == "债权投资-利息调整摊销":
                face = float(self.entry_params["face"].get())
                coupon = float(self.entry_params["coupon"].get())/100
                eff = float(self.entry_params["eff"].get())/100
                carry = float(self.entry_params["carry"].get())
                interest_income = carry * eff
                coupon_interest = face * coupon
                adjust = interest_income - coupon_interest
                entries = [
                    ("借：应收利息", coupon_interest),
                    ("借：债权投资-利息调整", adjust),
                    ("贷：投资收益", interest_income)
                ]
                amounts = {"应收利息": coupon_interest, "债权投资-利息调整": adjust, "投资收益": interest_income}

            elif biz == "其他权益工具投资公允价值变动":
                book = float(self.entry_params["book"].get())
                fair = float(self.entry_params["fair"].get())
                diff = fair - book
                entries = [
                    ("借：其他权益工具投资-公允价值变动", diff),
                    ("贷：其他综合收益", diff)
                ]
                amounts = {"其他权益工具投资": diff, "其他综合收益": diff}

            elif biz == "长期股权投资权益法-确认投资收益":
                profit = float(self.entry_params["profit"].get())
                rate = float(self.entry_params["rate"].get())/100
                invest = profit * rate
                entries = [
                    ("借：长期股权投资-损益调整", invest),
                    ("贷：投资收益", invest)
                ]
                amounts = {"长期股权投资": invest, "投资收益": invest}

            elif biz == "长期股权投资权益法-其他综合收益":
                oci = float(self.entry_params["oci"].get())
                rate = float(self.entry_params["rate"].get())/100
                share = oci * rate
                entries = [
                    ("借：长期股权投资-其他综合收益", share),
                    ("贷：其他综合收益", share)
                ]
                amounts = {"长期股权投资": share, "其他综合收益": share}

            elif biz == "收入确认-五步法（赊销）":
                revenue = float(self.entry_params["revenue"].get())
                tax_rate = float(self.entry_params["tax_rate"].get())/100
                tax = revenue * tax_rate
                entries = [
                    ("借：应收账款", revenue + tax),
                    ("贷：主营业务收入", revenue),
                    ("贷：应交税费-应交增值税(销项)", tax)
                ]
                amounts = {"应收账款": revenue+tax, "主营业务收入": revenue, "应交税费": tax}

            elif biz == "存货跌价准备计提":
                cost = float(self.entry_params["cost"].get())
                nrv = float(self.entry_params["nrv"].get())
                loss = cost - nrv
                if loss <= 0:
                    messagebox.showinfo("提示", "可变现净值高于成本，无需计提减值")
                    return
                entries = [
                    ("借：资产减值损失", loss),
                    ("贷：存货跌价准备", loss)
                ]
                amounts = {"资产减值损失": loss, "存货跌价准备": loss}

            elif biz == "固定资产减值计提":
                book = float(self.entry_params["book"].get())
                recover = float(self.entry_params["recover"].get())
                loss = book - recover
                if loss <= 0:
                    messagebox.showinfo("提示", "未发生减值")
                    return
                entries = [
                    ("借：资产减值损失", loss),
                    ("贷：固定资产减值准备", loss)
                ]
                amounts = {"资产减值损失": loss, "固定资产减值准备": loss}

            elif biz == "无形资产摊销":
                amort = float(self.entry_params["amort"].get())
                entries = [
                    ("借：管理费用", amort),
                    ("贷：累计摊销", amort)
                ]
                amounts = {"管理费用": amort, "累计摊销": amort}

            elif biz == "股份支付-权益结算":
                fair = float(self.entry_params["fair"].get())
                period = int(self.entry_params["period"].get())
                annual_expense = fair / period
                entries = [
                    ("借：管理费用", annual_expense),
                    ("贷：资本公积-其他资本公积", annual_expense)
                ]
                amounts = {"管理费用": annual_expense, "资本公积": annual_expense}

            elif biz == "计提法定盈余公积":
                profit = float(self.entry_params["profit"].get())
                rate = float(self.entry_params["rate"].get())/100
                reserve = profit * rate
                entries = [
                    ("借：利润分配-提取法定盈余公积", reserve),
                    ("贷：盈余公积-法定盈余公积", reserve)
                ]
                amounts = {"利润分配": reserve, "盈余公积": reserve}

            elif biz == "合并报表-内部存货交易抵消":
                sales = float(self.entry_params["sales"].get())
                cost = float(self.entry_params["cost"].get())
                unreal = float(self.entry_params["unreal"].get())
                entries = [
                    ("借：营业收入", sales),
                    ("贷：营业成本", sales - unreal),
                    ("贷：存货", unreal)
                ]
                amounts = {"营业收入": -sales, "营业成本": -(sales-unreal), "存货": -unreal}

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
应收账款,226000,0
主营业务收入,0,200000
应交税费,0,26000
库存商品,80000,0
主营业务成本,80000,0""")
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

    # ===================== 3. 财务报表生成 =====================
    def build_report_page(self):
        page = ttk.Frame(self.notebook)
        self.notebook.add(page, text="财务报表生成")

        left = tk.Frame(page, padx=20, pady=20)
        left.pack(side="left", fill="y")

        tk.Label(left, text="科目期末余额（元）", font=("微软雅黑", 12, "bold")).pack(anchor="w", pady=(0,10))

        self.report_inputs = {}
        items = [
            ("货币资金", "cash", "500000"),
            ("应收账款", "ar", "300000"),
            ("存货", "inventory", "400000"),
            ("固定资产", "fa", "1000000"),
            ("累计折旧", "dep", "200000"),
            ("无形资产", "ia", "200000"),
            ("短期借款", "short_loan", "300000"),
            ("应付账款", "ap", "250000"),
            ("长期借款", "long_loan", "400000"),
            ("实收资本", "capital", "800000"),
            ("盈余公积", "reserve", "100000"),
            ("未分配利润", "retained", "350000"),
            ("营业收入", "revenue", "2000000"),
            ("营业成本", "cost", "1200000"),
            ("税金及附加", "tax_add", "20000"),
            ("管理费用", "mgmt_exp", "150000"),
            ("销售费用", "sell_exp", "100000"),
            ("财务费用", "fin_exp", "50000"),
            ("所得税费用", "tax_exp", "120000"),
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
            ia = float(self.report_inputs["ia"].get())
            short_loan = float(self.report_inputs["short_loan"].get())
            ap = float(self.report_inputs["ap"].get())
            long_loan = float(self.report_inputs["long_loan"].get())
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
            non_current_assets = (fa - dep) + ia
            total_assets = current_assets + non_current_assets

            current_liab = short_loan + ap
            total_liab = current_liab + long_loan
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
            self.report_text.insert("end", f"  流动资产合计：{current_assets:>13,.2f}  流动负债合计：{current_liab:>13,.2f}\n\n")
            
            self.report_text.insert("end", f"  非流动资产：\n")
            self.report_text.insert("end", f"    固定资产净值：{fa-dep:>13,.2f}  长期借款：{long_loan:>15,.2f}\n")
            self.report_text.insert("end", f"    无形资产：{ia:>15,.2f}\n")
            self.report_text.insert("end", f"  非流动资产合计：{non_current_assets:>11,.2f}  负债合计：{total_liab:>15,.2f}\n\n")
            
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

    # ===================== 4. 所得税会计仿真 =====================
    def build_tax_page(self):
        page = ttk.Frame(self.notebook)
        self.notebook.add(page, text="所得税会计")

        left = tk.Frame(page, padx=20, pady=20)
        left.pack(side="left", fill="y")

        tk.Label(left, text="所得税会计参数", font=("微软雅黑", 12, "bold")).pack(anchor="w", pady=(0,10))

        self.tax_inputs = {}
        items = [
            ("税前会计利润(元)", "profit", "1000000"),
            ("所得税税率(%)", "rate", "25"),
            ("可抵扣暂时性差异(元)", "deductible", "200000"),
            ("应纳税暂时性差异(元)", "taxable", "100000"),
            ("国债利息收入(元)", "gov_interest", "50000"),
            ("税收滞纳金(元)", "penalty", "30000"),
        ]
        for label, key, default in items:
            row = tk.Frame(left)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, width=18, anchor="w").pack(side="left")
            entry = tk.Entry(row, width=12)
            entry.insert(0, default)
            entry.pack(side="right")
            self.tax_inputs[key] = entry

        tk.Button(left, text="计算所得税费用", command=self.calc_income_tax,
                  width=20, bg="#be123c", fg="white").pack(pady=15)

        self.tax_result = tk.Text(left, width=38, height=16, font=("微软雅黑", 10))
        self.tax_result.pack(pady=5)

        # 右侧递延所得税构成图
        self.tax_fig = plt.Figure(figsize=(6, 5), dpi=100)
        self.tax_canvas = FigureCanvasTkAgg(self.tax_fig, master=page)
        self.tax_canvas.get_tk_widget().pack(side="right", padx=10, pady=10)
        self.calc_income_tax()

    def calc_income_tax(self):
        try:
            profit = float(self.tax_inputs["profit"].get())
            rate = float(self.tax_inputs["rate"].get())/100
            deductible = float(self.tax_inputs["deductible"].get())
            taxable = float(self.tax_inputs["taxable"].get())
            gov_int = float(self.tax_inputs["gov_interest"].get())
            penalty = float(self.tax_inputs["penalty"].get())

            # 应纳税所得额
            taxable_income = profit - gov_int + penalty + deductible - taxable
            # 当期应交所得税
            current_tax = taxable_income * rate
            # 递延所得税
            dta = deductible * rate  # 递延所得税资产
            dtl = taxable * rate     # 递延所得税负债
            deferred_tax_expense = dtl - dta
            # 所得税费用
            income_tax_expense = current_tax + deferred_tax_expense

            self.tax_result.delete("1.0", "end")
            result = f"""
【所得税费用计算】
税前会计利润：  {profit:,.2f} 元

【纳税调整】
加：税收滞纳金：    {penalty:,.2f}
    可抵扣暂时性差异：{deductible:,.2f}
减：国债利息收入：  {gov_int:,.2f}
    应纳税暂时性差异：{taxable:,.2f}

应纳税所得额：  {taxable_income:,.2f} 元
当期应交所得税：{current_tax:,.2f} 元

【递延所得税】
递延所得税资产：{dta:,.2f} 元
递延所得税负债：{dtl:,.2f} 元
递延所得税费用：{deferred_tax_expense:,.2f} 元

【所得税费用】
所得税费用总额：{income_tax_expense:,.2f} 元

分录：
借：所得税费用        {income_tax_expense:,.2f}
    递延所得税资产      {dta:,.2f}
  贷：应交税费-应交所得税 {current_tax:,.2f}
      递延所得税负债      {dtl:,.2f}
"""
            self.tax_result.insert("end", result)

            # 图表
            self.tax_fig.clear()
            ax = self.tax_fig.add_subplot(111)
            items = ["当期应交所得税", "递延所得税资产", "递延所得税负债", "所得税费用"]
            values = [current_tax, dta, dtl, income_tax_expense]
            colors = ["#ef4444", "#3b82f6", "#10b981", "#f59e0b"]
            bars = ax.bar(items, values, color=colors)
            for bar, val in zip(bars, values):
                ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+max(values)*0.01,
                        f"{val:,.0f}", ha="center", fontsize=9)
            ax.set_title("所得税费用构成")
            ax.set_ylabel("金额(元)")
            ax.grid(axis="y", alpha=0.3)
            plt.setp(ax.get_xticklabels(), rotation=10)
            self.tax_canvas.draw()

        except ValueError:
            messagebox.showerror("错误", "请输入有效数字！")

    # ===================== 5. 租赁负债计算（新租赁准则） =====================
    def build_lease_page(self):
        page = ttk.Frame(self.notebook)
        self.notebook.add(page, text="租赁负债计算")

        left = tk.Frame(page, padx=20, pady=20)
        left.pack(side="left", fill="y")

        tk.Label(left, text="承租人租赁会计（新准则）", font=("微软雅黑", 12, "bold")).pack(anchor="w", pady=(0,10))

        self.lease_inputs = {}
        items = [
            ("年租金(元)", "payment", "100000"),
            ("租赁期(年)", "term", "5"),
            ("增量借款利率(%)", "rate", "6"),
            ("初始直接费用(元)", "initial_cost", "5000"),
        ]
        for label, key, default in items:
            row = tk.Frame(left)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, width=18, anchor="w").pack(side="left")
            entry = tk.Entry(row, width=12)
            entry.insert(0, default)
            entry.pack(side="right")
            self.lease_inputs[key] = entry

        tk.Button(left, text="计算使用权资产与摊销", command=self.calc_lease,
                  width=20, bg="#7c3aed", fg="white").pack(pady=15)

        self.lease_result = tk.Text(left, width=38, height=16, font=("微软雅黑", 10))
        self.lease_result.pack(pady=5)

        # 右侧摊销曲线图
        self.lease_fig = plt.Figure(figsize=(6, 5), dpi=100)
        self.lease_canvas = FigureCanvasTkAgg(self.lease_fig, master=page)
        self.lease_canvas.get_tk_widget().pack(side="right", padx=10, pady=10)
        self.calc_lease()

    def calc_lease(self):
        try:
            payment = float(self.lease_inputs["payment"].get())
            term = int(self.lease_inputs["term"].get())
            rate = float(self.lease_inputs["rate"].get())/100
            initial = float(self.lease_inputs["initial_cost"].get())

            # 租赁负债现值（普通年金现值）
            lease_liability = payment * (1 - (1+rate)**(-term)) / rate
            # 使用权资产
            right_of_use_asset = lease_liability + initial
            # 未确认融资费用
            unrecognized = payment * term - lease_liability

            # 摊销表
            amort_schedule = []
            carrying = lease_liability
            for year in range(1, term+1):
                interest = carrying * rate
                principal = payment - interest
                carrying -= principal
                amort_schedule.append((year, payment, interest, principal, carrying))

            self.lease_result.delete("1.0", "end")
            result = f"""
【租赁初始计量】
租赁付款额总额：  {payment*term:,.2f} 元
租赁负债现值：    {lease_liability:,.2f} 元
未确认融资费用：  {unrecognized:,.2f} 元
初始直接费用：    {initial:,.2f} 元
使用权资产成本：  {right_of_use_asset:,.2f} 元

【租赁期摊销表】
年期  支付租金   利息费用   本金偿还   期末负债
"""
            for year, pay, int_, prin, carry in amort_schedule:
                result += f" {year:2d}   {pay:>8,.0f}   {int_:>8,.0f}   {prin:>8,.0f}   {carry:>8,.0f}\n"

            result += f"""
初始确认分录：
借：使用权资产        {right_of_use_asset:,.2f}
    租赁负债-未确认融资费用 {unrecognized:,.2f}
  贷：租赁负债-租赁付款额 {payment*term:,.2f}
      银行存款            {initial:,.2f}
"""
            self.lease_result.insert("end", result)

            # 摊销曲线图
            self.lease_fig.clear()
            ax = self.lease_fig.add_subplot(111)
            years = [0] + [s[0] for s in amort_schedule]
            liabilities = [lease_liability] + [s[4] for s in amort_schedule]
            interests = [0] + [s[2] for s in amort_schedule]

            ax.plot(years, liabilities, marker="o", label="租赁负债余额", linewidth=2)
            ax.plot(years, np.cumsum(interests), marker="s", label="累计利息费用", linewidth=2)
            
            ax.set_xlabel("年份")
            ax.set_ylabel("金额(元)")
            ax.set_title("租赁负债摊销曲线")
            ax.legend()
            ax.grid(alpha=0.3)
            self.lease_canvas.draw()

        except ValueError:
            messagebox.showerror("错误", "请输入有效数字！")

    # ===================== 6. 会计章节题库 =====================
    def build_exam_page(self):
        page = ttk.Frame(self.notebook)
        self.notebook.add(page, text="会计章节题库")

        left = tk.Frame(page, padx=20, pady=20)
        left.pack(side="left", fill="y")

        tk.Label(left, text="CPA会计章节习题", font=("微软雅黑", 12, "bold")).pack(anchor="w", pady=(0,10))

        # 内置题库
        self.question_bank = [
            {"chapter": "总论", "q": "下列各项中，体现实质重于形式原则的是：",
             "options": ["A.计提存货跌价准备", "B.融资租入固定资产视同自有资产",
                        "C.发出存货计价方法选择", "D.交易性金融资产按公允价值计量"],
             "answer": "B"},
            {"chapter": "存货", "q": "下列各项中，不应计入存货成本的是：",
             "options": ["A.生产过程中发生的制造费用", "B.采购过程中发生的合理损耗",
                        "C.入库后发生的仓储费用", "D.为特定客户设计产品的设计费用"],
             "answer": "C"},
            {"chapter": "固定资产", "q": "下列各项中，应计提折旧的是：",
             "options": ["A.已提足折旧仍继续使用的固定资产", "B.单独计价入账的土地",
                        "C.处于更新改造过程中的固定资产", "D.未使用的厂房"],
             "answer": "D"},
            {"chapter": "金融资产", "q": "下列各项中，应当分类为以公允价值计量且其变动计入其他综合收益的是：",
             "options": ["A.交易性股票投资", "B.普通公司债券（收取本金利息）",
                        "C.非交易性权益工具投资（指定）", "D.应收账款"],
             "answer": "C"},
            {"chapter": "长期股权投资", "q": "权益法下，被投资方实现净利润，投资方应贷记：",
             "options": ["A.资本公积", "B.投资收益", "C.其他综合收益", "D.营业外收入"],
             "answer": "B"},
            {"chapter": "收入", "q": "收入确认的五步法中，第一步是：",
             "options": ["A.识别合同", "B.识别履约义务", "C.确定交易价格", "D.分摊交易价格"],
             "answer": "A"},
            {"chapter": "所得税", "q": "下列各项中，产生可抵扣暂时性差异的是：",
             "options": ["A.交易性金融资产公允价值上升", "B.计提存货跌价准备",
                        "C.国债利息收入", "D.罚款支出"],
             "answer": "B"},
            {"chapter": "合并财务报表", "q": "合并报表中，内部交易形成的存货未实现内部销售利润应：",
             "options": ["A.全额抵消", "B.按持股比例抵消", "C.无需抵消", "D.计入资本公积"],
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

        bars = ax.bar(chapters, rates, color=["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#0ea5e9"])
        for bar, val in zip(bars, rates):
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+1, f"{val:.0f}%", ha="center")
        ax.set_title(f"各章节正确率（共{len(self.question_bank)}题）")
        ax.set_ylabel("正确率(%)")
        ax.set_ylim(0, 100)
        ax.grid(axis="y", alpha=0.3)
        plt.setp(ax.get_xticklabels(), rotation=15)
        self.exam_canvas.draw()

    # ===================== 7. 学习数据可视化 =====================
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
【CPA会计学习统计】

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
            ax.set_title("CPA会计章节掌握度雷达图", pad=15, fontsize=12)
        self.analysis_canvas.draw()


if __name__ == "__main__":
    app = CPAAccountingSim()
    app.mainloop()
