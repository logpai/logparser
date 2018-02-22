# Datasets
Log datasets for log parsing task.

Details
--------
| Software System          |         Dataset Name         | Time Span  |  #Messages  |   Size   | Compressed (.tar.gz) | Source Link | 
| :----------------------- | :--------------------------: | :--------: | :---------: | :------: | :------------------: | :------------------: |
| **Distributed systems**     |                              |            |             |          |                      |
| HDFS                     |   [HDFS-1](./HDFS/HDFS-1)    | 38.7 hours | 11,175,629  |  1.54GB  |       152.01MB       | [Link](http://iiis.tsinghua.edu.cn/~weixu/sospdata.html) |
|                          |   [HDFS-2](./HDFS/HDFS-2)    |    N.A.    | 71,118,073  | 16.84GB  |       877.38MB       |
| Hadoop                   |      [Hadoop](./Hadoop)      |    N.A.    |   394,308   | 49.78MB  |        2.50MB        |
| Spark                    |       [Spark](./Spark)       |    N.A.    | 33,236,604  |  2.88GB  |       179.18MB       |
| Zookeeper                |   [Zookeeper](./Zookeeper)   | 26.7 days  |   74,380    | 10.18MB  |        452KB         |
| **Operating systems**    |                              |            |             |          |                      |
| Windows                  |     [Windows](./Windows)     | 226.7 days | 114,608,388 | 27.36GB  |        1.63GB        |
| Linux                    |       [Linux](./Linux)       | 263.9 days |   25,567    |  2.30MB  |        228KB         |
| **Server applications**     |                              |            |             |          |                      |
| Apache Web server        |      [Apache](./Apache)      | 263.9 days |   56,481    |  5.02MB  |        260KB         |
| **Supercomputers**       |                              |            |             |          |                      |
| Blue Gene/L              |         [BGL](./BGL)         | 214.7 days |  4,747,963  | 725.77MB |       61.46MB        | [Link](https://www.usenix.org/cfdr-data)
| HPC                      |         [HPC](./HPC)         |    N.A.    |   433,489   | 32.77MB  |        3.21MB        |
| Thunderbird              | [Thunderbird](./Thunderbird) |  244 days  | 211,212,192 | 31.04GB  |        1.97GB        |
| **On-premises software** |                              |            |             |          |                      |
| Proxifier                |   [Proxifier](./Proxifier)   |    N.A.    |   10,108    |  1.19MB  |        172KB         |


Data
--------------
In [data](https://github.com/logpai/logparser/tree/master/data), there are 5 datasets for you to play with. Each dataset contains several text files.
* rawlog.log: The raw log messages with ID. "ID\tword1 word2 word3"
* template[0-9]+: The log messages belong to a certain template.
* templates: The text of templates.


### License
The log datasets are freely available ONLY for research purposes. 

[LogPAI Team](https://github.com/orgs/logpai/people), 2018
