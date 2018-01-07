# Logparser
This repository provides a toolkit and benchmarks for automated log parsing, which is a crucial step in structured log analysis. Logparser implements data-driven approaches that automatically learn event templates from unstructured logs and convert raw log messages into a sequence of structured events. In the literature, the process of log parsing is also sometimes refered to as message template extraction, log key extraction, or log message clustering.

Log parsers currently made available:

| Tool | Reference |
| :---: | :---: |
| SLCT | [**IPOM'03**] A Data Clustering Algorithm for Mining Patterns from Event Logs |
| IPLoM | [**KDD'09**] A Lightweight Algorithm for Message Type Extraction in System Application Logs |
| LKE | [**ICDM'09**] A Data Clustering Algorithm for Mining Patterns from Event Logs |
| LogSig | [**CIKM'11**] LogSig: Generating System Events from Raw Textual Logs |
| POP | [**TSDC'17**] Pinjia He, Jieming Zhu, Shilin He, Jian Li, Michael R. Lyu. [Towards Automated Log Parsing for Large-Scale Log Data Analysis](http://jiemingzhu.github.io/pub/pjhe_tdsc2017.pdf). IEEE Transactions on Dependable and Secure Computing (TDSC), 2017. |

Benchmarking results on logs in our [loghub](https://github.com/logpai/loghub):

| Tool | HDFS | Hadoop | Spark | Zookeeper | BGL | HPC | Thunderbird | 
| :--- | :---: | :---: | :---: | :---: | :---: |  :---: | :---: | 
| SLCT |  |  | |  |  |   |  | 
| IPLoM | |  | |  |  |   |  | 
| LKE |  |  | |  |  |   |  | 
| LogSig |  |  | |  |  |   |  | 
| Tool | Windows | Linux | Android | HealthApp | Apache | Proxifier | OpenSSH | 
| :--- | :---: | :---: | :---: | :---: | :---: |  :---: | :---: |
| SLCT |  |  | |  |  |   |  | 
| IPLoM | |  | |  |  |   |  | 
| LKE |  |  | |  |  |   |  | 
| LogSig |  |  | |  |  |   |  | 


### Publications about logparser
+ [**TDSC'17**] Pinjia He, Jieming Zhu, Shilin He, Jian Li, Michael R. Lyu. [Towards Automated Log Parsing for Large-Scale Log Data Analysis](http://jiemingzhu.github.io/pub/pjhe_tdsc2017.pdf). IEEE Transactions on Dependable and Secure Computing (TDSC), 2017.
+ [**ICWS'17**] Pinjia He, Jieming Zhu, Zibin Zheng, Michael R. Lyu. [Drain: An Online Log Parsing Approach with Fixed Depth Tree](http://jiemingzhu.github.io/pub/pjhe_icws2017.pdf). IEEE International Conference on Web Services (ICWS), 2017.
+ [**DSN'16**] Pinjia He, Jieming Zhu, Shilin He, Jian Li, Michael R. Lyu. [An Evaluation Study on Log Parsing and Its Use in Log Mining](http://jiemingzhu.github.io/pub/pjhe_dsn2016.pdf). IEEE/IFIP International Conference on Dependable Systems and Networks (DSN), 2016.


### Feedback
For any bugs or feedback, please post to [our issue page](https://github.com/logpai/logparser/issues). 


### License
[The MIT License (MIT)](./LICENSE)

Copyright &copy; 2018, [LogPAI Team](https://github.com/orgs/logpai/people)

