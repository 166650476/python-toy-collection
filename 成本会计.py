import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# 中文显示配置
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False


class CostAccountingSim(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("成本会计学仿真综合展示系统")
        self.geometry("1280x780")
        self.resizable(False, False)

        # 顶部标题
        tk.Label(self, text="成本会计学学习仿真综合工具",
                 font=("微软雅黑", 16, "bold"), fg="#1a56db").pack(pady=8)

        # 多标签页容器
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=5)

        # 7大核心模块
        self.build_material_page()    # 1.材料费用分配
        self.build_labor_page()      # 2.人工费用分配
        self.build_manufacture_page() # 3.制造费用分配
        self.build_auxiliary_page()  # 4.辅助生产费用分配
        self.build_equivalent_page() # 5.约当产量法
        self.build_variety_page()    # 6.品种法成本计算
        self.build_analysis_page()   # 7.成本报表分析

    # ===================== 1. 材料费用分配（定额消耗量比例法） =====================
    def build_material_page(self):
        page = ttk.Frame(self.notebook)
        self.notebook.add(page, text="材料费用分配")

        left = tk.Frame(page, padx=20, pady=20)
        left.pack(side="left", fill="y")

        tk.Label(left, text="定额消耗量比例分配法", font=("微软雅黑", 12, "bold")).pack(anchor="w", pady=(0,10))

        self.material_inputs = {}
        items = [
            ("材料总费用(元)", "total_cost", "10000"),
            ("A产品产量(件)", "qty_a", "100"),
            ("A产品单位定额(千克/件)", "quota_a", "5"),
            ("B产品产量(件)", "qty_b", "200"),
            ("B产品单位定额(千克/件)", "quota_b", "3"),
        ]
        for label, key, default in items:
            row = tk.Frame(left)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, width=20, anchor="w").pack(side="left")
            entry = tk.Entry(row, width=12)
            entry.insert(0, default)
            entry.pack(side="right")
            self.material_inputs[key] = entry

        tk.Button(left, text="计算材料费用分配", command=self.calc_material,
                  width=20, bg="#1a56db", fg="white").pack(pady=15)

        self.material_result = tk.Text(left, width=38, height=16, font=("微软雅黑", 10))
        self.material_result.pack(pady=5)

        # 右侧图表
        self.material_fig = plt.Figure(figsize=(6, 5), dpi=100)
        self.material_canvas = FigureCanvasTkAgg(self.material_fig, master=page)
        self.material_canvas.get_tk_widget().pack(side="right", padx=10, pady=10)
        self.calc_material()

    def calc_material(self):
        try:
            total = float(self.material_inputs["total_cost"].get())
            qty_a = float(self.material_inputs["qty_a"].get())
            quota_a = float(self.material_inputs["quota_a"].get())
            qty_b = float(self.material_inputs["qty_b"].get())
            quota_b = float(self.material_inputs["quota_b"].get())

            total_quota_a = qty_a * quota_a
            total_quota_b = qty_b * quota_b
            total_quota = total_quota_a + total_quota_b
            rate = total / total_quota
            cost_a = total_quota_a * rate
            cost_b = total_quota_b * rate

            self.material_result.delete("1.0", "end")
            result = f"""
【材料费用分配表】
材料总费用：{total:,.2f} 元

产品  产量  单位定额  定额总耗量  分配率  分配金额
A产品  {qty_a:.0f}   {quota_a:.0f}    {total_quota_a:.0f}     {rate:.4f}  {cost_a:,.2f}
B产品  {qty_b:.0f}   {quota_b:.0f}    {total_quota_b:.0f}     {rate:.4f}  {cost_b:,.2f}
合计   -     -      {total_quota:.0f}     -      {total:,.2f}

分配说明：
按产品定额消耗量比例分配材料费用
分配率 = 材料总费用 ÷ 定额消耗总量
某产品应分配费用 = 该产品定额消耗 × 分配率
"""
            self.material_result.insert("end", result)

            self.material_fig.clear()
            ax = self.material_fig.add_subplot(111)
            ax.pie([cost_a, cost_b], labels=["A产品", "B产品"],
                   autopct="%1.1f%%", colors=["#3b82f6", "#10b981"], startangle=90)
            ax.set_title("材料费用分配结构")
            self.material_canvas.draw()

        except ValueError:
            messagebox.showerror("错误", "请输入有效数字！")

    # ===================== 2. 人工费用分配（生产工时比例法） =====================
    def build_labor_page(self):
        page = ttk.Frame(self.notebook)
        self.notebook.add(page, text="人工费用分配")

        left = tk.Frame(page, padx=20, pady=20)
        left.pack(side="left", fill="y")

        tk.Label(left, text="生产工时比例分配法", font=("微软雅黑", 12, "bold")).pack(anchor="w", pady=(0,10))

        self.labor_inputs = {}
        items = [
            ("生产工人薪酬总额(元)", "total_labor", "15000"),
            ("A产品生产工时(小时)", "hour_a", "2000"),
            ("B产品生产工时(小时)", "hour_b", "3000"),
        ]
        for label, key, default in items:
            row = tk.Frame(left)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, width=20, anchor="w").pack(side="left")
            entry = tk.Entry(row, width=12)
            entry.insert(0, default)
            entry.pack(side="right")
            self.labor_inputs[key] = entry

        tk.Button(left, text="计算人工费用分配", command=self.calc_labor,
                  width=20, bg="#0a8f4a", fg="white").pack(pady=15)

        self.labor_result = tk.Text(left, width=38, height=16, font=("微软雅黑", 10))
        self.labor_result.pack(pady=5)

        self.labor_fig = plt.Figure(figsize=(6, 5), dpi=100)
        self.labor_canvas = FigureCanvasTkAgg(self.labor_fig, master=page)
        self.labor_canvas.get_tk_widget().pack(side="right", padx=10, pady=10)
        self.calc_labor()

    def calc_labor(self):
        try:
            total = float(self.labor_inputs["total_labor"].get())
            h_a = float(self.labor_inputs["hour_a"].get())
            h_b = float(self.labor_inputs["hour_b"].get())

            total_hour = h_a + h_b
            rate = total / total_hour
            cost_a = h_a * rate
            cost_b = h_b * rate

            self.labor_result.delete("1.0", "end")
            result = f"""
【直接人工费用分配表】
生产工人薪酬总额：{total:,.2f} 元

产品  生产工时  分配率  分配金额
A产品  {h_a:.0f}    {rate:.4f}  {cost_a:,.2f}
B产品  {h_b:.0f}    {rate:.4f}  {cost_b:,.2f}
合计   {total_hour:.0f}    -      {total:,.2f}

分配说明：
按产品生产工时比例分配直接人工费用
分配率 = 薪酬总额 ÷ 总生产工时
某产品应分配费用 = 该产品工时 × 分配率
"""
            self.labor_result.insert("end", result)

            self.labor_fig.clear()
            ax = self.labor_fig.add_subplot(111)
            bars = ax.bar(["A产品", "B产品"], [cost_a, cost_b],
                          color=["#3b82f6", "#10b981"], width=0.5)
            for bar, val in zip(bars, [cost_a, cost_b]):
                ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+100,
                        f"{val:,.0f}", ha="center")
            ax.set_title("直接人工费用分配")
            ax.set_ylabel("金额(元)")
            ax.grid(axis="y", alpha=0.3)
            self.labor_canvas.draw()

        except ValueError:
            messagebox.showerror("错误", "请输入有效数字！")

    # ===================== 3. 制造费用分配（生产工时比例法） =====================
    def build_manufacture_page(self):
        page = ttk.Frame(self.notebook)
        self.notebook.add(page, text="制造费用分配")

        left = tk.Frame(page, padx=20, pady=20)
        left.pack(side="left", fill="y")

        tk.Label(left, text="生产工时比例分配法", font=("微软雅黑", 12, "bold")).pack(anchor="w", pady=(0,10))

        self.mfg_inputs = {}
        items = [
            ("制造费用总额(元)", "total_mfg", "12000"),
            ("A产品生产工时(小时)", "hour_a", "2000"),
            ("B产品生产工时(小时)", "hour_b", "3000"),
        ]
        for label, key, default in items:
            row = tk.Frame(left)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, width=20, anchor="w").pack(side="left")
            entry = tk.Entry(row, width=12)
            entry.insert(0, default)
            entry.pack(side="right")
            self.mfg_inputs[key] = entry

        tk.Button(left, text="计算制造费用分配", command=self.calc_manufacture,
                  width=20, bg="#f59e0b", fg="white").pack(pady=15)

        self.mfg_result = tk.Text(left, width=38, height=16, font=("微软雅黑", 10))
        self.mfg_result.pack(pady=5)

        self.mfg_fig = plt.Figure(figsize=(6, 5), dpi=100)
        self.mfg_canvas = FigureCanvasTkAgg(self.mfg_fig, master=page)
        self.mfg_canvas.get_tk_widget().pack(side="right", padx=10, pady=10)
        self.calc_manufacture()

    def calc_manufacture(self):
        try:
            total = float(self.mfg_inputs["total_mfg"].get())
            h_a = float(self.mfg_inputs["hour_a"].get())
            h_b = float(self.mfg_inputs["hour_b"].get())

            total_hour = h_a + h_b
            rate = total / total_hour
            cost_a = h_a * rate
            cost_b = h_b * rate

            self.mfg_result.delete("1.0", "end")
            result = f"""
【制造费用分配表】
制造费用总额：{total:,.2f} 元

产品  生产工时  分配率  分配金额
A产品  {h_a:.0f}    {rate:.4f}  {cost_a:,.2f}
B产品  {h_b:.0f}    {rate:.4f}  {cost_b:,.2f}
合计   {total_hour:.0f}    -      {total:,.2f}

分配说明：
按产品生产工时比例分配制造费用
分配率 = 制造费用总额 ÷ 总生产工时
某产品应分配费用 = 该产品工时 × 分配率
"""
            self.mfg_result.insert("end", result)

            self.mfg_fig.clear()
            ax = self.mfg_fig.add_subplot(111)
            ax.pie([cost_a, cost_b], labels=["A产品", "B产品"],
                   autopct="%1.1f%%", colors=["#f59e0b", "#ef4444"], startangle=90)
            ax.set_title("制造费用分配结构")
            self.mfg_canvas.draw()

        except ValueError:
            messagebox.showerror("错误", "请输入有效数字！")

    # ===================== 4. 辅助生产费用分配（直接+交互分配法对比） =====================
    def build_auxiliary_page(self):
        page = ttk.Frame(self.notebook)
        self.notebook.add(page, text="辅助生产费用分配")

        left = tk.Frame(page, padx=20, pady=20)
        left.pack(side="left", fill="y")

        tk.Label(left, text="直接分配法 vs 交互分配法", font=("微软雅黑", 12, "bold")).pack(anchor="w", pady=(0,10))

        self.aux_inputs = {}
        items = [
            ("供电车间费用(元)", "elec_cost", "4800"),
            ("供电总量(度)", "elec_total", "12000"),
            ("供水车间费用(元)", "water_cost", "3600"),
            ("供水总量(吨)", "water_total", "9000"),
            ("供电车间耗水(吨)", "elec_water", "1000"),
            ("供水车间耗电(度)", "water_elec", "2000"),
            ("A产品耗电(度)", "a_elec", "6000"),
            ("B产品耗电(度)", "b_elec", "4000"),
            ("一般耗用耗水(吨)", "dept_water", "8000"),
        ]
        for label, key, default in items:
            row = tk.Frame(left)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label, width=20, anchor="w").pack(side="left")
            entry = tk.Entry(row, width=12)
            entry.insert(0, default)
            entry.pack(side="right")
            self.aux_inputs[key] = entry

        tk.Button(left, text="计算两种方法对比", command=self.calc_auxiliary,
                  width=20, bg="#7c3aed", fg="white").pack(pady=15)

        self.aux_result = tk.Text(left, width=38, height=18, font=("微软雅黑", 9))
        self.aux_result.pack(pady=5)

        self.aux_fig = plt.Figure(figsize=(6, 5), dpi=100)
        self.aux_canvas = FigureCanvasTkAgg(self.aux_fig, master=page)
        self.aux_canvas.get_tk_widget().pack(side="right", padx=10, pady=10)
        self.calc_auxiliary()

    def calc_auxiliary(self):
        try:
            elec_cost = float(self.aux_inputs["elec_cost"].get())
            elec_total = float(self.aux_inputs["elec_total"].get())
            water_cost = float(self.aux_inputs["water_cost"].get())
            water_total = float(self.aux_inputs["water_total"].get())
            elec_water = float(self.aux_inputs["elec_water"].get())
            water_elec = float(self.aux_inputs["water_elec"].get())
            a_elec = float(self.aux_inputs["a_elec"].get())
            b_elec = float(self.aux_inputs["b_elec"].get())
            dept_water = float(self.aux_inputs["dept_water"].get())

            # ========== 直接分配法 ==========
            # 对外供应劳务量
            elec_out = elec_total - water_elec
            water_out = water_total - elec_water
            # 对外分配率
            elec_rate_direct = elec_cost / elec_out
            water_rate_direct = water_cost / water_out
            # 分配结果
            a_elec_cost_d = a_elec * elec_rate_direct
            b_elec_cost_d = b_elec * elec_rate_direct
            dept_water_cost_d = dept_water * water_rate_direct

            # ========== 交互分配法 ==========
            # 第一步：交互分配
            elec_rate_inter = elec_cost / elec_total
            water_rate_inter = water_cost / water_total
            # 交互转入转出
            elec_out_water = water_elec * elec_rate_inter  # 供电分给供水
            water_in_elec = elec_water * water_rate_inter  # 供水分给供电
            # 交互后实际费用
            elec_actual = elec_cost - elec_out_water + water_in_elec
            water_actual = water_cost - water_in_elec + elec_out_water
            # 第二步：对外分配
            elec_rate_final = elec_actual / elec_out
            water_rate_final = water_actual / water_out
            # 分配结果
            a_elec_cost_i = a_elec * elec_rate_final
            b_elec_cost_i = b_elec * elec_rate_final
            dept_water_cost_i = dept_water * water_rate_final

            self.aux_result.delete("1.0", "end")
            result = f"""
【直接分配法】
供电分配率：{elec_rate_direct:.4f} 元/度
供水分配率：{water_rate_direct:.4f} 元/吨
A产品电费：{a_elec_cost_d:,.2f} 元
B产品电费：{b_elec_cost_d:,.2f} 元
一般耗水费：{dept_water_cost_d:,.2f} 元

【交互分配法】
交互分配：
  供电分配率：{elec_rate_inter:.4f}
  供水分配率：{water_rate_inter:.4f}
  供电转出：{elec_out_water:,.2f} 元
  供水转出：{water_in_elec:,.2f} 元
交互后费用：
  供电实际：{elec_actual:,.2f} 元
  供水实际：{water_actual:,.2f} 元
对外分配率：
  供电：{elec_rate_final:.4f} 元/度
  供水：{water_rate_final:.4f} 元/吨
A产品电费：{a_elec_cost_i:,.2f} 元
B产品电费：{b_elec_cost_i:,.2f} 元
一般耗水费：{dept_water_cost_i:,.2f} 元
"""
            self.aux_result.insert("end", result)

            # 对比柱状图
            self.aux_fig.clear()
            ax = self.aux_fig.add_subplot(111)
            x = np.arange(3)
            width = 0.35
            direct_vals = [a_elec_cost_d, b_elec_cost_d, dept_water_cost_d]
            inter_vals = [a_elec_cost_i, b_elec_cost_i, dept_water_cost_i]

            ax.bar(x - width/2, direct_vals, width, label="直接分配法", color="#3b82f6")
            ax.bar(x + width/2, inter_vals, width, label="交互分配法", color="#f59e0b")

            ax.set_xticks(x)
            ax.set_xticklabels(["A产品电费", "B产品电费", "一般耗水费"])
            ax.set_ylabel("金额(元)")
            ax.set_title("两种分配方法结果对比")
            ax.legend()
            ax.grid(axis="y", alpha=0.3)
            self.aux_canvas.draw()

        except ValueError:
            messagebox.showerror("错误", "请输入有效数字！")

    # ===================== 5. 约当产量法（完工与在产品分配） =====================
    def build_equivalent_page(self):
        page = ttk.Frame(self.notebook)
        self.notebook.add(page, text="约当产量法")

        left = tk.Frame(page, padx=20, pady=20)
        left.pack(side="left", fill="y")

        tk.Label(left, text="约当产量比例法", font=("微软雅黑", 12, "bold")).pack(anchor="w", pady=(0,10))

        tk.Label(left, text="材料投入方式：", font=("微软雅黑", 10)).pack(anchor="w")
        self.material_mode = ttk.Combobox(left, state="readonly", width=18, values=["开工一次投入", "陆续投入"])
        self.material_mode.current(0)
        self.material_mode.pack(pady=2)

        self.eq_inputs = {}
        items = [
            ("月初在产品-直接材料", "begin_mat", "2000"),
            ("月初在产品-直接人工", "begin_labor", "800"),
            ("月初在产品-制造费用", "begin_mfg", "600"),
            ("本月发生-直接材料", "month_mat", "10000"),
            ("本月发生-直接人工", "month_labor", "4000"),
            ("本月发生-制造费用", "month_mfg", "3000"),
            ("完工产品数量(件)", "finish_qty", "200"),
            ("月末在产品数量(件)", "wip_qty", "50"),
            ("在产品完工程度(%)", "completion", "40"),
        ]
        for label, key, default in items:
            row = tk.Frame(left)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label, width=20, anchor="w").pack(side="left")
            entry = tk.Entry(row, width=12)
            entry.insert(0, default)
            entry.pack(side="right")
            self.eq_inputs[key] = entry

        tk.Button(left, text="计算约当产量成本", command=self.calc_equivalent,
                  width=20, bg="#0ea5e9", fg="white").pack(pady=15)

        self.eq_result = tk.Text(left, width=38, height=18, font=("微软雅黑", 10))
        self.eq_result.pack(pady=5)

        self.eq_fig = plt.Figure(figsize=(6, 5), dpi=100)
        self.eq_canvas = FigureCanvasTkAgg(self.eq_fig, master=page)
        self.eq_canvas.get_tk_widget().pack(side="right", padx=10, pady=10)
        self.calc_equivalent()

    def calc_equivalent(self):
        try:
            begin_mat = float(self.eq_inputs["begin_mat"].get())
            begin_labor = float(self.eq_inputs["begin_labor"].get())
            begin_mfg = float(self.eq_inputs["begin_mfg"].get())
            month_mat = float(self.eq_inputs["month_mat"].get())
            month_labor = float(self.eq_inputs["month_labor"].get())
            month_mfg = float(self.eq_inputs["month_mfg"].get())
            finish = float(self.eq_inputs["finish_qty"].get())
            wip = float(self.eq_inputs["wip_qty"].get())
            comp = float(self.eq_inputs["completion"].get()) / 100

            # 约当产量
            if self.material_mode.get() == "开工一次投入":
                mat_equivalent = wip  # 材料100%投入
            else:
                mat_equivalent = wip * comp
            labor_equivalent = wip * comp
            mfg_equivalent = wip * comp

            # 总生产费用
            total_mat = begin_mat + month_mat
            total_labor = begin_labor + month_labor
            total_mfg = begin_mfg + month_mfg

            # 单位成本
            unit_mat = total_mat / (finish + mat_equivalent)
            unit_labor = total_labor / (finish + labor_equivalent)
            unit_mfg = total_mfg / (finish + mfg_equivalent)
            unit_total = unit_mat + unit_labor + unit_mfg

            # 完工产品成本
            finish_mat = finish * unit_mat
            finish_labor = finish * unit_labor
            finish_mfg = finish * unit_mfg
            finish_total = finish * unit_total

            # 在产品成本
            wip_mat = mat_equivalent * unit_mat
            wip_labor = labor_equivalent * unit_labor
            wip_mfg = mfg_equivalent * unit_mfg
            wip_total = wip_mat + wip_labor + wip_mfg

            self.eq_result.delete("1.0", "end")
            result = f"""
【成本计算单】
成本项目  总费用  单位成本  完工成本  在产品成本
直接材料  {total_mat:,.2f}  {unit_mat:.2f}   {finish_mat:,.2f}  {wip_mat:,.2f}
直接人工  {total_labor:,.2f}  {unit_labor:.2f}   {finish_labor:,.2f}  {wip_labor:,.2f}
制造费用  {total_mfg:,.2f}  {unit_mfg:.2f}   {finish_mfg:,.2f}  {wip_mfg:,.2f}
合计    {total_mat+total_labor+total_mfg:,.2f}  {unit_total:.2f}   {finish_total:,.2f}  {wip_total:,.2f}

【约当产量计算】
材料约当产量：{mat_equivalent:.0f} 件
人工约当产量：{labor_equivalent:.0f} 件
制造费用约当产量：{mfg_equivalent:.0f} 件
完工产品产量：{finish:.0f} 件

说明：
材料{self.material_mode.get()}，加工费用按完工程度计算
单位成本 = 总生产费用 ÷（完工产量+在产品约当产量）
"""
            self.eq_result.insert("end", result)

            # 成本构成图
            self.eq_fig.clear()
            ax = self.eq_fig.add_subplot(111)
            items = ["直接材料", "直接人工", "制造费用"]
            finish_vals = [finish_mat, finish_labor, finish_mfg]
            wip_vals = [wip_mat, wip_labor, wip_mfg]
            x = np.arange(3)
            width = 0.35

            ax.bar(x - width/2, finish_vals, width, label="完工产品", color="#10b981")
            ax.bar(x + width/2, wip_vals, width, label="在产品", color="#f59e0b")

            ax.set_xticks(x)
            ax.set_xticklabels(items)
            ax.set_ylabel("金额(元)")
            ax.set_title("完工与在产品成本构成")
            ax.legend()
            ax.grid(axis="y", alpha=0.3)
            self.eq_canvas.draw()

        except ValueError:
            messagebox.showerror("错误", "请输入有效数字！")

    # ===================== 6. 品种法成本计算 =====================
    def build_variety_page(self):
        page = ttk.Frame(self.notebook)
        self.notebook.add(page, text="品种法成本计算")

        left = tk.Frame(page, padx=20, pady=20)
        left.pack(side="left", fill="y")

        tk.Label(left, text="产品成本计算-品种法", font=("微软雅黑", 12, "bold")).pack(anchor="w", pady=(0,10))

        self.variety_inputs = {}
        items = [
            ("产品名称", "name", "甲产品"),
            ("本月完工产量(件)", "finish_qty", "100"),
            ("月末在产品数量(件)", "wip_qty", "20"),
            ("在产品完工程度(%)", "completion", "50"),
            ("直接材料总额(元)", "mat_total", "12000"),
            ("直接人工总额(元)", "labor_total", "6600"),
            ("制造费用总额(元)", "mfg_total", "4400"),
        ]
        for label, key, default in items:
            row = tk.Frame(left)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label, width=20, anchor="w").pack(side="left")
            entry = tk.Entry(row, width=12)
            entry.insert(0, default)
            entry.pack(side="right")
            self.variety_inputs[key] = entry

        tk.Button(left, text="生成成本计算单", command=self.calc_variety,
                  width=20, bg="#b45309", fg="white").pack(pady=15)

        self.variety_result = tk.Text(left, width=38, height=18, font=("微软雅黑", 10))
        self.variety_result.pack(pady=5)

        self.variety_fig = plt.Figure(figsize=(6, 5), dpi=100)
        self.variety_canvas = FigureCanvasTkAgg(self.variety_fig, master=page)
        self.variety_canvas.get_tk_widget().pack(side="right", padx=10, pady=10)
        self.calc_variety()

    def calc_variety(self):
        try:
            name = self.variety_inputs["name"].get()
            finish = float(self.variety_inputs["finish_qty"].get())
            wip = float(self.variety_inputs["wip_qty"].get())
            comp = float(self.variety_inputs["completion"].get()) / 100
            mat = float(self.variety_inputs["mat_total"].get())
            labor = float(self.variety_inputs["labor_total"].get())
            mfg = float(self.variety_inputs["mfg_total"].get())

            # 约当产量（材料一次投入，加工逐步）
            mat_eq = wip
            labor_eq = wip * comp
            mfg_eq = wip * comp

            # 单位成本
            unit_mat = mat / (finish + mat_eq)
            unit_labor = labor / (finish + labor_eq)
            unit_mfg = mfg / (finish + mfg_eq)
            unit_total = unit_mat + unit_labor + unit_mfg

            # 完工总成本
            finish_mat = finish * unit_mat
            finish_labor = finish * unit_labor
            finish_mfg = finish * unit_mfg
            finish_total = finish * unit_total

            # 在产品成本
            wip_mat = mat_eq * unit_mat
            wip_labor = labor_eq * unit_labor
            wip_mfg = mfg_eq * unit_mfg
            wip_total = wip_mat + wip_labor + wip_mfg

            self.variety_result.delete("1.0", "end")
            result = f"""
【产品成本计算单】
产品名称：{name}    产量：{finish:.0f}件

成本项目  总成本  单位成本  完工总成本  月末在产品
直接材料  {mat:,.2f}  {unit_mat:.2f}   {finish_mat:,.2f}   {wip_mat:,.2f}
直接人工  {labor:,.2f}  {unit_labor:.2f}   {finish_labor:,.2f}   {wip_labor:,.2f}
制造费用  {mfg:,.2f}  {unit_mfg:.2f}   {finish_mfg:,.2f}   {wip_mfg:,.2f}
合计    {mat+labor+mfg:,.2f}  {unit_total:.2f}   {finish_total:,.2f}   {wip_total:,.2f}

成本项目构成：
直接材料占比：{mat/(mat+labor+mfg)*100:.2f}%
直接人工占比：{labor/(mat+labor+mfg)*100:.2f}%
制造费用占比：{mfg/(mat+labor+mfg)*100:.2f}%
"""
            self.variety_result.insert("end", result)

            # 完工产品成本构成饼图
            self.variety_fig.clear()
            ax = self.variety_fig.add_subplot(111)
            ax.pie([finish_mat, finish_labor, finish_mfg],
                   labels=["直接材料", "直接人工", "制造费用"],
                   autopct="%1.1f%%",
                   colors=["#3b82f6", "#10b981", "#f59e0b"], startangle=90)
            ax.set_title(f"{name}完工产品成本构成")
            self.variety_canvas.draw()

        except ValueError:
            messagebox.showerror("错误", "请输入有效数字！")

    # ===================== 7. 成本报表分析 =====================
    def build_analysis_page(self):
        page = ttk.Frame(self.notebook)
        self.notebook.add(page, text="成本报表分析")

        left = tk.Frame(page, padx=20, pady=20)
        left.pack(side="left", fill="y")

        tk.Label(left, text="可比产品成本分析", font=("微软雅黑", 12, "bold")).pack(anchor="w", pady=(0,10))

        self.analysis_inputs = {}
        items = [
            ("可比产品产量(件)", "qty", "500"),
            ("上年实际平均单位成本", "last_year", "120"),
            ("本年计划单位成本", "plan", "115"),
            ("本年实际单位成本", "actual", "112"),
        ]
        for label, key, default in items:
            row = tk.Frame(left)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, width=20, anchor="w").pack(side="left")
            entry = tk.Entry(row, width=12)
            entry.insert(0, default)
            entry.pack(side="right")
            self.analysis_inputs[key] = entry

        tk.Button(left, text="计算成本降低指标", command=self.calc_analysis,
                  width=20, bg="#be123c", fg="white").pack(pady=15)

        self.analysis_result = tk.Text(left, width=38, height=16, font=("微软雅黑", 10))
        self.analysis_result.pack(pady=5)

        self.analysis_fig = plt.Figure(figsize=(6, 5), dpi=100)
        self.analysis_canvas = FigureCanvasTkAgg(self.analysis_fig, master=page)
        self.analysis_canvas.get_tk_widget().pack(side="right", padx=10, pady=10)
        self.calc_analysis()

    def calc_analysis(self):
        try:
            qty = float(self.analysis_inputs["qty"].get())
            last = float(self.analysis_inputs["last_year"].get())
            plan = float(self.analysis_inputs["plan"].get())
            actual = float(self.analysis_inputs["actual"].get())

            # 按上年计算总成本
            total_last = qty * last
            total_plan = qty * plan
            total_actual = qty * actual

            # 实际比上年降低
            reduce_amt = total_last - total_actual
            reduce_rate = reduce_amt / total_last * 100
            # 实际比计划降低
            plan_reduce_amt = total_plan - total_actual
            plan_reduce_rate = plan_reduce_amt / total_plan * 100

            self.analysis_result.delete("1.0", "end")
            result = f"""
【可比产品成本分析】
可比产品产量：{qty:.0f} 件

按上年平均单位成本：{total_last:,.2f} 元
按本年计划单位成本：{total_plan:,.2f} 元
本年实际总成本：  {total_actual:,.2f} 元

【实际比上年】
成本降低额：{reduce_amt:,.2f} 元
成本降低率：{reduce_rate:.2f}%

【实际比计划】
成本降低额：{plan_reduce_amt:,.2f} 元
成本降低率：{plan_reduce_rate:.2f}%

分析结论：
{"✅ 完成成本降低任务" if reduce_amt > 0 else "❌ 未完成成本降低任务"}
"""
            self.analysis_result.insert("end", result)

            # 对比柱状图
            self.analysis_fig.clear()
            ax = self.analysis_fig.add_subplot(111)
            items = ["上年实际", "本年计划", "本年实际"]
            values = [total_last, total_plan, total_actual]
            colors = ["#8b5cf6", "#3b82f6", "#10b981"]
            bars = ax.bar(items, values, color=colors, width=0.6)
            for bar, val in zip(bars, values):
                ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+1000,
                        f"{val:,.0f}", ha="center")
            ax.set_title("可比产品总成本对比")
            ax.set_ylabel("总成本(元)")
            ax.grid(axis="y", alpha=0.3)
            self.analysis_canvas.draw()

        except ValueError:
            messagebox.showerror("错误", "请输入有效数字！")


if __name__ == "__main__":
    app = CostAccountingSim()
    app.mainloop()
