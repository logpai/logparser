import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO

# 1. 构造数据
data = [
    ["HDFS_25%",  "Drain",          42],
    ["HDFS_25%",  "Spell",          34],
    ["HDFS_25%",  "HLM_Parser_S",   34],
    ["HDFS_25%",  "Drain_A",        42],
    ["HDFS_25%",  "Spell_A",        34],
    ["HDFS_25%",  "HLM_Parser",     35],

    ["HDFS_50%",  "Drain",          44],
    ["HDFS_50%",  "Spell",          34],
    ["HDFS_50%",  "HLM_Parser_S",   34],
    ["HDFS_50%",  "Drain_A",        44],
    ["HDFS_50%",  "Spell_A",        34],
    ["HDFS_50%",  "HLM_Parser",     36],

    ["HDFS_75%",  "Drain",          46],
    ["HDFS_75%",  "Spell",          36],
    ["HDFS_75%",  "HLM_Parser_S",   36],
    ["HDFS_75%",  "Drain_A",        46],
    ["HDFS_75%",  "Spell_A",        36],
    ["HDFS_75%",  "HLM_Parser",     39],

    ["HDFS_100%", "Drain",          48],
    ["HDFS_100%", "Spell",          37],
    ["HDFS_100%", "HLM_Parser_S",   37],
    ["HDFS_100%", "Drain_A",        48],
    ["HDFS_100%", "Spell_A",        37],
    ["HDFS_100%", "HLM_Parser",     43]
]

df = pd.DataFrame(data, columns=["Dataset", "Algorithm", "TemplateSize"])

# 2. 确保横坐标按照指定顺序显示
dataset_order = ["HDFS_25%", "HDFS_50%", "HDFS_75%", "HDFS_100%"]
df["Dataset"] = pd.Categorical(df["Dataset"], categories=dataset_order, ordered=True)

# 3. 绘图
sns.set_style("whitegrid")
plt.figure(figsize=(7, 5))

# 为每个算法单独绘制一条折线
for algo in df["Algorithm"].unique():
    subset = df[df["Algorithm"] == algo].sort_values("Dataset")
    plt.plot(
        subset["Dataset"],
        subset["TemplateSize"],
        marker='o',
        label=algo
    )

# 自定义标题与坐标轴标签
plt.title("Comparison of Template Size on HDFS (25% ~ 100%)")
plt.xlabel("HDFS")
plt.ylabel("Number of templates")
plt.ylim(30, 50)  # 视数据情况，可微调上下限
plt.legend()
plt.tight_layout()

# 如果您在 Jupyter Notebook 中，执行到这里就能看到图；
# 若在本地脚本中运行，则需要加上这一行:
plt.show()

# 4. 如果需要将图转换为 Base64（可选）
buffer = BytesIO()
plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
buffer.seek(0)
img_base64 = base64.b64encode(buffer.read()).decode("utf-8")

print("下面是该图的 Base64 编码：\n")
print(img_base64)