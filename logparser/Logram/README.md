# Logram

Logram is an automated log parsing technique, which leverages n-gram dictionaries to achieve efficient log parsing. 

Read more information about Logram from the following paper:

+ Hetong Dai, Heng Li, Che-Shao Chen, Weiyi Shang, and Tse-Hsun (Peter) Chen. [Logram: Efficient Log Parsing Using n-Gram
Dictionaries](https://arxiv.org/pdf/2001.03038.pdf), *IEEE Transactions on Software Engineering (TSE)*, 2020.

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
|:-----------:|:----------|:--------|
|     HDFS    | 0.990518   | 0.93     |
|    Hadoop   | 0.78249    | 0.451    |
|    Spark    | 0.479691   | 0.282    |
|  Zookeeper  | 0.923936   | 0.7235   |
|     BGL     | 0.956032   | 0.587    |
|     HPC     | 0.993748   | 0.9105   |
| Thunderbird | 0.993876   | 0.554    |
|   Windows   | 0.913735   | 0.694    |
|    Linux    | 0.541378   | 0.361    |
|   Android   | 0.975017   | 0.7945   |
|  HealthApp  | 0.587935   | 0.2665   |
|    Apache   | 0.637665   | 0.3125   |
|  Proxifier  | 0.750476   | 0.5035   |
|   OpenSSH   | 0.979348   | 0.6115   |
|  OpenStack  | 0.742866   | 0.3255   |
|     Mac     | 0.892896   | 0.568    |


### Citation

:telescope: If you use our logparser tools or benchmarking results in your publication, please kindly cite the following papers.

+ [**ICSE'19**] Jieming Zhu, Shilin He, Jinyang Liu, Pinjia He, Qi Xie, Zibin Zheng, Michael R. Lyu. [Tools and Benchmarks for Automated Log Parsing](https://arxiv.org/pdf/1811.03509.pdf). *International Conference on Software Engineering (ICSE)*, 2019.
+ [**DSN'16**] Pinjia He, Jieming Zhu, Shilin He, Jian Li, Michael R. Lyu. [An Evaluation Study on Log Parsing and Its Use in Log Mining](https://jiemingzhu.github.io/pub/pjhe_dsn2016.pdf). *IEEE/IFIP International Conference on Dependable Systems and Networks (DSN)*, 2016.
