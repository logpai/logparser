# SLCT

SLCT (Simple Logfile Clustering Tool) is a tool that was designed to find clusters in logfile(s), so that each cluster corresponds to a certain line pattern that occurs frequently enough. With the help of SLCT, one can quickly build a model of logfile(s), and also identify rare lines that do not fit the model (and are possibly anomalous).

To provide a common interface for log parsing, we write a Python wrapper around the [original SLCT source code in C](http://ristov.github.io/slct/slct-0.05.tar.gz). This also eases our benchmarking experiments. Same with the original release, our implementation has only been tested successfully on Linux with GCC. We tried running the tool on Windows using cygwin with GCC installed, but failed with a crash. You are advised to use the SLCT tool on Linux. But it is still possible to work around the issue if some efforts are made.

Read more information about SLCT from the following paper:

+ Risto Vaarandi. [A Data Clustering Algorithm for Mining Patterns from Event Logs](http://www.quretec.com/u/vilo/edu/2003-04/DM_seminar_2003_II/ver1/P12/slct-ipom03-web.pdf), *Proceedings of the 3rd IEEE Workshop on IP Operations & Management (IPOM)*, 2003.

### Running

The code has been tested in the following enviornment:

+ gcc 7.5.0
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
|     HDFS    | 0.965812   | 0.545    |
|    Hadoop   | 0.811246   | 0.422    |
|    Spark    | 0.80456    | 0.685    |
|  Zookeeper  | 0.923766   | 0.7255   |
|     BGL     | 0.955247   | 0.5725   |
|     HPC     | 0.979433   | 0.8385   |
| Thunderbird | 0.988334   | 0.882    |
|   Windows   | 0.907062   | 0.6965   |
|    Linux    | 0.556248   | 0.2965   |
|   Android   | 0.983652   | 0.8815   |
|  HealthApp  | 0.811914   | 0.331    |
|    Apache   | 0.942897   | 0.7305   |
|  Proxifier  | 0.775799   | 0.518    |
|   OpenSSH   | 0.975529   | 0.521    |
|  OpenStack  | 0.973587   | 0.867    |
|     Mac     | 0.882471   | 0.5575   |

### Citation

:telescope: If you use our logparser tools or benchmarking results in your publication, please kindly cite the following papers.

+ [**ICSE'19**] Jieming Zhu, Shilin He, Jinyang Liu, Pinjia He, Qi Xie, Zibin Zheng, Michael R. Lyu. [Tools and Benchmarks for Automated Log Parsing](https://arxiv.org/pdf/1811.03509.pdf). *International Conference on Software Engineering (ICSE)*, 2019.
+ [**DSN'16**] Pinjia He, Jieming Zhu, Shilin He, Jian Li, Michael R. Lyu. [An Evaluation Study on Log Parsing and Its Use in Log Mining](https://jiemingzhu.github.io/pub/pjhe_dsn2016.pdf). *IEEE/IFIP International Conference on Dependable Systems and Networks (DSN)*, 2016.
