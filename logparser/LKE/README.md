# LKE

LKE (Log Key Extraction) is one of the representative algorithms for log parsing. It first leverages empirical rules for preprocessing and then uses weighted edit distance for hierarchical clustering of log messages. After further group splitting with fine tuning, log keys are generated from the resulting clusters.

Read more information about LKE from the following paper:

+ Qiang Fu, Jian-Guang Lou, Yi Wang, Jiang Li. [Execution Anomaly Detection in Distributed Systems through Unstructured Log Analysis](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/DM790-CR.pdf), *IEEE International Conference on Data Mining (ICDM)*, 2009.

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
|    Hadoop   | 0.220457   | 0        |
|    Spark    | 0.731617   | 0.6335   |
|  Zookeeper  | 0.994407   | 0.8545   |
|     BGL     | 0.942901   | 0.6455   |
|     HPC     | 0.778628   | 0.574    |
| Thunderbird | 0.982164   | 0.8125   |
|   Windows   | 0.999904   | 0.9895   |
|    Linux    | 0.925896   | 0.5185   |
|   Android   | 0.992097   | 0.9105   |
|  HealthApp  | 0.323943   | 0.2295   |
|    Apache   | 1          | 1        |
|  Proxifier  | 0.813394   | 0.495    |
|   OpenSSH   | 0.9364     | 0.4255   |
|  OpenStack  | 0.935767   | 0.787    |
|     Mac     | 0.348802   | 0.3685   |


### Citation

:telescope: If you use our logparser tools or benchmarking results in your publication, please kindly cite the following papers.

+ [**ICSE'19**] Jieming Zhu, Shilin He, Jinyang Liu, Pinjia He, Qi Xie, Zibin Zheng, Michael R. Lyu. [Tools and Benchmarks for Automated Log Parsing](https://arxiv.org/pdf/1811.03509.pdf). *International Conference on Software Engineering (ICSE)*, 2019.
+ [**DSN'16**] Pinjia He, Jieming Zhu, Shilin He, Jian Li, Michael R. Lyu. [An Evaluation Study on Log Parsing and Its Use in Log Mining](https://jiemingzhu.github.io/pub/pjhe_dsn2016.pdf). *IEEE/IFIP International Conference on Dependable Systems and Networks (DSN)*, 2016.
