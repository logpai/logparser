import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO

data_str = """Dataset,Algorithm,TimeToken,TemplateSize
HDFS_5w,Drain,0:00:02.219004,16
HDFS_5w,Spell,0:00:02.398902,13
HDFS_5w,HLM_Parser_S,0:00:02.285563,14
HDFS_5w,Drain_A,0:00:02.839519,16
HDFS_5w,Spell_A,0:00:02.366394,13
HDFS_5w,HLM_Parser,0:00:02.690298,14
HDFS_10w,Drain,0:00:04.605934,20
HDFS_10w,Spell,0:00:04.889888,17
HDFS_10w,HLM_Parser_S,0:00:04.595991,18
HDFS_10w,Drain_A,0:00:05.552280,20
HDFS_10w,Spell_A,0:00:05.033182,17
HDFS_10w,HLM_Parser,0:00:05.496426,18
HDFS_15w,Drain,0:00:06.878725,25
HDFS_15w,Spell,0:00:07.430257,22
HDFS_15w,HLM_Parser_S,0:00:06.936391,22
HDFS_15w,Drain_A,0:00:08.237755,25
HDFS_15w,Spell_A,0:00:07.224823,22
HDFS_15w,HLM_Parser,0:00:08.179232,22
HDFS_20w,Drain,0:00:09.386087,25
HDFS_20w,Spell,0:00:09.681421,22
HDFS_20w,HLM_Parser_S,0:00:09.466780,22
HDFS_20w,Drain_A,0:00:11.614381,25
HDFS_20w,Spell_A,0:00:10.058407,22
HDFS_20w,HLM_Parser,0:00:11.144340,23
BGL_5w,Drain,0:00:01.907647,68
BGL_5w,Spell,0:00:02.078338,180
BGL_5w,HLM_Parser_S,0:00:02.086663,68
BGL_5w,Drain_A,0:00:01.993392,68
BGL_5w,Spell_A,0:00:02.054959,180
BGL_5w,HLM_Parser,0:00:02.390845,68
BGL_10w,Drain,0:00:03.754315,70
BGL_10w,Spell,0:00:04.228793,253
BGL_10w,HLM_Parser_S,0:00:03.917973,70
BGL_10w,Drain_A,0:00:04.683585,70
BGL_10w,Spell_A,0:00:04.443231,253
BGL_10w,HLM_Parser,0:00:04.213192,70
BGL_15w,Drain,0:00:06.468234,74
BGL_15w,Spell,0:00:07.106304,299
BGL_15w,HLM_Parser_S,0:00:06.445330,74
BGL_15w,Drain_A,0:00:06.421960,74
BGL_15w,Spell_A,0:00:06.290827,299
BGL_15w,HLM_Parser,0:00:06.442239,74
BGL_20w,Drain,0:00:08.023953,149
BGL_20w,Spell,0:00:08.907729,418
BGL_20w,HLM_Parser_S,0:00:08.059582,140
BGL_20w,Drain_A,0:00:07.788921,149
BGL_20w,Spell_A,0:00:08.033090,419
BGL_20w,HLM_Parser,0:00:07.771927,145
"""

df = pd.read_csv(StringIO(data_str))
df.head()

df['Time_in_seconds'] = pd.to_timedelta(df['TimeToken']).dt.total_seconds()
df.head()

# 设置画布和风格
sns.set(style="whitegrid")
datasets = df['Dataset'].unique()

fig, axes = plt.subplots(nrows=len(datasets), ncols=1, figsize=(8, 4 * len(datasets)))

for i, dataset in enumerate(datasets):
    subset = df[df['Dataset'] == dataset]
    ax = axes[i] if len(datasets) > 1 else axes
    sns.barplot(
        data=subset,
        x='Algorithm',
        y='Time_in_seconds',
        ax=ax,
        palette='Set2'
    )
    ax.set_title(f"Time Comparison for {dataset}")
    ax.set_ylabel("Time (seconds)")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')

plt.tight_layout()
plt.show()

fig, ax = plt.subplots(figsize=(10, 6))

# 为了让横轴有序，可以对 Dataset 按“_5w/_10w/_15w/_20w”排序
df['DatasetOrder'] = df['Dataset'].apply(lambda x: int(x.split('_')[-1].replace('w','')))

# 按算法分组再画图
for alg in df['Algorithm'].unique():
    subset = df[df['Algorithm'] == alg].sort_values('DatasetOrder')
    ax.plot(subset['Dataset'], subset['Time_in_seconds'], marker='o', label=alg)

ax.set_title("Time Comparison Across Datasets by Algorithm")
ax.set_xlabel("Dataset")
ax.set_ylabel("Time (seconds)")
ax.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(data=df, x='Dataset', y='TemplateSize', hue='Algorithm', palette='Set3')
ax.set_title("Template Size Comparison by Dataset & Algorithm")
ax.set_xlabel("Dataset")
ax.set_ylabel("Template Size")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

