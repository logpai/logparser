# MoLFI

MoLFI (Multi-objective Log message Format Identification) is a tool implementing a search-based approach to solve the problem of log message format identification. MoLFI uses an evolutionary approach based on NSGA-II to solve this problem.

MoLFI applies the following steps:

1. Pre-processing the log file (detect trivial variable parts using domain knowledge).
2. Run NSGA-II algorithm.
3. Post-processing: apply corrections to the resulting solutions.

Read more information about MoLFI from the following paper:

+ Salma Messaoudi, Annibale Panichella, Domenico Bianculli, Lionel Briand, and Raimondas Sasnauskas. [A Search-based Approach for Accurate Identification of Log Message Formats](http://hdl.handle.net/10993/35286), *Proceedings of the 26th IEEE/ACM International Conference on Program Comprehension (ICPC)*, 2018.

### Running

The code has been tested in the following enviornment:
+ python 3.7.6
+ regex 2022.3.2
+ pandas 1.0.1
+ numpy 1.18.1
+ scipy 1.4.1
+ deap 1.4.1

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
|    Hadoop   | 0.999339   | 0.952    |
|    Spark    | 0.512882   | 0.417    |
|  Zookeeper  | 0.998413   | 0.839    |
|     BGL     | 0.999554   | 0.96     |
|     HPC     | 0.977579   | 0.8115   |
| Thunderbird | 0.998597   | 0.6435   |
|   Windows   | 0.912146   | 0.4055   |
|    Linux    | 0.722888   | 0.288    |
|   Android   | 0.853959   | 0.6275   |
|  HealthApp  | 0.782073   | 0.3205   |
|    Apache   | 1          | 1        |
|  Proxifier  | 0.742606   | 0        |
|   OpenSSH   | 0.99759    | 0.54     |
|  OpenStack  | 0.726798   | 0.213    |
|     Mac     | 0.932086   | 0.6235   |

### Citation

:telescope: If you use our logparser tools or benchmarking results in your publication, please kindly cite the following papers.

+ [**ICSE'19**] Jieming Zhu, Shilin He, Jinyang Liu, Pinjia He, Qi Xie, Zibin Zheng, Michael R. Lyu. [Tools and Benchmarks for Automated Log Parsing](https://arxiv.org/pdf/1811.03509.pdf). *International Conference on Software Engineering (ICSE)*, 2019.
+ [**DSN'16**] Pinjia He, Jieming Zhu, Shilin He, Jian Li, Michael R. Lyu. [An Evaluation Study on Log Parsing and Its Use in Log Mining](https://jiemingzhu.github.io/pub/pjhe_dsn2016.pdf). *IEEE/IFIP International Conference on Dependable Systems and Networks (DSN)*, 2016.
