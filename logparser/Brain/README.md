# Brain


Automated log analysis can facilitate failure diagnosis for developers and operators using a large volume of logs. Log parsing is a prerequisite step for automated log analysis, which parses semi-structured logs into structured logs. However, existing parsers are difficult to apply to software-intensive systems, due to their unstable parsing accuracy on various software. Although neural network-based approaches are stable, their inefficiency makes it challenging to keep up with the speed of log production.We found that a logging statement always generate the same template words, thus, the word with the most frequency in each log is more likely to be constant. However, the identical constant and variable generated from different logging statements may break this rule Inspired by this key insight, we propose a new stable log parsing approach, called Brain, which creates initial groups according to the longest common pattern. Then a bidirectional tree is used to hierarchically complement the constant words to the longest common pattern to form the complete log template efficiently. Experimental results on 16 benchmark datasets show that our approach outperforms the state-of-the-art parsers on two widely-used parsing accuracy metrics, and it only takes around 46 seconds to process one million lines of logs.


### Running

Install the required enviornment:
```
pip install -r requirements.txt
```

Run the following scripts to start the demo:

```
python demo.py
```

Run the following scripts to execute the benchmark:

```
python benchmark.py
```

### Docker images

```
1. docker pull docker.io/gaiusyu/brain:v2
2. docker run -it --name brain gaiusyu/brain:v2
```

### Benchmark

Running the benchmark script on Loghub_2k datasets, you could obtain the following results.

|   Dataset   | F1_measure | Accuracy |
|:-----------:|:----------|:---------|
|  Proxifier  | 1          | 1        |
|     HDFS    | 0.999984   | 0.9975   |
|    Hadoop   | 0.998749   | 0.949    |
|    Spark    | 0.99998    | 0.9975   |
|  Zookeeper  | 0.9998     | 0.9875   |
|     BGL     | 0.999932   | 0.986    |
|     HPC     | 0.997707   | 0.945    |
| Thunderbird | 0.999933   | 0.971    |
|   Windows   | 0.999995   | 0.997    |
|    Linux    | 0.999992   | 0.996    |
|   Android   | 0.996837   | 0.9605   |
|  HealthApp  | 1          | 1        |
|    Apache   | 1          | 1        |
|   OpenSSH   | 1          | 1        |
|  OpenStack  | 1          | 1        |
|     Mac     | 0.995821   | 0.942    |


### 🔥 Citation

If you use the code or benchmarking results in your publication, please kindly cite the following papers.

+ [**TSC'23**] Siyu Yu, Pinjia He, Ningjiang Chen, and Yifan Wu. [Brain: Log Parsing with Bidirectional Parallel Tree](https://ieeexplore.ieee.org/abstract/document/10109145), *IEEE Transactions on Service Computing*, 2023.
+ [**ICSE'19**] Jieming Zhu, Shilin He, Jinyang Liu, Pinjia He, Qi Xie, Zibin Zheng, Michael R. Lyu. [Tools and Benchmarks for Automated Log Parsing](https://arxiv.org/pdf/1811.03509.pdf). *International Conference on Software Engineering (ICSE)*, 2019.
