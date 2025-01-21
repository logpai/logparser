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
    ("HDFS_25%", "HLM_Parser_S", 39),
    ("HDFS_25%", "Drain_A", 42),
    ("HDFS_25%", "HLM_Parser", 39),
    ("HDFS_50%", "Drain", 44),
    ("HDFS_50%", "Spell", 34),
    ("HDFS_50%", "HLM_Parser_S", 40),
    ("HDFS_50%", "Drain_A", 44),
    ("HDFS_50%", "HLM_Parser", 40),
    ("HDFS_75%", "Drain", 46),
    ("HDFS_75%", "Spell", 36),
    ("HDFS_75%", "HLM_Parser_S", 41),
    ("HDFS_75%", "Drain_A", 46),
    ("HDFS_75%", "HLM_Parser", 41),
    ("HDFS_100%", "Drain", 48),
    ("HDFS_100%", "Spell", 37),
    ("HDFS_100%", "HLM_Parser_S", 42),
    ("HDFS_100%", "Drain_A", 48),
    ("HDFS_100%", "HLM_Parser", 42),

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
    ("BGL_100%", "Spell", 24444),
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


# 2. 拆分 "BGL_25%" => (DatasetName="BGL", Portion="25%")
def split_dataset_and_portion(ds_str):
    parts = ds_str.split("_")
    dataset_name = parts[0]  # HDFS / BGL / OpenStack
    portion_str = parts[1]  # 25% / 50% / 75% / 100%
    return dataset_name, portion_str


df[["DatasetName", "Portion"]] = df["Dataset"].apply(lambda x: pd.Series(split_dataset_and_portion(x)))

# 3. 将数据集和 x 轴顺序固定
datasets = ["HDFS", "BGL", "OpenStack"]
portion_order = ["25%", "50%", "75%", "100%"]

algo_order = ["Drain", "Spell", "HLM_Parser_S", "Drain_A", "HLM_Parser"]
marker_list = ["D", "s", "^", "o", "x"]
colors = sns.color_palette("Set2", len(algo_order))

sns.set_style("white")  # 去网格
fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(18, 5), sharey=False)

for idx, dsname in enumerate(datasets):
    ax = axes[idx]
    df_sub = df[df["DatasetName"] == dsname].copy()

    # 按算法依次绘制折线，不标注数值
    for i, algo in enumerate(algo_order):
        sub_algo = df_sub[df_sub["Algorithm"] == algo].copy()
        # 保证 Portion 的有序分类
        sub_algo["Portion"] = pd.Categorical(sub_algo["Portion"], categories=portion_order, ordered=True)
        sub_algo.sort_values("Portion", inplace=True)

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

    # 设置标题、坐标等
    ax.set_title(dsname, fontsize=14)
    ax.set_xlabel("")
    ax.set_ylabel("Number of templates", fontsize=12)
    ax.grid(False)
    ax.legend(loc='best', fontsize=9)

    # 根据数据集使用不同刻度策略
    if dsname == "BGL":
        ax.set_yscale('log')
        # BGL 自定义刻度
        custom_ticks = [300, 500, 1000, 2000, 3000, 5000, 10000, 20000, 24444]
        ax.set_yticks(custom_ticks)
        ax.set_yticklabels([str(t) for t in custom_ticks])
        ax.set_ylim(bottom=300, top=30000)
    elif dsname == "OpenStack":
        ax.set_yscale('log')
        custom_ticks = [0,40,  50, 100, 500, 100, 2000, 3000]
        ax.set_yticks(custom_ticks)
        ax.set_yticklabels([str(t) for t in custom_ticks])
        ax.set_ylim(bottom=10, top=3000)
    else:  # HDFS
        ax.set_yscale('log')
        custom_ticks = [30, 35, 40, 45, 50]
        ax.set_yticks(custom_ticks)
        ax.set_yticklabels([str(t) for t in custom_ticks])
        ax.set_ylim(bottom=30, top=50)

plt.tight_layout()
plt.show()