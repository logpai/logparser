import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO

# 1. 构造数据
data = [
    ["HDFS_5w",  "Drain",          16],
    ["HDFS_10w", "Drain",          20],
    ["HDFS_15w", "Drain",          25],
    ["HDFS_20w", "Drain",          25],

    ["HDFS_5w",  "Drain_A",        16],
    ["HDFS_10w", "Drain_A",        20],
    ["HDFS_15w", "Drain_A",        25],
    ["HDFS_20w", "Drain_A",        25],

    ["HDFS_5w",  "HLM_Parser",     14],
    ["HDFS_10w", "HLM_Parser",     18],
    ["HDFS_15w", "HLM_Parser",     22],
    ["HDFS_20w", "HLM_Parser",     23],

    ["HDFS_5w",  "HLM_Parser_S",   14],
    ["HDFS_10w", "HLM_Parser_S",   18],
    ["HDFS_15w", "HLM_Parser_S",   22],
    ["HDFS_20w", "HLM_Parser_S",   22],

    ["HDFS_5w",  "Spell",          13],
    ["HDFS_10w", "Spell",          17],
    ["HDFS_15w", "Spell",          22],
    ["HDFS_20w", "Spell",          22],

    ["HDFS_5w",  "Spell_A",        13],
    ["HDFS_10w", "Spell_A",        17],
    ["HDFS_15w", "Spell_A",        22],
    ["HDFS_20w", "Spell_A",        22],
]

df = pd.DataFrame(data, columns=["Dataset", "Algorithm", "TemplateSize"])

# 2. 确保横坐标按照指定顺序显示
dataset_order = ["HDFS_5w", "HDFS_10w", "HDFS_15w", "HDFS_20w"]
df["Dataset"] = pd.Categorical(df["Dataset"], categories=dataset_order, ordered=True)

# 3. 画图
sns.set_style("whitegrid")
plt.figure(figsize=(6, 4))

for algo in df["Algorithm"].unique():
    subset = df[df["Algorithm"] == algo].sort_values("Dataset")
    plt.plot(
        subset["Dataset"],
        subset["TemplateSize"],
        marker='o',
        label=algo
    )

plt.title("Comparison of TemplateSize on HDFS")
plt.xlabel("HDFS")
plt.ylabel("Number of templates")
plt.xticks(rotation=0)
plt.ylim(10, 30)  # 可以根据数据范围自行调整
plt.legend()
plt.tight_layout()
plt.show()

# 4. 将图保存为 PNG 并转成 Base64，直接在此处输出
buffer = BytesIO()
plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
buffer.seek(0)
img_base64 = base64.b64encode(buffer.read()).decode("utf-8")

print("下面是该图的 Base64 编码：\n")
print(img_base64)