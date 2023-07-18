# LFA

LFA (Log File Abstraction) is a log parsing approach that extends over SLCT. SLCT cannot abstract event templates for all log messages. In LFA, token frequencies are compared within each log message instead of across all log messages, thus parameters can be identified by distinguishing token frequencies within a log message.

Read more information about LFA from the following paper:

+ Meiyappan Nagappan, Mladen A. Vouk. [Abstracting Log Lines to Log Event Types for Mining Software System Logs](http://www.se.rit.edu/~mei/publications/pdfs/Abstracting-Log-Lines-to-Log-Event-Types-for-Mining-Software-System-Logs.pdf), *Proceedings of the International Working Conference on Mining Software Repositories (MSR)*, 2010.

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
|     HDFS    | 0.999545   | 0.885    |
|    Hadoop   | 0.998121   | 0.9      |
|    Spark    | 0.999968   | 0.9935   |
|  Zookeeper  | 0.998478   | 0.8385   |
|     BGL     | 0.997902   | 0.854    |
|     HPC     | 0.975881   | 0.8165   |
| Thunderbird | 0.998657   | 0.6485   |
|   Windows   | 0.9102     | 0.588    |
|    Linux    | 0.581437   | 0.2785   |
|   Android   | 0.922051   | 0.616    |
|  HealthApp  | 0.916975   | 0.5485   |
|    Apache   | 1          | 1        |
|  Proxifier  | 0.80148    | 0.0255   |
|   OpenSSH   | 0.977016   | 0.5005   |
|  OpenStack  | 0.901897   | 0.2      |
|     Mac     | 0.933583   | 0.599    |


### Citation

:telescope: If you use our logparser tools or benchmarking results in your publication, please kindly cite the following papers.

+ [**ICSE'19**] Jieming Zhu, Shilin He, Jinyang Liu, Pinjia He, Qi Xie, Zibin Zheng, Michael R. Lyu. [Tools and Benchmarks for Automated Log Parsing](https://arxiv.org/pdf/1811.03509.pdf). *International Conference on Software Engineering (ICSE)*, 2019.
+ [**DSN'16**] Pinjia He, Jieming Zhu, Shilin He, Jian Li, Michael R. Lyu. [An Evaluation Study on Log Parsing and Its Use in Log Mining](https://jiemingzhu.github.io/pub/pjhe_dsn2016.pdf). *IEEE/IFIP International Conference on Dependable Systems and Networks (DSN)*, 2016.

