# LogMine

LogMine is one of the representative log parsers that extracts high quality patterns for a given set of log messages. The method is shown fast, memory efficient, accurate, and scalable. 

Read more information about LogMine from the following paper:

+ Hossein Hamooni, Biplob Debnath, Jianwu Xu, Hui Zhang, Geoff Jiang, Adbullah Mueen. [LogMine: Fast Pattern Recognition for Log Analytics](http://www.cs.unm.edu/~mueen/Papers/LogMine.pdf), *Proceedings of the 25th ACM International Conference on Information and Knowledge Management (CIKM)*, 2016.

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
|:-----------:|------------|----------|
|     HDFS    | 0.99884    | 0.8505   |
|    Hadoop   | 0.99553    | 0.8695   |
|    Spark    | 0.841196   | 0.5755   |
|  Zookeeper  | 0.985402   | 0.6875   |
|     BGL     | 0.970038   | 0.7245   |
|     HPC     | 0.975752   | 0.784    |
| Thunderbird | 0.998775   | 0.9185   |
|   Windows   | 0.999987   | 0.9925   |
|    Linux    | 0.938952   | 0.6115   |
|   Android   | 0.893388   | 0.504    |
|  HealthApp  | 0.917665   | 0.6865   |
|    Apache   | 1          | 1        |
|  Proxifier  | 0.719125   | 0.5165   |
|   OpenSSH   | 0.775875   | 0.4305   |
|  OpenStack  | 0.994108   | 0.743    |
|     Mac     | 0.981544   | 0.876    |

### Citation

:telescope: If you use our logparser tools or benchmarking results in your publication, please kindly cite the following papers.

+ [**ICSE'19**] Jieming Zhu, Shilin He, Jinyang Liu, Pinjia He, Qi Xie, Zibin Zheng, Michael R. Lyu. [Tools and Benchmarks for Automated Log Parsing](https://arxiv.org/pdf/1811.03509.pdf). *International Conference on Software Engineering (ICSE)*, 2019.
+ [**DSN'16**] Pinjia He, Jieming Zhu, Shilin He, Jian Li, Michael R. Lyu. [An Evaluation Study on Log Parsing and Its Use in Log Mining](https://jiemingzhu.github.io/pub/pjhe_dsn2016.pdf). *IEEE/IFIP International Conference on Dependable Systems and Networks (DSN)*, 2016.
