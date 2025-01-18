import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO

# 1. 准备数据
data = [
    ["HDFS_25%", "Drain", "0:01:10.384538"],
    ["HDFS_25%", "Spell", "0:01:21.154015"],
    ["HDFS_25%", "HLM_Parser_S", "0:01:10.959019"],
    ["HDFS_25%", "Drain_A", "0:01:35.377905"],
    ["HDFS_25%", "Spell_A", "0:01:21.950141"],
    ["HDFS_25%", "HLM_Parser", "0:01:34.736174"],

    ["HDFS_50%", "Drain", "0:02:24.568219"],
    ["HDFS_50%", "Spell", "0:02:52.729654"],
    ["HDFS_50%", "HLM_Parser_S", "0:02:22.264511"],
    ["HDFS_50%", "Drain_A", "0:03:18.239822"],
    ["HDFS_50%", "Spell_A", "0:02:45.631801"],
    ["HDFS_50%", "HLM_Parser", "0:03:15.231407"],

    ["HDFS_75%", "Drain", "0:03:44.381771"],
    ["HDFS_75%", "Spell", "0:04:13.689505"],
    ["HDFS_75%", "HLM_Parser_S", "0:03:43.579916"],
    ["HDFS_75%", "Drain_A", "0:05:09.557604"],
    ["HDFS_75%", "Spell_A", "0:04:31.584934"],
    ["HDFS_75%", "HLM_Parser", "0:05:14.712758"],

    ["HDFS_100%", "Drain", "0:05:19.378797"],
    ["HDFS_100%", "Spell", "0:05:58.926436"],
    ["HDFS_100%", "HLM_Parser_S", "0:05:12.322213"],
    ["HDFS_100%", "Drain_A", "0:07:05.904838"],
    ["HDFS_100%", "Spell_A", "0:05:57.731851"],
    ["HDFS_100%", "HLM_Parser", "0:06:44.831548"],
]

df = pd.DataFrame(data, columns=["Dataset", "Algorithm", "TimeToken"])

# 2. 按指定顺序整理横坐标
order_list = ["HDFS_25%", "HDFS_50%", "HDFS_75%", "HDFS_100%"]
df["Dataset"] = pd.Categorical(df["Dataset"], categories=order_list, ordered=True)

# 3. 将 TimeToken 转换为秒或分钟
df["Time_in_seconds"] = pd.to_timedelta(df["TimeToken"]).dt.total_seconds()
# 如果想以分钟为单位，可以用下面这行：
# df["Time_in_minutes"] = df["Time_in_seconds"] / 60.0

# 4. 绘制折线图
sns.set_style("whitegrid")
plt.figure(figsize=(7, 5))

for algo in df["Algorithm"].unique():
    subset = df[df["Algorithm"] == algo].sort_values("Dataset")
    plt.plot(
        subset["Dataset"],
        subset["Time_in_seconds"],  # 或者 subset["Time_in_minutes"]
        marker='o',
        label=algo
    )

# 5. 设置图表信息
plt.title("Time Comparison (HDFS_25% ~ HDFS_100%)")
plt.xlabel("HDFS Scale")
plt.ylabel("Time (seconds)")  # 若用分钟则写 "Time (minutes)"
plt.xticks(rotation=0)
plt.legend()
plt.tight_layout()

# 若在脚本中运行需要 plt.show()，Jupyter 中直接运行则可显示
plt.show()

# 6. （可选）若需要生成 Base64 图片
buffer = BytesIO()
plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
buffer.seek(0)
img_base64 = base64.b64encode(buffer.read()).decode("utf-8")

print("下面是该图的 Base64 编码：\n")
print(img_base64)