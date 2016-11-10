# Logparser
A python package of log parsers with benchmarks for log template/event extraction

Paper
------
If you use these parsers, please cite our paper using the following reference:<br /><br />
@Conference{He16DSN,<br />
  Title                    = {An Evaluation Study on Log Parsing and Its Use in Log Mining},<br />
  Author                   = {He, P. and Zhu, J. and He, S. and Li, J. and Lyu, R.},<br />
  Booktitle                = {DSN'16: Proc. of the 46th Annual IEEE/IFIP International Conference on Dependable Systems and Networks},<br />
  Year                     = {2016}<br />
}


Parsers
--------
If you are not familiar with log parser, please check the [Principles of Parsers](https://github.com/cuhk-cse/logparser/blob/master/tutorials/PARSERS.md) <br />
The codes are [here](https://github.com/cuhk-cse/logparser/tree/master/logparser).

* SLCT (Simple Logfile Clustering Tool): [A Data Clustering Algorithm for Mining Patterns from Event Logs](http://ristov.github.io/publications/slct-ipom03-web.pdf) (SLCT is wrapped around on the [C source code](http://ristov.github.io/slct/) provided by the author.)
* IPLoM (Iterative Partitioning Log Mining): [A Lightweight Algorithm for Message Type Extraction in System Application Logs](http://ieeexplore.ieee.org/xpls/abs_all.jsp?arnumber=5936060)
* LKE (Log Key Extraction): [Execution Anomaly Detection in Distributed Systems through Unstructured Log Analysis](http://research.microsoft.com/pubs/102365/DM790-CR.pdf)
* LogSig: [LogSig: Gnerating Ssystem Events from Raw Textual Logs](http://users.cis.fiu.edu/~taoli/pub/liang-cikm2011.pdf)
* POP: a parallel log parsing method optimized on top of Spark.


Data
--------------
In [data](https://github.com/cuhk-cse/logparser/tree/master/data), there are 5 datasets for you to play with. Each dataset contains several text files.
* rawlog.log: The raw log messages with ID. "ID\tword1 word2 word3"
* template[0-9]+: The log messages belong to a certain template.
* templates: The text of templates.

Quick Start
--------------
***Input***: A raw log file. Each line of the file follows "ID\tword1 word2 word3" <br />
***Output***: Two parts. One is splitted log messages (only contains log ID) in different text files. The other is the ***templates*** file which contains all templates. <br />

***Examples***: Before running the examples, please copy the parser source file to the same directory.
* [Example1](https://github.com/cuhk-cse/logparser/blob/master/demo/example1.py): This file is used to evaluate the performance of LogSig. It iterates 10 times and record several important information (e.g., TP, FP, time). To play with your own dataset, you could modify the path and files name in the code. You should also modify the path for ground truth data in [RI_precision](https://github.com/cuhk-cse/logparser/blob/master/demo/RI_precision.py)
* [Example2](https://github.com/cuhk-cse/logparser/blob/master/demo/example2.py): This file is a simple example to demonstrate the usage of LogSig. The usage of other log parsers is similar.
* [Example3](https://github.com/cuhk-cse/logparser/blob/master/demo/example3.py): This file is to demonstrate the usage of POP.

<br /> For SLCT, because it is based on the original C code, the running example is [here](https://github.com/cuhk-cse/logparser/blob/master/logparser/SLCT/demo/SLCT_demo_BGL/precision_10_times.py). This program is platform-dependent because the .so files are only valid in Linux.


Documentation
--------------
[To be continued]



