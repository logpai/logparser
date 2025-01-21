import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re

# 设置英文字体为 Times New Roman，中文字体为 宋体
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['axes.unicode_minus'] = False  # 用来显示负号
# 为了能显示中文，指定中文字体（如宋体）
plt.rcParams['font.sans-serif'] = ['SimSun']

# 1. 准备数据
raw_data = [
    # HDFS
    ("HDFS", "Drain", "05:19.4"),
    ("HDFS", "Spell", "05:58.9"),
    ("HDFS", "HLM-Parser_S", "04:32.3"),
    ("HDFS", "Drain_A", "07:05.9"),
    ("HDFS", "HLM-Parser", "06:12.8"),

    # BGL
    ("BGL", "Drain", "02:23.7"),
    ("BGL", "Spell", "16:22.8"),
    ("BGL", "HLM-Parser_S", "02:01.0"),
    ("BGL", "Drain_A", "03:01.6"),
    ("BGL", "HLM-Parser", "02:49.6"),

    # OpenStack
    ("OpenStack", "Drain", "00:04.8"),
    ("OpenStack", "Spell", "00:19.7"),
    ("OpenStack", "HLM-Parser_S", "00:04.4"),
    ("OpenStack", "Drain_A", "00:04.9"),
    ("OpenStack", "HLM-Parser", "00:04.5"),
]


# 2. 将字符串形式的时间解析为总秒数
def parse_time_token(t_str):
    """
    假设格式为 'MM:SS.sss' (不含小时)；
    如果有小时，可在此扩展。
    """
    match = re.match(r"(\d+):(\d+\.?\d*)", t_str)
    if match:
        minutes = int(match.group(1))
        seconds = float(match.group(2))
        return minutes * 60 + seconds
    else:
        return 0.0


df = pd.DataFrame(raw_data, columns=["Dataset", "Algorithm", "TimeToken"])
df["Time_in_seconds"] = df["TimeToken"].apply(parse_time_token)

# 3. 配置绘图布局，横向排列
fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(15, 5), sharey=False)

# 定义算法显示顺序，确保三幅图的柱子顺序一致
algo_order = ["Drain", "Spell", "HLM-Parser_S", "Drain_A", "HLM-Parser"]

# 给三个数据集分别绘制图表
datasets = ["HDFS", "BGL", "OpenStack"]

for i, dataset_name in enumerate(datasets):
    ax = axes[i]
    subset = df[df["Dataset"] == dataset_name].copy()

    # 将 Algorithm 设置为分类数据，指定顺序
    subset["Algorithm"] = pd.Categorical(subset["Algorithm"],
                                         categories=algo_order,
                                         ordered=True)
    subset.sort_values("Algorithm", inplace=True)

    # 画柱状图
    sns.barplot(
        data=subset,
        x="Algorithm",
        y="Time_in_seconds",
        ax=ax,
        palette="Set2"
    )

    # 去掉网格线
    ax.grid(False)

    # 让Y轴从0开始，并在最高值处留一些空白
    y_min = 0
    y_max = subset["Time_in_seconds"].max()
    ax.set_ylim(y_min, y_max * 1.2)

    # 设置标题与坐标轴标签
    ax.set_title(dataset_name, fontsize=14)
    ax.set_xlabel("")  # 不显示x轴标题
    ax.set_ylabel("Time (seconds)", fontsize=12)

    # 旋转横轴刻度标签，避免重叠
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right")

    # 在每个柱状图上方标注时间（秒）
    for p in ax.patches:
        ax.annotate(f'{p.get_height():.2f} sec',
                    (p.get_x() + p.get_width() / 2., p.get_height()),
                    xytext=(0, 5),  # 偏移量，避免与柱状图重叠
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=10)

plt.tight_layout()
plt.show()