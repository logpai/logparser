# IPLoM

IPLoM (Iterative Partitioning Log Mining) is one of the state-of-the-art algorithms for log parsing. It leverages the unique characteristics of log messages for iterative log partitioning, which thus enables efficient message type extraction. Since the original open-source implementation is not available anymore, we re-implement the algorithm using Python.

Read more information about IPLoM from the following papers:

+ Adetokunbo Makanju, A. Nur Zincir-Heywood, Evangelos E. Milios. [Clustering Event Logs Using Iterative Partitioning](https://web.cs.dal.ca/~makanju/publications/paper/kdd09.pdf), *ACM SIGKDD Conference on Knowledge Discovery and Data Mining (KDD)*, 2009.
+ Adetokunbo Makanju, A. Nur Zincir-Heywood, Evangelos E. Milios. [A Lightweight Algorithm for Message Type Extraction in System Application Logs](http://ieeexplore.ieee.org/abstract/document/5936060/), *IEEE Transactions on Knowledge and Data Engineering (TKDE)*, 2012.


### Running

The code has been tested in the following enviornment:
+ python 3.7.6
+ regex 2022.3.2
+ pandas 1.0.1
+ numpy 1.18.1
+ scipy 1.4.1

Run the following scripts to start the demo:

```
python demo.py
```

Run the following scripts to execute the benchmark:

```
python benchmark.py
```

### Benchmark

Running the benchmark script on Loghub_2k datasets, you could obtain the following results.

|   Dataset   | F1_measure | Accuracy |
|:-----------:|:------------|:----------|
|     HDFS    | 1          | 1        |
|    Hadoop   | 0.996377   | 0.954    |
|    Spark    | 0.991876   | 0.92     |
|  Zookeeper  | 0.999462   | 0.9615   |
|     BGL     | 0.99911    | 0.939    |
|     HPC     | 0.978379   | 0.829    |
| Thunderbird | 0.998711   | 0.663    |
|   Windows   | 0.994604   | 0.567    |
|    Linux    | 0.964118   | 0.6715   |
|   Android   | 0.949099   | 0.7115   |
|  HealthApp  | 0.95811    | 0.8215   |
|    Apache   | 1          | 1        |
|  Proxifier  | 0.786398   | 0.5165   |
|   OpenSSH   | 0.997588   | 0.54     |
|  OpenStack  | 0.909057   | 0.3305   |
|     Mac     | 0.957185   | 0.6705   |


### Citation

:telescope: If you use our logparser tools or benchmarking results in your publication, please kindly cite the following papers.

+ [**ICSE'19**] Jieming Zhu, Shilin He, Jinyang Liu, Pinjia He, Qi Xie, Zibin Zheng, Michael R. Lyu. [Tools and Benchmarks for Automated Log Parsing](https://arxiv.org/pdf/1811.03509.pdf). *International Conference on Software Engineering (ICSE)*, 2019.
+ [**DSN'16**] Pinjia He, Jieming Zhu, Shilin He, Jian Li, Michael R. Lyu. [An Evaluation Study on Log Parsing and Its Use in Log Mining](https://jiemingzhu.github.io/pub/pjhe_dsn2016.pdf). *IEEE/IFIP International Conference on Dependable Systems and Networks (DSN)*, 2016.