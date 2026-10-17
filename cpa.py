import tkinter as tk
from tkinter import ttk, messagebox
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# 中文显示配置
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False


class CPASimulator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("注册会计师备考仿真综合展示系统")
        self.geometry("1250x780")
        self.resizable(False, False)

        # 顶部标题
        tk.Label(self, text="CPA专业阶段备考仿真综合工具",
                 font=("微软雅黑", 16, "bold"), fg="#1a56db").pack(pady=8)

        # 全局学习数据
        self.study_data = {
            "subject_scores": {"会计": 0, "审计": 0, "财管": 0, "税法": 0, "经济法": 0, "战略": 0},
            "exam_records": [],
            "done_questions": 0,
            "correct_questions": 0
        }

        # 多标签页容器
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=5)

        # 8大功能模块
        self.build_accounting_page()   # 1.会计分录仿真
        self.build_audit_page()        # 2.审计风险评估
        self.build_finance_page()      # 3.财管指标测算
        self.build_tax_page()          # 4.税法税金计算
        self.build_strategy_page()     # 5.战略SWOT分析
        self.build_exam_page()         # 6.题库模考训练
        self.build_plan_page()         # 7.备考计划生成
        self.build_analysis_page()     # 8.学习数据可视化

    # ===================== 1. 会计分录仿真模块 =====================
    def build_accounting_page(self):
        page = ttk.Frame(self.notebook)
        self.notebook.add(page, text="会计分录仿真")

        # 左侧业务选择
        left = tk.Frame(page, padx=20, pady=20)
        left.pack(side="left", fill="y")

        tk.Label(left, text="CPA会计高频业务", font=("微软雅黑", 12, "bold")).pack(anchor="w", pady=(0,10))

        self.biz_type = ttk.Combobox(left, state="readonly", width=25, values=[
            "交易性金融资产购入",
            "交易性金融资产公允价值变动",
            "长期股权投资权益法-确认投资收益",
            "存货跌价准备计提",
            "固定资产折旧计提",
            "固定资产减值计提",
            "收入确认-赊销",
            "应付职工薪酬计提"
        ])
        self.biz_type.current(0)
        self.biz_type.pack(pady=5)
        self.biz_type.bind("<<ComboboxSelected>>", self.show_entry_params)

        self.param_frame = tk.Frame(left)
        self.param_frame.pack(pady=10, fill="x")
        self.entry_params = {}

        tk.Button(left, text="生成会计分录", command=self.generate_entry,
                  width=20, bg="#1a56db", fg="white").pack(pady=15)

        # 分录展示区
        tk.Label(left, text="记账凭证", font=("微软雅黑", 11, "bold")).pack(anchor="w")
        self.entry_text = tk.Text(left, width=38, height=18, font=("微软雅黑", 10))
        self.entry_text.pack(pady=5)

        # 右侧科目金额分布图
        self.account_fig = plt.Figure(figsize=(6, 5), dpi=100)
        self.account_canvas = FigureCanvasTkAgg(self.account_fig, master=page)
        self.account_canvas.get_tk_widget().pack(side="right", padx=10, pady=10)
        self.show_entry_params()

    def show_entry_params(self, e=None):
        for widget in self.param_frame.winfo_children():
            widget.destroy()
        self.entry_params.clear()

        biz = self.biz_type.get()
        params_map = {
            "交易性金融资产购入": [("成本金额(元)", "cost", "100000"), ("交易费用(元)", "fee", "2000")],
            "交易性金融资产公允价值变动": [("账面价值(元)", "book", "100000"), ("公允价值(元)", "fair", "120000")],
            "长期股权投资权益法-确认投资收益": [("被投资方净利润(元)", "profit", "500000"), ("持股比例(%)", "rate", "30")],
            "存货跌价准备计提": [("存货成本(元)", "cost", "200000"), ("可变现净值(元)", "nrv", "180000")],
            "固定资产折旧计提": [("原值(元)", "cost", "500000"), ("年折旧额(元)", "dep", "47500")],
            "固定资产减值计提": [("账面价值(元)", "book", "400000"), ("可收回金额(元)", "recover", "320000")],
            "收入确认-赊销": [("销售收入(元)", "revenue", "200000"), ("增值税额(元)", "tax", "26000")],
            "应付职工薪酬计提": [("工资总额(元)", "salary", "150000"), ("社保公积金(元)", "social", "30000")]
        }

        for label, key, default in params_map[biz]:
            row = tk.Frame(self.param_frame)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label, width=18, anchor="w").pack(side="left")
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

            elif biz == "交易性金融资产公允价值变动":
                book = float(self.entry_params["book"].get())
                fair = float(self.entry_params["fair"].get())
                diff = fair - book
                if diff > 0:
                    entries = [
                        ("借：交易性金融资产-公允价值变动", diff),
                        ("贷：公允价值变动损益", diff)
                    ]
                else:
                    entries = [
                        ("借：公允价值变动损益", -diff),
                        ("贷：交易性金融资产-公允价值变动", -diff)
                    ]
                amounts = {"交易性金融资产": abs(diff), "公允价值变动损益": abs(diff)}

            elif biz == "长期股权投资权益法-确认投资收益":
                profit = float(self.entry_params["profit"].get())
                rate = float(self.entry_params["rate"].get()) / 100
                invest = profit * rate
                entries = [
                    ("借：长期股权投资-损益调整", invest),
                    ("贷：投资收益", invest)
                ]
                amounts = {"长期股权投资": invest, "投资收益": invest}

            elif biz == "存货跌价准备计提":
                cost = float(self.entry_params["cost"].get())
                nrv = float(self.entry_params["nrv"].get())
                loss = cost - nrv
                if loss > 0:
                    entries = [
                        ("借：资产减值损失", loss),
                        ("贷：存货跌价准备", loss)
                    ]
                    amounts = {"资产减值损失": loss, "存货跌价准备": loss}
                else:
                    messagebox.showinfo("提示", "可变现净值高于成本，无需计提减值")
                    return

            elif biz == "固定资产折旧计提":
                dep = float(self.entry_params["dep"].get())
                entries = [
                    ("借：管理费用", dep),
                    ("贷：累计折旧", dep)
                ]
                amounts = {"管理费用": dep, "累计折旧": dep}

            elif biz == "固定资产减值计提":
                book = float(self.entry_params["book"].get())
                recover = float(self.entry_params["recover"].get())
                loss = book - recover
                if loss > 0:
                    entries = [
                        ("借：资产减值损失", loss),
                        ("贷：固定资产减值准备", loss)
                    ]
                    amounts = {"资产减值损失": loss, "固定资产减值准备": loss}
                else:
                    messagebox.showinfo("提示", "未发生减值")
                    return

            elif biz == "收入确认-赊销":
                revenue = float(self.entry_params["revenue"].get())
                tax = float(self.entry_params["tax"].get())
                entries = [
                    ("借：应收账款", revenue + tax),
                    ("贷：主营业务收入", revenue),
                    ("贷：应交税费-应交增值税(销项)", tax)
                ]
                amounts = {"应收账款": revenue+tax, "主营业务收入": revenue, "应交税费": tax}

            elif biz == "应付职工薪酬计提":
                salary = float(self.entry_params["salary"].get())
                social = float(self.entry_params["social"].get())
                entries = [
                    ("借：管理费用", salary + social),
                    ("贷：应付职工薪酬-工资", salary),
                    ("贷：应付职工薪酬-社保公积金", social)
                ]
                amounts = {"管理费用": salary+social, "应付职工薪酬": salary+social}

            # 显示分录
            self.entry_text.delete("1.0", "end")
            self.entry_text.insert("end", f"摘要：{biz}\n")
            self.entry_text.insert("end", "="*40 + "\n")
            for subject, amount in entries:
                if "借：" in subject:
                    self.entry_text.insert("end", f"{subject:<25} {amount:>10,.2f}\n")
                else:
                    self.entry_text.insert("end", f"    {subject:<21} {amount:>10,.2f}\n")

            # 绘制科目金额图
            self.account_fig.clear()
            ax = self.account_fig.add_subplot(111)
            subjects = list(amounts.keys())
            values = list(amounts.values())
            bars = ax.bar(subjects, values, color=["#3b82f6", "#10b981", "#f59e0b", "#ef4444"])
            for bar, val in zip(bars, values):
                ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+max(values)*0.01,
                        f"{val:,.0f}", ha="center", fontsize=9)
            ax.set_title("业务涉及科目金额")
            ax.set_ylabel("金额(元)")
            ax.grid(axis="y", alpha=0.3)
            plt.setp(ax.get_xticklabels(), rotation=15)
            self.account_canvas.draw()

        except ValueError:
            messagebox.showerror("错误", "请输入有效数字！")

    # ===================== 2. 审计风险评估模块 =====================
    def build_audit_page(self):
        page = ttk.Frame(self.notebook)
        self.notebook.add(page, text="审计风险评估")

        left = tk.Frame(page, padx=20, pady=20)
        left.pack(side="left", fill="y")

        tk.Label(left, text="审计风险模型参数", font=("微软雅黑", 12, "bold")).pack(anchor="w", pady=(0,10))

        self.risk_inputs = {}
        items = [
            ("重大错报风险(%)", "mm_risk", "40"),
            ("检查风险(%)", "check_risk", "15"),
            ("控制风险(%)", "control_risk", "30"),
            ("固有风险(%)", "inherent_risk", "50")
        ]
        for label, key, default in items:
            row = tk.Frame(left)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, width=18, anchor="w").pack(side="left")
            entry = tk.Entry(row, width=12)
            entry.insert(0, default)
            entry.pack(side="right")
            self.risk_inputs[key] = entry

        tk.Button(left, text="计算审计风险", command=self.calc_audit_risk,
                  width=20, bg="#b45309", fg="white").pack(pady=15)

        self.risk_result = tk.Text(left, width=35, height=12, font=("微软雅黑", 10))
        self.risk_result.pack(pady=5)

        # 右侧风险雷达图
        self.risk_fig = plt.Figure(figsize=(6, 5), dpi=100)
        self.risk_canvas = FigureCanvasTkAgg(self.risk_fig, master=page)
        self.risk_canvas.get_tk_widget().pack(side="right", padx=10, pady=10)
        self.calc_audit_risk()

    def calc_audit_risk(self):
        try:
            mm = float(self.risk_inputs["mm_risk"].get()) / 100
            check = float(self.risk_inputs["check_risk"].get()) / 100
            control = float(self.risk_inputs["control_risk"].get()) / 100
            inherent = float(self.risk_inputs["inherent_risk"].get()) / 100

            audit_risk = mm * check * 100
            mm_verify = inherent * control * 100

            self.risk_result.delete("1.0", "end")
            result = f"""
【审计风险模型】
审计风险 = 重大错报风险 × 检查风险

重大错报风险：{mm*100:.1f}%
检查风险：    {check*100:.1f}%
审计风险：    {audit_risk:.2f}%

【重大错报拆解】
重大错报风险 = 固有风险 × 控制风险

固有风险：  {inherent*100:.1f}%
控制风险：  {control*100:.1f}%
测算值：    {mm_verify:.1f}%

【审计结论】
审计风险{audit_risk:.2f}%，
{"处于可接受水平" if audit_risk < 5 else "偏高，需追加审计程序"}
"""
            self.risk_result.insert("end", result)

            # 雷达图
            self.risk_fig.clear()
            ax = self.risk_fig.add_subplot(111, polar=True)
            categories = ["固有风险", "控制风险", "重大错报风险", "检查风险", "审计风险"]
            scores = [inherent*100, control*100, mm*100, check*100, audit_risk]
            scores += scores[:1]
            angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False)
            angles = np.append(angles, angles[0])

            ax.plot(angles, scores, 'o-', color="#b45309", linewidth=2)
            ax.fill(angles, scores, alpha=0.25, color="#b45309")
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories)
            ax.set_ylim(0, 100)
            ax.set_title("审计风险评估雷达图", pad=15, fontsize=12)
            self.risk_canvas.draw()

        except ValueError:
            messagebox.showerror("错误", "请输入有效数字！")

    # ===================== 3. 财管指标测算模块 =====================
    def build_finance_page(self):
        page = ttk.Frame(self.notebook)
        self.notebook.add(page, text="财管指标测算")

        left = tk.Frame(page, padx=20, pady=20)
        left.pack(side="left", fill="y")

        tk.Label(left, text="管理用报表 & 杜邦分析", font=("微软雅黑", 12, "bold")).pack(anchor="w", pady=(0,10))

        self.fin_inputs = {}
        items = [
            ("税后经营净利润(万)", "nopat", "180"),
            ("净经营资产(万)", "net_assets", "1000"),
            ("税后利息费用(万)", "interest", "30"),
            ("净负债(万)", "net_debt", "400"),
            ("股东权益(万)", "equity", "600"),
            ("营业收入(万)", "revenue", "2000")
        ]
        for label, key, default in items:
            row = tk.Frame(left)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, width=18, anchor="w").pack(side="left")
            entry = tk.Entry(row, width=12)
            entry.insert(0, default)
            entry.pack(side="right")
            self.fin_inputs[key] = entry

        tk.Button(left, text="测算管理用杜邦", command=self.calc_finance,
                  width=20, bg="#0a8f4a", fg="white").pack(pady=15)

        self.fin_result = tk.Text(left, width=35, height=14, font=("微软雅黑", 10))
        self.fin_result.pack(pady=5)

        # 右侧杜邦拆解图
        self.fin_fig = plt.Figure(figsize=(6, 5), dpi=100)
        self.fin_canvas = FigureCanvasTkAgg(self.fin_fig, master=page)
        self.fin_canvas.get_tk_widget().pack(side="right", padx=10, pady=10)
        self.calc_finance()

    def calc_finance(self):
        try:
            nopat = float(self.fin_inputs["nopat"].get())
            na = float(self.fin_inputs["net_assets"].get())
            interest = float(self.fin_inputs["interest"].get())
            nd = float(self.fin_inputs["net_debt"].get())
            eq = float(self.fin_inputs["equity"].get())
            rev = float(self.fin_inputs["revenue"].get())

            # 管理用杜邦体系
            roic = nopat / na * 100          # 净经营资产净利率
            net_interest_rate = interest / nd * 100  # 税后利息率
            leverage = nd / eq                 # 净财务杠杆
            roe = (roic + (roic - net_interest_rate) * leverage)  # 权益净利率

            self.fin_result.delete("1.0", "end")
            result = f"""
【管理用杜邦分析体系】
权益净利率 = 净经营资产净利率 + 
  (净经营资产净利率 - 税后利息率) × 净财务杠杆

净经营资产净利率：{roic:.2f}%
税后利息率：    {net_interest_rate:.2f}%
经营差异率：    {roic - net_interest_rate:.2f}%
净财务杠杆：    {leverage:.2f} 倍
杠杆贡献率：    {(roic - net_interest_rate)*leverage:.2f}%
权益净利率ROE： {roe:.2f}%

【周转指标】
净经营资产周转次数：{rev/na:.2f} 次
销售税后经营净利率：{nopat/rev*100:.2f}%
"""
            self.fin_result.insert("end", result)

            # 柱状图对比
            self.fin_fig.clear()
            ax = self.fin_fig.add_subplot(111)
            items = ["净经营资产净利率", "税后利息率", "经营差异率", "权益净利率ROE"]
            values = [roic, net_interest_rate, roic-net_interest_rate, roe]
            colors = ["#10b981", "#f59e0b", "#3b82f6", "#ef4444"]
            bars = ax.bar(items, values, color=colors, width=0.6)
            for bar, val in zip(bars, values):
                ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.3,
                        f"{val:.2f}%", ha="center", fontsize=9)
            ax.set_title("管理用杜邦分析指标")
            ax.set_ylabel("百分比(%)")
            ax.grid(axis="y", alpha=0.3)
            plt.setp(ax.get_xticklabels(), rotation=10)
            self.fin_canvas.draw()

        except ValueError:
            messagebox.showerror("错误", "请输入有效数字！")

    # ===================== 4. 税法税金计算模块 =====================
    def build_tax_page(self):
        page = ttk.Frame(self.notebook)
        self.notebook.add(page, text="税法税金计算")

        left = tk.Frame(page, padx=20, pady=20)
        left.pack(side="left", fill="y")

        tk.Label(left, text="三大税种计算器", font=("微软雅黑", 12, "bold")).pack(anchor="w", pady=(0,10))

        self.tax_type = ttk.Combobox(left, state="readonly", width=20, values=[
            "增值税(一般纳税人)", "企业所得税", "个人所得税(综合所得)"
        ])
        self.tax_type.current(0)
        self.tax_type.pack(pady=5)
        self.tax_type.bind("<<ComboboxSelected>>", self.show_tax_params)

        self.tax_param_frame = tk.Frame(left)
        self.tax_param_frame.pack(pady=10, fill="x")
        self.tax_params = {}

        tk.Button(left, text="计算应纳税额", command=self.calc_tax,
                  width=20, bg="#be123c", fg="white").pack(pady=15)

        self.tax_result = tk.Text(left, width=35, height=15, font=("微软雅黑", 10))
        self.tax_result.pack(pady=5)

        # 右侧税负构成图
        self.tax_fig = plt.Figure(figsize=(6, 5), dpi=100)
        self.tax_canvas = FigureCanvasTkAgg(self.tax_fig, master=page)
        self.tax_canvas.get_tk_widget().pack(side="right", padx=10, pady=10)
        self.show_tax_params()

    def show_tax_params(self, e=None):
        for widget in self.tax_param_frame.winfo_children():
            widget.destroy()
        self.tax_params.clear()

        tax = self.tax_type.get()
        params_map = {
            "增值税(一般纳税人)": [
                ("不含税销售额(元)", "sales", "100000"),
                ("进项税额(元)", "input", "10000"),
                ("进项转出(元)", "input_out", "500"),
                ("适用税率(%)", "rate", "13")
            ],
            "企业所得税": [
                ("利润总额(元)", "profit", "300000"),
                ("纳税调增额(元)", "add", "20000"),
                ("纳税调减额(元)", "minus", "10000"),
                ("所得税税率(%)", "rate", "25")
            ],
            "个人所得税(综合所得)": [
                ("年收入额(元)", "income", "200000"),
                ("专项扣除(元)", "special", "30000"),
                ("专项附加扣除(元)", "extra", "24000"),
                ("其他扣除(元)", "other", "0")
            ]
        }

        for label, key, default in params_map[tax]:
            row = tk.Frame(self.tax_param_frame)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label, width=18, anchor="w").pack(side="left")
            entry = tk.Entry(row, width=12)
            entry.insert(0, default)
            entry.pack(side="right")
            self.tax_params[key] = entry

    def calc_tax(self):
        try:
            tax_type = self.tax_type.get()
            tax_amount = 0
            breakdown = {}

            if tax_type == "增值税(一般纳税人)":
                sales = float(self.tax_params["sales"].get())
                input_tax = float(self.tax_params["input"].get())
                input_out = float(self.tax_params["input_out"].get())
                rate = float(self.tax_params["rate"].get()) / 100

                output_tax = sales * rate
                payable = output_tax - input_tax + input_out
                tax_amount = max(payable, 0)

                self.tax_result.delete("1.0", "end")
                self.tax_result.insert("end", f"""
【增值税计算】
销项税额：  {output_tax:,.2f} 元
进项税额：  {input_tax:,.2f} 元
进项税额转出：{input_out:,.2f} 元
应纳税额：  {tax_amount:,.2f} 元
税负率：      {tax_amount/sales*100:.2f}%
""")
                breakdown = {"销项税额": output_tax, "进项抵扣": -input_tax, "进项转出": input_out}

            elif tax_type == "企业所得税":
                profit = float(self.tax_params["profit"].get())
                add = float(self.tax_params["add"].get())
                minus = float(self.tax_params["minus"].get())
                rate = float(self.tax_params["rate"].get()) / 100

                taxable = profit + add - minus
                tax_amount = taxable * rate

                self.tax_result.delete("1.0", "end")
                self.tax_result.insert("end", f"""
【企业所得税计算】
利润总额：    {profit:,.2f} 元
纳税调增：    {add:,.2f} 元
纳税调减：    {minus:,.2f} 元
应纳税所得额：{taxable:,.2f} 元
适用税率：    {rate*100:.0f}%
应纳所得税额：{tax_amount:,.2f} 元
""")
                breakdown = {"利润总额": profit, "纳税调增": add, "纳税调减": -minus, "应纳税额": tax_amount}

            elif tax_type == "个人所得税(综合所得)":
                income = float(self.tax_params["income"].get())
                special = float(self.tax_params["special"].get())
                extra = float(self.tax_params["extra"].get())
                other = float(self.tax_params["other"].get())

                # 减除费用6万
                taxable = income - 60000 - special - extra - other
                taxable = max(taxable, 0)

                # 七级超额累进税率
                brackets = [
                    (36000, 0.03, 0),
                    (144000, 0.1, 2520),
                    (300000, 0.2, 16920),
                    (420000, 0.25, 31920),
                    (660000, 0.3, 52920),
                    (960000, 0.35, 85920),
                    (float('inf'), 0.45, 181920)
                ]
                tax_amount = 0
                for limit, rate, quick in brackets:
                    if taxable <= limit:
                        tax_amount = taxable * rate - quick
                        break

                self.tax_result.delete("1.0", "end")
                self.tax_result.insert("end", f"""
【个人所得税(综合所得)】
年收入额：      {income:,.2f} 元
减除费用：      60,000.00 元
专项扣除：      {special:,.2f} 元
专项附加扣除：  {extra:,.2f} 元
应纳税所得额：  {taxable:,.2f} 元
应纳个税：      {tax_amount:,.2f} 元
税负率：        {tax_amount/income*100:.2f}%
""")
                breakdown = {"收入总额": income, "各项扣除": 60000+special+extra+other, "应纳税额": tax_amount}

            # 绘制税负图
            self.tax_fig.clear()
            ax = self.tax_fig.add_subplot(111)
            labels = list(breakdown.keys())
            values = [abs(v) for v in breakdown.values()]
            colors = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444"]
            ax.pie(values, labels=labels, autopct="%1.1f%%", colors=colors[:len(values)], startangle=90)
            ax.set_title(f"{tax_type}构成")
            self.tax_canvas.draw()

        except ValueError:
            messagebox.showerror("错误", "请输入有效数字！")

    # ===================== 5. 战略SWOT分析模块 =====================
    def build_strategy_page(self):
        page = ttk.Frame(self.notebook)
        self.notebook.add(page, text="战略SWOT分析")

        left = tk.Frame(page, padx=20, pady=20)
        left.pack(side="left", fill="y")

        tk.Label(left, text="SWOT因素输入", font=("微软雅黑", 12, "bold")).pack(anchor="w", pady=(0,10))

        self.swot_inputs = {}
        quadrants = [
            ("优势 S", "s", "品牌知名度高\n财务状况良好\n技术研发能力强"),
            ("劣势 W", "w", "产品成本偏高\n渠道覆盖不足\n人才储备不足"),
            ("机会 O", "o", "政策支持\n市场需求增长\n技术迭代机遇"),
            ("威胁 T", "t", "竞争加剧\n原材料涨价\n监管趋严")
        ]

        for label, key, default in quadrants:
            tk.Label(left, text=label, font=("微软雅黑", 10, "bold"), fg="#1a56db").pack(anchor="w", pady=(8,2))
            text = tk.Text(left, width=30, height=4, font=("微软雅黑", 9))
            text.insert("end", default)
            text.pack()
            self.swot_inputs[key] = text

        tk.Button(left, text="生成SWOT分析矩阵", command=self.generate_swot,
                  width=22, bg="#7c3aed", fg="white").pack(pady=15)

        self.swot_result = tk.Text(left, width=35, height=8, font=("微软雅黑", 10))
        self.swot_result.pack()

        # 右侧SWOT矩阵图
        self.swot_fig = plt.Figure(figsize=(6, 5), dpi=100)
        self.swot_canvas = FigureCanvasTkAgg(self.swot_fig, master=page)
        self.swot_canvas.get_tk_widget().pack(side="right", padx=10, pady=10)
        self.generate_swot()

    def generate_swot(self):
        s = self.swot_inputs["s"].get("1.0", "end").strip().split("\n")
        w = self.swot_inputs["w"].get("1.0", "end").strip().split("\n")
        o = self.swot_inputs["o"].get("1.0", "end").strip().split("\n")
        t = self.swot_inputs["t"].get("1.0", "end").strip().split("\n")

        # 战略推导
        so = "SO战略：发挥优势，抓住机会\n  利用品牌技术优势，抢占市场增长机遇"
        wo = "WO战略：克服劣势，利用机会\n  降低成本，拓展渠道，借政策东风补短板"
        st = "ST战略：利用优势，规避威胁\n  技术升级对冲成本上涨，差异化应对竞争"
        wt = "WT战略：减少劣势，回避威胁\n  收缩非核心业务，强化成本管控"

        self.swot_result.delete("1.0", "end")
        self.swot_result.insert("end", f"""
【战略组合推导】
{so}
{wo}
{st}
{wt}
""")

        # 绘制四象限矩阵
        self.swot_fig.clear()
        ax = self.swot_fig.add_subplot(111)

        # 四个象限
        ax.axvline(0, color="black", linewidth=1.5)
        ax.axhline(0, color="black", linewidth=1.5)

        # 象限内容
        ax.text(-0.5, 0.5, "优势 S\n"+"\n".join(s[:3]), va="center", ha="center",
                bbox=dict(facecolor="#dcfce7", alpha=0.8), fontsize=9)
        ax.text(0.5, 0.5, "机会 O\n"+"\n".join(o[:3]), va="center", ha="center",
                bbox=dict(facecolor="#dbeafe", alpha=0.8), fontsize=9)
        ax.text(-0.5, -0.5, "劣势 W\n"+"\n".join(w[:3]), va="center", ha="center",
                bbox=dict(facecolor="#fee2e2", alpha=0.8), fontsize=9)
        ax.text(0.5, -0.5, "威胁 T\n"+"\n".join(t[:3]), va="center", ha="center",
                bbox=dict(facecolor="#fef3c7", alpha=0.8), fontsize=9)

        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title("SWOT战略分析矩阵", fontsize=12, pad=10)
        self.swot_canvas.draw()

    # ===================== 6. 题库模考训练模块 =====================
    def build_exam_page(self):
        page = ttk.Frame(self.notebook)
        self.notebook.add(page, text="题库模考训练")

        left = tk.Frame(page, padx=20, pady=20)
        left.pack(side="left", fill="y")

        tk.Label(left, text="CPA精选客观题", font=("微软雅黑", 12, "bold")).pack(anchor="w", pady=(0,10))

        self.question_bank = [
            {"subject": "会计", "q": "下列各项中，应计入存货成本的是：",
             "options": ["A.非正常消耗的直接材料", "B.采购入库后的仓储费用",
                        "C.生产过程中为达到下一个生产阶段所必需的仓储费用", "D.不能归属于使存货达到目前场所的其他支出"],
             "answer": "C"},
            {"subject": "审计", "q": "下列各项中，属于认定层次重大错报风险的是：",
             "options": ["A.管理层缺乏诚信", "B.内部控制薄弱",
                        "C.存货跌价准备计提不足", "D.行业环境恶化"],
             "answer": "C"},
            {"subject": "财管", "q": "下列各项中，属于经营营运资本的是：",
             "options": ["A.短期借款", "B.应付债券", "C.应收账款", "D.长期股权投资"],
             "answer": "C"},
            {"subject": "税法", "q": "下列各项中，属于增值税视同销售的是：",
             "options": ["A.将外购货物用于集体福利", "B.将自产货物用于投资",
                        "C.将外购货物用于个人消费", "D.将自产货物用于连续生产应税产品"],
             "answer": "B"},
            {"subject": "经济法", "q": "根据公司法律制度，有限责任公司首次股东会的召集人是：",
             "options": ["A.董事长", "B.监事会", "C.出资最多的股东", "D.法定代表人"],
             "answer": "C"},
            {"subject": "战略", "q": "下列各项中，属于成本领先战略适用情形的是：",
             "options": ["A.产品差异化程度高", "B.价格敏感的顾客众多",
                        "C.目标市场具有特定需求", "D.技术变革快"],
             "answer": "B"}
        ]

        self.current_q = 0
        self.q_var = tk.StringVar()

        self.q_subject = tk.Label(left, text="", font=("微软雅黑", 10), fg="#666")
        self.q_subject.pack(anchor="w")

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

        self.q_result = tk.Label(left, text="", font=("微软雅黑", 11, "bold"))
        self.q_result.pack(pady=5)

        # 右侧各科正确率
        self.exam_fig = plt.Figure(figsize=(6, 5), dpi=100)
        self.exam_canvas = FigureCanvasTkAgg(self.exam_fig, master=page)
        self.exam_canvas.get_tk_widget().pack(side="right", padx=10, pady=10)

        self.subject_correct = {}
        self.subject_total = {}
        self.load_question()
        self.update_exam_chart()

    def load_question(self):
        q = self.question_bank[self.current_q]
        self.q_subject.config(text=f"科目：{q['subject']}")
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
        sub = q["subject"]
        self.subject_total[sub] = self.subject_total.get(sub, 0) + 1

        if self.q_var.get() == q["answer"]:
            self.subject_correct[sub] = self.subject_correct.get(sub, 0) + 1
            self.q_result.config(text="✅ 回答正确", fg="#0a8f4a")
        else:
            self.q_result.config(text=f"❌ 正确答案：{q['answer']}", fg="#d92d20")

        self.study_data["done_questions"] += 1
        if self.q_var.get() == q["answer"]:
            self.study_data["correct_questions"] += 1

        self.update_exam_chart()

    def next_question(self):
        self.current_q = (self.current_q + 1) % len(self.question_bank)
        self.load_question()

    def update_exam_chart(self):
        self.exam_fig.clear()
        ax = self.exam_fig.add_subplot(111)
        subjects = ["会计", "审计", "财管", "税法", "经济法", "战略"]
        rates = []
        for s in subjects:
            total = self.subject_total.get(s, 0)
            correct = self.subject_correct.get(s, 0)
            rates.append(correct/total*100 if total > 0 else 0)
            self.study_data["subject_scores"][s] = rates[-1]

        bars = ax.bar(subjects, rates, color=["#3b82f6", "#b45309", "#0a8f4a", "#be123c", "#7c3aed", "#f59e0b"])
        for bar, val in zip(bars, rates):
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+1, f"{val:.0f}%", ha="center")
        ax.set_title("各科正确率统计")
        ax.set_ylabel("正确率(%)")
        ax.set_ylim(0, 100)
        ax.grid(axis="y", alpha=0.3)
        self.exam_canvas.draw()

    # ===================== 7. 备考计划生成模块 =====================
    def build_plan_page(self):
        page = ttk.Frame(self.notebook)
        self.notebook.add(page, text="备考计划生成")

        left = tk.Frame(page, padx=20, pady=20)
        left.pack(side="left", fill="y")

        tk.Label(left, text="CPA备考计划生成器", font=("微软雅黑", 12, "bold")).pack(anchor="w", pady=(0,10))

        tk.Label(left, text="距离考试天数：").pack(anchor="w", pady=5)
        self.days_entry = tk.Entry(left, width=10)
        self.days_entry.insert(0, "180")
        self.days_entry.pack(anchor="w")

        tk.Label(left, text="每日学习时长(小时)：").pack(anchor="w", pady=5)
        self.hours_entry = tk.Entry(left, width=10)
        self.hours_entry.insert(0, "4")
        self.hours_entry.pack(anchor="w")

        tk.Label(left, text="薄弱科目：").pack(anchor="w", pady=5)
        self.weak_sub = tk.StringVar(value="会计")
        subs = ["会计", "审计", "财管", "税法", "经济法", "战略"]
        for s in subs:
            tk.Radiobutton(left, text=s, variable=self.weak_sub, value=s).pack(anchor="w")

        tk.Button(left, text="生成备考计划", command=self.generate_plan, width=18, bg="#1a56db", fg="white").pack(pady=15)

        self.plan_text = tk.Text(left, width=40, height=22, font=("微软雅黑", 10))
        self.plan_text.pack()

        # 右侧时间分配饼图
        self.plan_fig = plt.Figure(figsize=(5, 5), dpi=100)
        self.plan_canvas = FigureCanvasTkAgg(self.plan_fig, master=page)
        self.plan_canvas.get_tk_widget().pack(side="right", padx=10, pady=10)
        self.generate_plan()

    def generate_plan(self):
        try:
            days = int(self.days_entry.get())
            hours = float(self.hours_entry.get())
            weak = self.weak_sub.get()

            # 六科基础时间权重
            base_weight = {"会计": 0.22, "审计": 0.18, "财管": 0.18, "税法": 0.16, "经济法": 0.14, "战略": 0.12}
            base_weight[weak] += 0.05
            total_w = sum(base_weight.values())
            time_dist = {k: v/total_w * hours for k, v in base_weight.items()}

            plan = f"""【CPA专业阶段 {days} 天备考计划】
每日学习时长：{hours} 小时
薄弱科目强化：{weak}

━━━━━━━━━━━━━━━━━
每日各科时间分配：
"""
            for k, v in time_dist.items():
                plan += f"  {k}：{v:.1f} 小时\n"

            plan += f"""
━━━━━━━━━━━━━━━━━
阶段规划：

【基础阶段 第1-{days//3}天】
• 通读六科教材，搭建知识框架
• 每章配套客观题练习
• 重点攻克{weak}基础章节

【强化阶段 第{days//3+1}-{days*2//3}天】
• 重难点章节突破，主观题专项训练
• 历年真题逐章练习
• 错题本整理复盘

【冲刺阶段 第{days*2//3+1}-{days}天】
• 整套真题模考，掐时间
• 回归教材，查漏补缺
• 背诵记忆类科目（经济法/战略）
• 调整作息，保持状态
"""
            self.plan_text.delete("1.0", "end")
            self.plan_text.insert("end", plan)

            # 饼图
            self.plan_fig.clear()
            ax = self.plan_fig.add_subplot(111)
            colors = ["#3b82f6", "#b45309", "#0a8f4a", "#be123c", "#7c3aed", "#f59e0b"]
            ax.pie(time_dist.values(), labels=time_dist.keys(),
                   autopct="%1.1f%%", colors=colors, startangle=90)
            ax.set_title("每日学习时间分配")
            self.plan_canvas.draw()

        except ValueError:
            messagebox.showerror("错误", "请输入有效数字！")

    # ===================== 8. 学习数据可视化模块 =====================
    def build_analysis_page(self):
        page = ttk.Frame(self.notebook)
        self.notebook.add(page, text="学习数据分析")

        left = tk.Frame(page, padx=20, pady=20)
        left.pack(side="left", fill="y")

        tk.Label(left, text="学习数据总览", font=("微软雅黑", 12, "bold")).pack(anchor="w", pady=(0,10))

        self.stats_text = tk.Text(left, width=30, height=16, font=("微软雅黑", 10))
        self.stats_text.pack(pady=5)

        tk.Button(left, text="刷新数据", command=self.refresh_stats, width=18, bg="#1a56db", fg="white").pack(pady=10)

        # 右侧能力雷达图
        self.analysis_fig = plt.Figure(figsize=(6, 5), dpi=100)
        self.analysis_canvas = FigureCanvasTkAgg(self.analysis_fig, master=page)
        self.analysis_canvas.get_tk_widget().pack(side="right", padx=10, pady=10)
        self.refresh_stats()

    def refresh_stats(self):
        scores = self.study_data["subject_scores"]
        done = self.study_data["done_questions"]
        correct = self.study_data["correct_questions"]
        total_rate = correct/done*100 if done > 0 else 0

        stats = f"""
【CPA备考进度统计】

已完成题目：{done} 道
正确题目：  {correct} 道
总正确率：  {total_rate:.1f}%

【各科掌握度】
会计：  {scores['会计']:.1f}%
审计：  {scores['审计']:.1f}%
财管：  {scores['财管']:.1f}%
税法：  {scores['税法']:.1f}%
经济法：{scores['经济法']:.1f}%
战略：  {scores['战略']:.1f}%

综合测评得分：
{sum(scores.values())/6:.1f} 分
"""
        self.stats_text.delete("1.0", "end")
        self.stats_text.insert("end", stats)

        # 雷达图
        self.analysis_fig.clear()
        ax = self.analysis_fig.add_subplot(111, polar=True)
        categories = list(scores.keys())
        values = list(scores.values())
        values += values[:1]
        angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False)
        angles = np.append(angles, angles[0])

        ax.plot(angles, values, 'o-', color="#1a56db", linewidth=2)
        ax.fill(angles, values, alpha=0.25, color="#1a56db")
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_ylim(0, 100)
        ax.set_title("CPA六科能力雷达图", pad=15, fontsize=12)
        self.analysis_canvas.draw()


if __name__ == "__main__":
    app = CPASimulator()
    app.mainloop()
