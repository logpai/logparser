import matplotlib.pyplot as plt
from matplotlib import rcParams
import numpy as np

# 示例数据
x1 = [20, 22, 24, 26, 28, 30]  # 参数 r
x2 = [32, 64, 96, 128, 160]     # 参数 u
x3 = [1, 2, 3, 4, 5]            # 参数 L
x4 = [6, 7, 8, 9, 10]           # 参数 h

precision1 = [0.98, 0.99, 1.0, 0.99, 0.99, 0.98]
recall1 = [0.97, 0.98, 1.0, 0.98, 0.97, 0.96]
f1_1 = [0.97, 0.99, 1.0, 0.98, 0.98, 0.97]

precision2 = [0.96, 0.97, 0.98, 0.99, 0.97]
recall2 = [0.95, 0.96, 0.98, 0.97, 0.96]
f1_2 = [0.96, 0.97, 0.98, 0.98, 0.96]

precision3 = [0.99, 0.99, 1.0, 0.99, 0.99]
recall3 = [0.98, 0.98, 1.0, 0.98, 0.98]
f1_3 = [0.98, 0.99, 1.0, 0.99, 0.99]

precision4 = [0.95, 0.96, 0.97, 0.98, 0.97]
recall4 = [0.96, 0.97, 0.98, 0.99, 0.98]
f1_4 = [0.95, 0.97, 0.98, 0.99, 0.97]

# 设置字体为 SimHei (黑体) 或其他支持中文的字体
rcParams['font.sans-serif'] = ['SimHei']  # 设置默认字体
rcParams['axes.unicode_minus'] = False   # 解决负号 '-' 显示为方块的问题

# 创建子图
fig, axes = plt.subplots(2, 2, figsize=(12, 8))  # 2行2列子图

# (a) TFAD vs r
axes[0, 0].plot(x1, precision1, marker='o', label="Precision")
axes[0, 0].plot(x1, recall1, marker='x', label="Recall")
axes[0, 0].plot(x1, f1_1, marker='^', label="F1")
axes[0, 0].set_title("(a) TFAD vs r")
axes[0, 0].set_xlabel("日志模板主数量: r")
axes[0, 0].set_ylabel("Score")
axes[0, 0].legend()

# (b) TFAD vs u
axes[0, 1].plot(x2, precision2, marker='o', label="Precision")
axes[0, 1].plot(x2, recall2, marker='x', label="Recall")
axes[0, 1].plot(x2, f1_2, marker='^', label="F1")
axes[0, 1].set_title("(b) TFAD vs u")
axes[0, 1].set_xlabel("神经网络隐层大小: u")
axes[0, 1].set_ylabel("Score")
axes[0, 1].legend()

# (c) TFAD vs L
axes[1, 0].plot(x3, precision3, marker='o', label="Precision")
axes[1, 0].plot(x3, recall3, marker='x', label="Recall")
axes[1, 0].plot(x3, f1_3, marker='^', label="F1")
axes[1, 0].set_title("(c) TFAD vs L")
axes[1, 0].set_xlabel("神经网络层数: L")
axes[1, 0].set_ylabel("Score")
axes[1, 0].legend()

# (d) TFAD vs h
axes[1, 1].plot(x4, precision4, marker='o', label="Precision")
axes[1, 1].plot(x4, recall4, marker='x', label="Recall")
axes[1, 1].plot(x4, f1_4, marker='^', label="F1")
axes[1, 1].set_title("(d) TFAD vs h")
axes[1, 1].set_xlabel("日志模板主滑动窗口长度: h")
axes[1, 1].set_ylabel("Score")
axes[1, 1].legend()

# 调整子图布局
plt.tight_layout()
plt.show()