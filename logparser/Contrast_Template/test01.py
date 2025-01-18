import matplotlib.pyplot as plt

# 数据
x = [25, 50, 75, 100]
drain_hdfs = [40, 45, 48, 50]
spell_hdfs = [30, 32, 34, 35]
spella_hdfs = [20, 22, 24, 25]
ham_lcs_hdfs = [25, 28, 30, 32]

drain_openstack = [60, 65, 70, 75]
spell_openstack = [50, 55, 60, 65]
spella_openstack = [40, 45, 50, 55]
ham_lcs_openstack = [45, 50, 55, 60]

drain_linux = [300, 400, 600, 800]
spell_linux = [200, 300, 400, 500]
spella_linux = [100, 150, 200, 250]
ham_lcs_linux = [150, 200, 300, 400]

# 创建子图
fig, axs = plt.subplots(2, 2, figsize=(10, 8))

# HDFS 图表
axs[0, 0].plot(x, drain_hdfs, label="Drain", marker='s')
axs[0, 0].plot(x, spell_hdfs, label="Spell", marker='d')
axs[0, 0].plot(x, spella_hdfs, label="SpellA", marker='o')
axs[0, 0].plot(x, ham_lcs_hdfs, label="Ham-LCS", marker='^')
axs[0, 0].set_title("HDFS")
axs[0, 0].set_ylabel("Number of templates")
axs[0, 0].legend()

# Openstack 图表
axs[0, 1].plot(x, drain_openstack, label="Drain", marker='s')
axs[0, 1].plot(x, spell_openstack, label="Spell", marker='d')
axs[0, 1].plot(x, spella_openstack, label="SpellA", marker='o')
axs[0, 1].plot(x, ham_lcs_openstack, label="Ham-LCS", marker='^')
axs[0, 1].set_title("Openstack")

# Linux 图表
axs[1, 0].plot(x, drain_linux, label="Drain", marker='s')
axs[1, 0].plot(x, spell_linux, label="Spell", marker='d')
axs[1, 0].plot(x, spella_linux, label="SpellA", marker='o')
axs[1, 0].plot(x, ham_lcs_linux, label="Ham-LCS", marker='^')
axs[1, 0].set_title("Linux")
axs[1, 0].set_ylabel("Number of templates")
axs[1, 0].set_xlabel("Percentage")
axs[1, 0].legend()

# 移除右下角空白子图
fig.delaxes(axs[1, 1])

# 调整布局
plt.tight_layout()
plt.show()