import pandas as pd
df = pd.read_excel("报销记录.xlsx")
# 按部门、费用类型汇总
summary = df.groupby(["部门","费用科目"])["金额"].sum()
summary.to_excel("费用汇总表.xlsx")
print(summary)
