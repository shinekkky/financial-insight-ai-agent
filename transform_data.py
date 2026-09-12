import pandas as pd
import random

# 读取你那个原始的 CSV
try:
    df = pd.read_csv(r'D:\Desktop\论文25.暑假\数据2\300\沪深300数据.csv')
    print("成功读取原始数据！")
except:
    print("找不到文件，请确保 '沪深300数据.csv' 在 D:\PythonProject3 文件夹下")

# --- 开始改造 ---
# 1. 改名
df.rename(columns={'date': '交易日期'}, inplace=True)

# 2. 把收盘价变成金额（除以10，看着更像报销金额）
df['金额'] = df['close'].apply(lambda x: round(x / 10 + random.uniform(10, 50), 2))

# 3. 编造审计字段（让数据看起来像账本）
subjects = ['差旅费', '办公用品', '招待费', '租赁费', '技术服务费', '设备采购']
staffs = ['张伟', '王芳', '李娜', '赵强', '陈静', '刘波']
depts = ['财务部', '销售部', '研发部', '市场部', '行政部']

df['费用科目'] = [random.choice(subjects) for _ in range(len(df))]
df['经办人'] = [random.choice(staffs) for _ in range(len(df))]
df['所属部门'] = [random.choice(depts) for _ in range(len(df))]
df['备注'] = "项目周期性支出"

# 4. 挑选最终要留下的列
new_df = df[['交易日期', '费用科目', '金额', '经办人', '所属部门', '备注']]

# 5. 保存到 data 文件夹里
import os
if not os.path.exists('data'):
    os.makedirs('data')

new_df.to_excel('沪深300.xlsx', index=False)
print("🚀 改造成功！新文件已生成在：沪深300.xlsx")