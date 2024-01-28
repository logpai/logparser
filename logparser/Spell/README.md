# Spell

Spell is a structured Streaming Parser for Event Logs using an LCS (longest common subsequence) based approach. Spell parses unstructured log messages into structured message templates and parameters in an online streaming fashion. We implemented Spell using Python with a standard interface for benchmarking purpose.

Read more information about Spell from the following paper:

+ Min Du, Feifei Li. [Spell: Streaming Parsing of System Event Logs](https://www.cs.utah.edu/~lifeifei/papers/spell.pdf), *IEEE International Conference on Data Mining (ICDM)*, 2016.

### Running

The code has been tested in the following enviornment:

+ python 3.7.6
+ regex 2022.3.2
+ pandas 1.0.1
+ numpy 1.18.1
+ scipy 1.4.1

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
|:-----------:|:------------|:----------|
|     HDFS    | 1          | 1        |
|    Hadoop   | 0.920197   | 0.7775   |
|    Spark    | 0.991018   | 0.905    |
|  Zookeeper  | 0.999549   | 0.9635   |
|     BGL     | 0.956932   | 0.7865   |
|     HPC     | 0.986063   | 0.654    |
| Thunderbird | 0.994456   | 0.8435   |
|   Windows   | 0.999974   | 0.9885   |
|    Linux    | 0.936822   | 0.605    |
|   Android   | 0.992196   | 0.9185   |
|  HealthApp  | 0.886674   | 0.639    |
|    Apache   | 1          | 1        |
|  Proxifier  | 0.832044   | 0.5265   |
|   OpenSSH   | 0.918038   | 0.554    |
|  OpenStack  | 0.994108   | 0.764    |
|     Mac     | 0.963472   | 0.7565   |

### Citation

:telescope: If you use our logparser tools or benchmarking results in your publication, please kindly cite the following papers.

+ [**ICSE'19**] Jieming Zhu, Shilin He, Jinyang Liu, Pinjia He, Qi Xie, Zibin Zheng, Michael R. Lyu. [Tools and Benchmarks for Automated Log Parsing](https://arxiv.org/pdf/1811.03509.pdf). *International Conference on Software Engineering (ICSE)*, 2019.
+ [**DSN'16**] Pinjia He, Jieming Zhu, Shilin He, Jian Li, Michael R. Lyu. [An Evaluation Study on Log Parsing and Its Use in Log Mining](https://jiemingzhu.github.io/pub/pjhe_dsn2016.pdf). *IEEE/IFIP International Conference on Dependable Systems and Networks (DSN)*, 2016.
