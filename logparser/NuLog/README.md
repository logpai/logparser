## NuLog

Parsing semi-structured records with free-form text log messages into structured templates is the first and crucial step that enables further analysis. NuLog presents a novel parsing technique that utilizes a self-supervised learning model and formulates the parsing task as masked language modeling (MLM). In the process of parsing, the model extracts summarizations from the logs in the form of a vector embedding. This allows the coupling of the MLM as pre-training with a downstream anomaly detection task. 


### Running

Note that we modify NuLog to support both CPU and GPU devices. We run the experiments on a P100 GPU machine.

Install the required enviornment:

```
pip install -r requirements.txt
```

Run the following script to start the demo:

```
python demo.py
```

Run the following script to execute the benchmark:

```
python benchmark.py
```

### Benchmark

Running the benchmark script on Loghub_2k datasets, you could obtain the following results.

|   Dataset   | F1_measure | Accuracy |
|:-----------:|:----------|:---------|
| BGL | 0.999779 | 0.9785 |
| Android | 0.972805 | 0.831 |
| OpenStack | 0.999856 | 0.968 |
| HDFS | 0.99998 | 0.9965 |
| Apache | 1 | 1 |
| HPC | 0.994403 | 0.9465 |
| Windows | 0.999983 | 0.9945 |
| HealthApp | 0.996484 | 0.8765 |
| Mac | 0.748933 | 0.8165 |
| Spark | 0.999996 | 0.998 |

### 🔥 Citation

If you use the code or benchmarking results in your publication, please kindly cite the following papers.

+ [**PKDD'20**] Sasho Nedelkoski, Jasmin Bogatinovski, Alexander Acker, Jorge Cardoso, Odej Kao. [Self-Supervised Log Parsing](https://arxiv.org/abs/2003.07905), *Joint European Conference on Machine Learning and Knowledge Discovery in Databases (ECML-PKDD)*, 2020.
+ [**ICSE'19**] Jieming Zhu, Shilin He, Jinyang Liu, Pinjia He, Qi Xie, Zibin Zheng, Michael R. Lyu. [Tools and Benchmarks for Automated Log Parsing](https://arxiv.org/pdf/1811.03509.pdf). *International Conference on Software Engineering (ICSE)*, 2019.
