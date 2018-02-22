# Datasets
This page lists the 11 datasets used in our submission to TPDS, which are freely accessible for research purposes. Some of the logs are production data released from previous studies, while some others are collected from real systems in our lab environment.

Among these datasets, 6 of them (Hadoop, Spark, Windows, Linux, Apache, Thunderbird) are collected for the extended experiments in our journal submission. For datasets (BGL, HPC, HDFS, Zookeeper, Proxifier) used in the previous [conference paper](http://ieeexplore.ieee.org/document/8029742/), we host only sample datasets (2k lines) here due to their large size. If you are interested in the full datasets, please request the [raw logs at Zenodo](https://doi.org/10.5281/zenodo.1144100) or visit the source links wherever applicable. We will send you the full datasets upon requests.

Details
--------
| Software System          |         Dataset Name         |  #Messages  |   Message Length   | #Events | Source Link | 
| :----------------------- | :--------------------------: | :--------: | :---------: | :------------------: | :------------------: |
| **Distributed systems**     |                              |            |             |          |                      |
| HDFS                     |   [HDFS](./2kHDFS)    | 4,747,963 | 10-102  |  376  |     [Link](http://iiis.tsinghua.edu.cn/~weixu/sospdata.html) |
| Hadoop                   |      [Hadoop](./Hadoop)      |    2,000    |   6-48    |        116        | |
| Spark                    |       [Spark](./Spark)       |    2,000    | 6-22    |     36   | |
| Zookeeper                |   [Zookeeper](./2kZookeeper)   | 74,380  |   8-27    | 80  |
| **Operating systems**    |                              |            |             |          |                      |
| Windows                  |     [Windows](./Windows)     | 2,000 | 6-22 | 50  |                |
| Linux                    |       [Linux](./Linux)       | 2,000 |   7-25    |  123  |              |
| **Server applications**     |                              |            |             |          |                      |
| Apache Web server        |      [Apache](./Apache)      | 2,000 |   5-10    |  6  |               |
| **Supercomputers**       |                              |            |             |          |                      |
| Blue Gene/L              |         [BGL](./2kBGL)        | 4,747,963 |  10-102  | 376 |  [Link](https://www.usenix.org/cfdr-data) |
| HPC                      |         [HPC](./2kHPC)         |    433,489    |   6-104   | 105  |            |
| Thunderbird              | [Thunderbird](./Thunderbird) |  2,000  | 11-133 | 154  |                |
| **On-premises software** |                              |            |             |          |                      |
| Proxifier                |   [Proxifier](./2kProxifier)   |    10,108    |   10-27    |  8  |               |



### License
The log datasets are freely available ONLY for research purposes. 

[LogPAI Team](https://github.com/orgs/logpai/people), 2018
