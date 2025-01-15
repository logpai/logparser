import matplotlib.pyplot as plt
import numpy as np

labels = ['Drain', 'Spell', 'Our Method']
precision = [0.9, 0.92, 0.99]
recall = [0.88, 0.91, 0.98]
f1_value = [0.89, 0.915, 0.985]

x = np.arange(len(labels))
width = 0.2

fig, ax = plt.subplots()
ax.bar(x - width, precision, width, label='Precision')
ax.bar(x, recall, width, label='Recall')
ax.bar(x + width, f1_value, width, label='F1 Value')

ax.set_xlabel('Methods')
ax.set_ylabel('Values')
ax.set_title('Comparison of Methods')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()

plt.show()