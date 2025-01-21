import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import ScalarFormatter

# 设置英文字体为 Times New Roman，中文字体为 宋体
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.sans-serif'] = ['SimSun']

# 1. 原始数据
raw_data = [
    # HDFS
    ("HDFS_25%", "Drain", 42),
    ("HDFS_25%", "Spell", 34),
    ("HDFS_25%", "HLM_Parser_S", 34),
    ("HDFS_25%", "Drain_A", 42),
    ("HDFS_25%", "HLM_Parser", 35),
    ("HDFS_50%", "Drain", 44),
    ("HDFS_50%", "Spell", 34),
    ("HDFS_50%", "HLM_Parser_S", 34),
    ("HDFS_50%", "Drain_A", 44),
    ("HDFS_50%", "HLM_Parser", 36),
    ("HDFS_75%", "Drain", 46),
    ("HDFS_75%", "Spell", 36),
    ("HDFS_75%", "HLM_Parser_S", 36),
    ("HDFS_75%", "Drain_A", 46),
    ("HDFS_75%", "HLM_Parser", 39),
    ("HDFS_100%", "Drain", 48),
    ("HDFS_100%", "Spell", 37),
    ("HDFS_100%", "HLM_Parser_S", 37),
    ("HDFS_100%", "Drain_A", 48),
    ("HDFS_100%", "HLM_Parser", 43),

    # BGL
    ("BGL_25%", "Drain", 339),
    ("BGL_25%", "Spell", 729),
    ("BGL_25%", "HLM_Parser_S", 302),
    ("BGL_25%", "Drain_A", 339),
    ("BGL_25%", "HLM_Parser", 310),
    ("BGL_50%", "Drain", 1046),
    ("BGL_50%", "Spell", 911),
    ("BGL_50%", "HLM_Parser_S", 370),
    ("BGL_50%", "Drain_A", 1046),
    ("BGL_50%", "HLM_Parser", 381),
    ("BGL_75%", "Drain", 2544),
    ("BGL_75%", "Spell", 1587),
    ("BGL_75%", "HLM_Parser_S", 754),
    ("BGL_75%", "Drain_A", 2544),
    ("BGL_75%", "HLM_Parser", 775),
    ("BGL_100%", "Drain", 3819),
    ("BGL_100%", "Spell", 24444),  # 超大值
    ("BGL_100%", "HLM_Parser_S", 1681),
    ("BGL_100%", "Drain_A", 3819),
    ("BGL_100%", "HLM_Parser", 1708),

    # OpenStack
    ("OpenStack_25%", "Drain", 40),
    ("OpenStack_25%", "Spell", 772),
    ("OpenStack_25%", "HLM_Parser_S", 40),
    ("OpenStack_25%", "Drain_A", 40),
    ("OpenStack_25%", "HLM_Parser", 40),
    ("OpenStack_50%", "Drain", 40),
    ("OpenStack_50%", "Spell", 1502),
    ("OpenStack_50%", "HLM_Parser_S", 40),
    ("OpenStack_50%", "Drain_A", 40),
    ("OpenStack_50%", "HLM_Parser", 40),
    ("OpenStack_75%", "Drain", 40),
    ("OpenStack_75%", "Spell", 2229),
    ("OpenStack_75%", "HLM_Parser_S", 40),
    ("OpenStack_75%", "Drain_A", 40),
    ("OpenStack_75%", "HLM_Parser", 40),
    ("OpenStack_100%", "Drain", 43),
    ("OpenStack_100%", "Spell", 2670),
    ("OpenStack_100%", "HLM_Parser_S", 43),
    ("OpenStack_100%", "Drain_A", 43),
    ("OpenStack_100%", "HLM_Parser", 43),
]

df = pd.DataFrame(raw_data, columns=["Dataset", "Algorithm", "TemplateSize"])


# 将像 "BGL_25%" 拆分成 (DatasetName="BGL", Portion="25%")
def split_dataset_and_portion(ds_str):
    parts = ds_str.split("_")
    dataset_name = parts[0]  # HDFS / BGL / OpenStack
    portion_str = parts[1]  # 25% / 50% / 75% / 100%
    return dataset_name, portion_str


df[["DatasetName", "Portion"]] = df["Dataset"].apply(lambda x: pd.Series(split_dataset_and_portion(x)))

# 要绘制的 3 个子图
datasets = ["HDFS", "BGL", "OpenStack"]
portion_order = ["25%", "50%", "75%", "100%"]

algo_order = ["Drain", "Spell", "HLM_Parser_S", "Drain_A", "HLM_Parser"]
marker_list = ["o", "s", "^", "D", "x"]
colors = sns.color_palette("Set2", len(algo_order))

sns.set_style("white")  # 去网格
fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(18, 5), sharey=False)

for idx, dsname in enumerate(datasets):
    ax = axes[idx]
    df_sub = df[df["DatasetName"] == dsname].copy()

    # 对每种算法分别画线
    for i, algo in enumerate(algo_order):
        sub_algo = df_sub[df_sub["Algorithm"] == algo].copy()
        sub_algo["Portion"] = pd.Categorical(sub_algo["Portion"], categories=portion_order, ordered=True)
        sub_algo.sort_values("Portion", inplace=True)

        # 画折线
        ax.plot(
            sub_algo["Portion"],
            sub_algo["TemplateSize"],
            marker=marker_list[i],
            label=algo,
            markersize=8,
            color=colors[i],
            fillstyle='none',
            linewidth=1.5
        )

        # 显示数值
        for x_val, y_val in zip(sub_algo["Portion"], sub_algo["TemplateSize"]):
            ax.annotate(f'{y_val}', xy=(x_val, y_val), xytext=(0, 5),
                        textcoords="offset points", ha='center', va='bottom', fontsize=9)

    # 标题、坐标等
    ax.set_title(dsname, fontsize=14)
    ax.set_xlabel("")
    ax.set_ylabel("Number of templates", fontsize=12)
    ax.grid(False)
    ax.legend(loc='best', fontsize=9)

    # 如果是 BGL，采用对数坐标 + 自定义刻度
    if dsname == "BGL":
        ax.set_yscale('log')
        # 手动指定刻度
        custom_ticks = [300, 500, 1000, 2000, 3000, 5000, 10000, 20000, 24444]
        ax.set_yticks(custom_ticks)
        ax.set_yticklabels([str(t) for t in custom_ticks])  # 直接显示数字
        ax.set_ylim(bottom=200, top=30000)  # 自行给个上限(如 3万)让最顶部留点空白

    # 如果是 OpenStack, 也保持对数刻度(若您想要)
    elif dsname == "OpenStack":
        ax.set_yscale('log')
        # 也可做类似 BGL 的自定义, 这里示例随意
        # 例如: custom_ticks2 = [1, 40, 100, 500, 1000, 2000, 3000, 5000, 10000]
        # ax.set_yticks(custom_ticks2)
        # ...
        ax.set_ylim(bottom=1)

    else:
        # HDFS 正常线性刻度
        y_max = df_sub["TemplateSize"].max()
        ax.set_ylim(0, y_max * 1.2)

plt.tight_layout()
plt.show()