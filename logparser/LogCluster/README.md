# LogCluster

LogCluster is a Perl-based tool for log file clustering and mining line patterns from log files. The development of LogCluster was inspired by [SLCT](http://ristov.github.io/slct/), but LogCluster includes a number of novel features and data processing options. 

To provide a common interface for log parsing, we write a Python wrapper around the original [LogCluster source code in Perl](https://github.com/ristov/logcluster). This also eases our benchmarking experiments. The implementation has been tested on both Linux and Windows systems. Especially, [Strawberry Perl](http://strawberryperl.com/) has been installed to run the Perl program on Windows.

Read more information about LogCluster from the following paper:

+ Risto Vaarandi, Mauno Pihelgas. [LogCluster - A Data Clustering and Pattern Mining Algorithm for Event Logs](http://ristov.github.io/publications/cnsm15-logcluster-web.pdf), *Proceedings of the 11th International Conference on Network and Service Management (CNSM)*, 2015.

### Running

The code has been tested in the following enviornment:
+ python 3.7.6
+ regex 2022.3.2
+ pandas 1.0.1
+ numpy 1.18.1
+ scipy 1.4.1
+ perl 5.26.1

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
|     HDFS    | 0.951863   | 0.546    |
|    Hadoop   | 0.885621   | 0.563    |
|    Spark    | 0.974048   | 0.7985   |
|  Zookeeper  | 0.924229   | 0.7315   |
|     BGL     | 0.996965   | 0.835    |
|     HPC     | 0.985579   | 0.7875   |
| Thunderbird | 0.997233   | 0.5985   |
|   Windows   | 0.907275   | 0.713    |
|    Linux    | 0.921884   | 0.6285   |
|   Android   | 0.983998   | 0.7975   |
|  HealthApp  | 0.758866   | 0.5305   |
|    Apache   | 0.942418   | 0.7085   |
|  Proxifier  | 0.761671   | 0.478    |
|   OpenSSH   | 0.931467   | 0.4255   |
|  OpenStack  | 0.987363   | 0.6955   |
|     Mac     | 0.932406   | 0.6035   |

### Citation

:telescope: If you use our logparser tools or benchmarking results in your publication, please kindly cite the following papers.

+ [**ICSE'19**] Jieming Zhu, Shilin He, Jinyang Liu, Pinjia He, Qi Xie, Zibin Zheng, Michael R. Lyu. [Tools and Benchmarks for Automated Log Parsing](https://arxiv.org/pdf/1811.03509.pdf). *International Conference on Software Engineering (ICSE)*, 2019.
+ [**DSN'16**] Pinjia He, Jieming Zhu, Shilin He, Jian Li, Michael R. Lyu. [An Evaluation Study on Log Parsing and Its Use in Log Mining](https://jiemingzhu.github.io/pub/pjhe_dsn2016.pdf). *IEEE/IFIP International Conference on Dependable Systems and Networks (DSN)*, 2016.
