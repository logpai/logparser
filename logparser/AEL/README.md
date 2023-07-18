## AEL

AEL (Abstracting Execution Logs) is one of the state-of-the-art log parsing approaches, which comprises four steps: anonymize, tokenize, categorize, and reconcile. In particular, in the reconcile step, the original algorithm merges events that have only a different token. However, this process cannot handle the cases where one single template multiple different parameter tokens. To improve the generability of this algorithm, we use a parameter merge_percent to set the percentage of different tokens when merging two events.

Read more information about AEL from the following paper:

+ Zhen Ming Jiang, Ahmed E. Hassan, Gilbert Hamann, Parminder Flora. [An Automated Approach for Abstracting Execution Logs to Execution Events](http://www.cse.yorku.ca/~zmjiang/publications/jsme2008.pdf), *Journal of Software Maintenance and Evolution: Research and Practice (JSME)*, 2008.


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
|:-----------:|:--------------|:------------|
|     HDFS    | 0.999984       | 0.9975       |
|    Hadoop   | 0.995869       | 0.869        |
|    Spark    | 0.991018       | 0.905        |
|  Zookeeper  | 0.995291       | 0.921        |
|     BGL     | 0.999554       | 0.957        |
|     HPC     | 0.992206       | 0.903        |
| Thunderbird | 0.99913        | 0.941        |
|   Windows   | 0.999281       | 0.6895       |
|    Linux    | 0.99235        | 0.6725       |
|   Android   | 0.940411       | 0.6815       |
|  HealthApp  | 0.863969       | 0.5675       |
|    Apache   | 1              | 1            |
|  Proxifier  | 0.786336       | 0.495        |
|   OpenSSH   | 0.987212       | 0.538        |
|  OpenStack  | 0.986042       | 0.7575       |
|     Mac     | 0.962113       | 0.7635       |


### Citation

:telescope: If you use our logparser tools or benchmarking results in your publication, please kindly cite the following papers.

+ [**ICSE'19**] Jieming Zhu, Shilin He, Jinyang Liu, Pinjia He, Qi Xie, Zibin Zheng, Michael R. Lyu. [Tools and Benchmarks for Automated Log Parsing](https://arxiv.org/pdf/1811.03509.pdf). *International Conference on Software Engineering (ICSE)*, 2019.
+ [**DSN'16**] Pinjia He, Jieming Zhu, Shilin He, Jian Li, Michael R. Lyu. [An Evaluation Study on Log Parsing and Its Use in Log Mining](https://jiemingzhu.github.io/pub/pjhe_dsn2016.pdf). *IEEE/IFIP International Conference on Dependable Systems and Networks (DSN)*, 2016.
