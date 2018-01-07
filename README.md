# Logparser
This repository provides a toolkit and benchmarks for automated log parsing, which is a crucial step in structured log analysis. Logparser implements data-driven approaches that automatically learn event templates from unstructured logs and convert raw log messages into a sequence of structured events. In the literature, the process of log parsing is also sometimes refered to as message template extraction, log key extraction, or log message clustering.

Log parsers currently made available:

| Tool | Reference |
| :---: | :--- |
| SLCT | [**IPOM'03**] Risto Vaarandi. [A Data Clustering Algorithm for Mining Patterns from Event Logs](http://www.quretec.com/u/vilo/edu/2003-04/DM_seminar_2003_II/ver1/P12/slct-ipom03-web.pdf), 2003 |
| IPLoM | [**KDD'09**] Adetokunbo Makanju, A. Nur Zincir-Heywood, Evangelos E. Milios. [Clustering Event Logs Using Iterative Partitioning](https://web.cs.dal.ca/~makanju/publications/paper/kdd09.pdf), 2009.<br> [**TKDE'12**] Adetokunbo Makanju, A. Nur Zincir-Heywood, Evangelos E. Milios. [A Lightweight Algorithm for Message Type Extraction in System Application Logs](http://ieeexplore.ieee.org/abstract/document/5936060/), 2012 |
| LKE | [**ICDM'09**] Qiang Fu, Jian-Guang Lou, Yi Wang, Jiang Li. [Execution Anomaly Detection in Distributed Systems through Unstructured Log Analysis](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/DM790-CR.pdf), 2009. |
| LogSig | [**CIKM'11**] Liang Tang, Tao Li, Chang-Shing Perng. [LogSig: Generating System Events from Raw Textual Logs](https://users.cs.fiu.edu/~taoli/pub/liang-cikm2011.pdf), 2011. |
| LogCluster | [**CNSM'15**] Risto Vaarandi, Mauno Pihelgas. [LogCluster - A Data Clustering and Pattern Mining Algorithm for Event Logs](http://dl.ifip.org/db/conf/cnsm/cnsm2015/1570161213.pdf), 2015 | 
| POP | [**TSDC'17**] Pinjia He, Jieming Zhu, Shilin He, Jian Li, Michael R. Lyu. [Towards Automated Log Parsing for Large-Scale Log Data Analysis](http://jiemingzhu.github.io/pub/pjhe_tdsc2017.pdf), 2017. |

Benchmarking results on logs in our [loghub](https://github.com/logpai/loghub):

| Tool | HDFS | Hadoop | Spark | Zookeeper | BGL | HPC | Thunderbird | 
| :--- | :---: | :---: | :---: | :---: | :---: |  :---: | :---: | 
| SLCT |  |  | |  |  |   |  | 
| IPLoM | |  | |  |  |   |  | 
| LKE |  |  | |  |  |   |  | 
| LogSig |  |  | |  |  |   |  | 
|  |  |  | |  |  |   |  | 
| Tool | Windows | Linux | Android | HealthApp | Apache | Proxifier | OpenSSH | 
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

