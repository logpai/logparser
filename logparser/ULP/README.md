# ULP

ULP (Universal Log Parsing) is a highly accurate log parsing tool, the ability to extract templates from unstructured log data. ULP learns from sample log data to recognize future log events. It combines pattern matching and frequency analysis techniques. First, log events are organized into groups using a text processing method. Frequency analysis is then applied locally to instances of the same group to identify static and dynamic content of log events. When applied to 10 log datasets of the Loghub benchmark, ULP achieves an average accuracy of 89.2%, which outperforms the accuracy of four leading log parsing tools, namely Drain, Logram, Spell and AEL. Additionally, ULP can parse up to four million log events in less than 3 minutes. ULP can be readily used by practitioners and researchers to parse effectively and efficiently large log files so as to support log analysis tasks.

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
|     HDFS    | 0.999984   | 0.9975   |
|    Hadoop   | 0.999923   | 0.9895   |
|    Spark    | 0.994593   | 0.922    |
|  Zookeeper  | 0.999876   | 0.9925   |
|     BGL     | 0.999453   | 0.93     |
|     HPC     | 0.994433   | 0.9505   |
| Thunderbird | 0.998665   | 0.6755   |
|   Windows   | 0.989051   | 0.41     |
|    Linux    | 0.476099   | 0.3635   |
|   Android   | 0.971417   | 0.838    |
|  HealthApp  | 0.993431   | 0.9015   |
|    Apache   | 1          | 1        |
|  Proxifier  | 0.739766   | 0.024    |
|   OpenSSH   | 0.939796   | 0.434    |
|  OpenStack  | 0.834337   | 0.4915   |
|     Mac     | 0.981294   | 0.814    |


### 🔥 Citation

If you use the code or benchmarking results in your publication, please kindly cite the following papers.

+ [**ICSME'22**] Issam Sedki, Abdelwahab Hamou-Lhadj, Otmane Ait-Mohamed, Mohammed A. Shehab. [An Effective Approach for Parsing Large Log Files](https://users.encs.concordia.ca/~abdelw/papers/ICSME2022_ULP.pdf), *Proceedings of the IEEE International Conference on Software Maintenance and Evolution (ICSME)*, 2022.
+ [**ICSE'19**] Jieming Zhu, Shilin He, Jinyang Liu, Pinjia He, Qi Xie, Zibin Zheng, Michael R. Lyu. [Tools and Benchmarks for Automated Log Parsing](https://arxiv.org/pdf/1811.03509.pdf). *International Conference on Software Engineering (ICSE)*, 2019.
