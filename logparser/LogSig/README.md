# LogSig

LogSig is a message signature based algorithm to generate system events from textual log messages. By searching the most representative message signatures, LogSig categorizes log messages into a set of event templates. LogSig can handle various types of log data, and is able to incorporate human's domain knowledge to achieve a high performance. We implemented LogSig using Python with a standard interface for benchmarking purpose.

Read more information about LogSig from the following paper:

+ Liang Tang, Tao Li, Chang-Shing Perng. [LogSig: Generating System Events from Raw Textual Logs](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.222.9320&rep=rep1&type=pdf), *Proceedings of the 20th ACM International Conference on Information and Knowledge Management (CIKM)*, 2011.

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
|     HDFS    | 0.878375   | 0.508    |
|    Hadoop   | 0.991263   | 0.6325   |
|    Spark    | 0.950993   | 0.5435   |
|  Zookeeper  | 0.998232   | 0.7825   |
|     BGL     | 0.933208   | 0.232    |
|     HPC     | 0.745191   | 0.382    |
| Thunderbird | 0.982687   | 0.7555   |
|   Windows   | 0.914486   | 0.6815   |
|    Linux    | 0.651881   | 0.107    |
|   Android   | 0.863749   | 0.541    |
|  HealthApp  | 0.610617   | 0.092    |
|    Apache   | 0.949806   | 0.7305   |
|  Proxifier  | 0.910655   | 0.4935   |
|   OpenSSH   | 0.969416   | 0.4405   |
|  OpenStack  | 0.996399   | 0.8385   |
|     Mac     | 0.937878   | 0.5175   |

### Citation

:telescope: If you use our logparser tools or benchmarking results in your publication, please kindly cite the following papers.

+ [**ICSE'19**] Jieming Zhu, Shilin He, Jinyang Liu, Pinjia He, Qi Xie, Zibin Zheng, Michael R. Lyu. [Tools and Benchmarks for Automated Log Parsing](https://arxiv.org/pdf/1811.03509.pdf). *International Conference on Software Engineering (ICSE)*, 2019.
+ [**DSN'16**] Pinjia He, Jieming Zhu, Shilin He, Jian Li, Michael R. Lyu. [An Evaluation Study on Log Parsing and Its Use in Log Mining](https://jiemingzhu.github.io/pub/pjhe_dsn2016.pdf). *IEEE/IFIP International Conference on Dependable Systems and Networks (DSN)*, 2016.
