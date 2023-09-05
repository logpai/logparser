# SHISO

SHISO is a method for mining log formats and retrieving log types and parameters in an online manner. By creating a structured tree using the nodes generated from log messages, SHISO refines log format continuously in realtime. We implemented SHISO using Python with a standard interface for benchmarking purpose.

Read more information about SHISO from the following paper:

+ Masayoshi Mizutani. [Incremental Mining of System Log Format](http://ieeexplore.ieee.org/document/6649746/), *IEEE International Conference on Services Computing (SCC)*, 2013.

### Running

The code has been tested in the following enviornment:
+ python 3.7.6
+ regex 2022.3.2
+ pandas 1.0.1
+ numpy 1.18.1
+ scipy 1.4.1
+ nltk 3.4.5

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
|     HDFS    | 0.999984   | 0.9975   |
|    Hadoop   | 0.997513   | 0.867    |
|    Spark    | 0.991526   | 0.906    |
|  Zookeeper  | 0.993337   | 0.66     |
|     BGL     | 0.99445    | 0.711    |
|     HPC     | 0.541336   | 0.3245   |
| Thunderbird | 0.911185   | 0.576    |
|   Windows   | 0.912983   | 0.7005   |
|    Linux    | 0.975457   | 0.6715   |
|   Android   | 0.843701   | 0.585    |
|  HealthApp  | 0.842471   | 0.397    |
|    Apache   | 1          | 1        |
|  Proxifier  | 0.77964    | 0.5165   |
|   OpenSSH   | 0.997639   | 0.619    |
|  OpenStack  | 0.993697   | 0.7215   |
|     Mac     | 0.959845   | 0.595    |

### Citation

:telescope: If you use our logparser tools or benchmarking results in your publication, please kindly cite the following papers.

+ [**ICSE'19**] Jieming Zhu, Shilin He, Jinyang Liu, Pinjia He, Qi Xie, Zibin Zheng, Michael R. Lyu. [Tools and Benchmarks for Automated Log Parsing](https://arxiv.org/pdf/1811.03509.pdf). *International Conference on Software Engineering (ICSE)*, 2019.
+ [**DSN'16**] Pinjia He, Jieming Zhu, Shilin He, Jian Li, Michael R. Lyu. [An Evaluation Study on Log Parsing and Its Use in Log Mining](https://jiemingzhu.github.io/pub/pjhe_dsn2016.pdf). *IEEE/IFIP International Conference on Dependable Systems and Networks (DSN)*, 2016.
