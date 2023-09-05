# LenMa

LenMa is one of the representative log parsers that utilizes the token length properties of log messages for event template extraction. The authors open source [the original implementation on Github](https://github.com/keiichishima/templateminer). We further wrap up the code with the logparser interface for benchmarking purpose. 

Read more information about LenMa from the following paper:

+ Keiichi Shima. [Length Matters: Clustering System Log Messages using Length of Words](https://arxiv.org/pdf/1611.03213.pdf), *Proceedings of International Conference on Network and Service Management (CNSM)*, 2015.

### Running

The code has been tested in the following enviornment:
+ python 3.7.6
+ regex 2022.3.2
+ pandas 1.0.1
+ numpy 1.18.1
+ scipy 1.4.1
+ sklearn 0.22.1

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
|     HDFS    | 0.999984   | 0.9975   |
|    Hadoop   | 0.996539   | 0.885    |
|    Spark    | 0.989073   | 0.8835   |
|  Zookeeper  | 0.998418   | 0.8405   |
|     BGL     | 0.939369   | 0.6895   |
|     HPC     | 0.980824   | 0.8295   |
| Thunderbird | 0.999708   | 0.943    |
|   Windows   | 0.994594   | 0.5655   |
|    Linux    | 0.995105   | 0.701    |
|   Android   | 0.992152   | 0.8795   |
|  HealthApp  | 0.393984   | 0.174    |
|    Apache   | 1          | 1        |
|  Proxifier  | 0.749723   | 0.508    |
|   OpenSSH   | 0.998989   | 0.925    |
|  OpenStack  | 0.994427   | 0.7425   |
|     Mac     | 0.958653   | 0.698    |


### Citation

:telescope: If you use our logparser tools or benchmarking results in your publication, please kindly cite the following papers.

+ [**ICSE'19**] Jieming Zhu, Shilin He, Jinyang Liu, Pinjia He, Qi Xie, Zibin Zheng, Michael R. Lyu. [Tools and Benchmarks for Automated Log Parsing](https://arxiv.org/pdf/1811.03509.pdf). *International Conference on Software Engineering (ICSE)*, 2019.
+ [**DSN'16**] Pinjia He, Jieming Zhu, Shilin He, Jian Li, Michael R. Lyu. [An Evaluation Study on Log Parsing and Its Use in Log Mining](https://jiemingzhu.github.io/pub/pjhe_dsn2016.pdf). *IEEE/IFIP International Conference on Dependable Systems and Networks (DSN)*, 2016.
