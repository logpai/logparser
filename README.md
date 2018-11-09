[![Documentation Status](https://readthedocs.org/projects/logparser/badge/?version=latest)](https://logparser.readthedocs.io/en/latest/?badge=latest)
[![license](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE.md)

# Logparser
Logparser provides a toolkit and benchmarks for automated log parsing, which is a crucial step towards structured log analytics. Logparser implements a number of state-of-the-art data-driven approaches for this goal. By applying logparser, users can automatically learn event templates from unstructured logs and convert raw log messages into a sequence of structured events. In the literature, the process of log parsing is sometimes refered to as message template extraction, log key extraction, or log message clustering. 

Read the docs: https://logparser.readthedocs.io

**Note**: If you use any of our tools or benchmarks in your research for publication, please kindly cite the following papers.
+ [**Arxiv'18**] Jieming Zhu, Shilin He, Jinyang Liu, Pinjia He, Qi Xie, Zibin Zheng, Michael R. Lyu. [Tools and Benchmarks for Automated Log Parsing](https://arxiv.org/pdf/1811.03509.pdf). arXiv:1811.03509, 2018.
+ [**DSN'16**] Pinjia He, Jieming Zhu, Shilin He, Jian Li, Michael R. Lyu. [An Evaluation Study on Log Parsing and Its Use in Log Mining](http://jiemingzhu.github.io/pub/pjhe_dsn2016.pdf). IEEE/IFIP International Conference on Dependable Systems and Networks (DSN), 2016.

### Log parsers currently available: (still in beta release!)

| Tools | References |
| :--- | :--- |
| SLCT | [**IPOM'03**] Risto Vaarandi. [A Data Clustering Algorithm for Mining Patterns from Event Logs](http://www.quretec.com/u/vilo/edu/2003-04/DM_seminar_2003_II/ver1/P12/slct-ipom03-web.pdf), 2003 |
| AEL | [**QSIC'08**] Zhen Ming Jiang, Ahmed E. Hassan, Parminder Flora, Gilbert Hamann. [Abstracting Execution Logs to Execution Events for Enterprise Applications](https://www.researchgate.net/publication/4366728_Abstracting_Execution_Logs_to_Execution_Events_for_Enterprise_Applications_Short_Paper), 2008<br> [**JSME'08**] Zhen Ming Jiang, Ahmed E. Hassan, Gilbert Hamann, Parminder Flora. [An Automated Approach for Abstracting Execution Logs to Execution Events](http://www.cse.yorku.ca/~zmjiang/publications/jsme2008.pdf), 2008 |
| IPLoM | [**KDD'09**] Adetokunbo Makanju, A. Nur Zincir-Heywood, Evangelos E. Milios. [Clustering Event Logs Using Iterative Partitioning](https://web.cs.dal.ca/~makanju/publications/paper/kdd09.pdf), 2009<br> [**TKDE'12**] Adetokunbo Makanju, A. Nur Zincir-Heywood, Evangelos E. Milios. [A Lightweight Algorithm for Message Type Extraction in System Application Logs](http://ieeexplore.ieee.org/abstract/document/5936060/), 2012 |
| LKE | [**ICDM'09**] Qiang Fu, Jian-Guang Lou, Yi Wang, Jiang Li. [Execution Anomaly Detection in Distributed Systems through Unstructured Log Analysis](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/DM790-CR.pdf), 2009 |
| LFA | [**MSR'10**] Meiyappan Nagappan, Mladen A. Vouk. [Abstracting Log Lines to Log Event Types for Mining Software System Logs](http://www.se.rit.edu/~mei/publications/pdfs/Abstracting-Log-Lines-to-Log-Event-Types-for-Mining-Software-System-Logs.pdf), 2010|
| LogSig | [**CIKM'11**] Liang Tang, Tao Li, Chang-Shing Perng. [LogSig: Generating System Events from Raw Textual Logs](https://users.cs.fiu.edu/~taoli/pub/liang-cikm2011.pdf), 2011 |
| SHISO | [**SCC'13**] Masayoshi Mizutani. [Incremental Mining of System Log Format](http://ieeexplore.ieee.org/document/6649746/), 2013|
| LogCluster | [**CNSM'15**] Risto Vaarandi, Mauno Pihelgas. [LogCluster - A Data Clustering and Pattern Mining Algorithm for Event Logs](http://dl.ifip.org/db/conf/cnsm/cnsm2015/1570161213.pdf), 2015 |
| LenMa | [**CNSM'15**] Keiichi Shima. [Length Matters: Clustering System Log Messages using Length of Words](https://arxiv.org/pdf/1611.03213.pdf), 2015. |
| LogMine | [**CIKM'16**] Hossein Hamooni, Biplob Debnath, Jianwu Xu, Hui Zhang, Geoff Jiang, Adbullah Mueen. [LogMine: Fast Pattern Recognition for Log Analytics](http://www.cs.unm.edu/~mueen/Papers/LogMine.pdf), 2016 |
| Spell | [**ICDM'16**] Min Du, Feifei Li. [Spell: Streaming Parsing of System Event Logs](https://www.cs.utah.edu/~lifeifei/papers/spell.pdf), 2016 |
| Drain | [**ICWS'17**] Pinjia He, Jieming Zhu, Zibin Zheng, and Michael R. Lyu. [Drain: An Online Log Parsing Approach with Fixed Depth Tree](http://jiemingzhu.github.io/pub/pjhe_icws2017.pdf), 2017 |
| POP | [**TDSC'17**] Pinjia He, Jieming Zhu, Shilin He, Jian Li, Michael R. Lyu. [Towards Automated Log Parsing for Large-Scale Log Data Analysis](http://jiemingzhu.github.io/pub/pjhe_tdsc2017.pdf), 2017 |
| MoLFI | [**ICPC'18**] Salma Messaoudi, Annibale Panichella, Domenico Bianculli, Lionel Briand, Raimondas Sasnauskas. [A Search-based Approach for Accurate Identification of Log Message Formats](http://publications.uni.lu/bitstream/10993/35286/1/ICPC-2018.pdf), 2018 |


### Benchmarking results
All the log parsers have been evaluated on [loghub](https://github.com/logpai/loghub) log samples. We report parsing accuracy as the percentage of accurately parsed log messages. Note that accuracy values above 0.9 are marked in bold, and the best accuracy results achieved are marked with \*. 

| **Tools**   |  **HDFS**   | **Hadoop** | **Spark**  | **Zookeeper** | **OpenStack** |  **BGL**   |   **HPC**   | **Thunderbird** |
| :---------- | :---------: | :--------: | :--------: | :-----------: | :-----------: | :--------: | :---------: | :-------------: |
| SLCT        |    0.545    |   0.423    |   0.685    |     0.726     |     0.867     |   0.573    |    0.839    |      0.882      |
| AEL         |  **0.998**  |   0.538    | **0.905**  |   **0.921**   |     0.758     | **0.957**  |  **0.903**  |    **0.941**    |
| IPLoM       |   **1***    | **0.954**  | **0.920**  |   **0.962**   |     0.871     | **0.939**  |    0.824    |      0.663      |
| LKE         |   **1***    |   0.670    |   0.634    |     0.438     |     0.787     |   0.128    |    0.574    |      0.813      |
| LFA         |    0.885    | **0.900**  | **0.994**  |     0.839     |     0.200     |   0.854    |    0.817    |      0.649      |
| LogSig      |    0.850    |   0.633    |   0.544    |     0.738     |     0.866     |   0.227    |    0.354    |      0.694      |
| SHISO       |  **0.998**  |   0.867    | **0.906**  |     0.660     |     0.722     |   0.711    |    0.325    |      0.576      |
| LogCluster  |    0.546    |   0.563    |   0.799    |     0.732     |     0.696     |   0.835    |    0.788    |      0.599      |
| LenMa       |  **0.998**  |   0.885    |   0.884    |     0.841     |     0.743     |   0.690    |    0.830    |    **0.943**    |
| LogMine     |    0.851    |   0.870    |   0.576    |     0.688     |     0.743     |   0.723    |    0.784    |    **0.919**    |
| Spell       |   **1***    |   0.778    | **0.905**  |   **0.964**   |     0.764     |   0.787    |    0.654    |      0.844      |
| Drain       |  **0.998**  | **0.948**  | **0.920**  |   **0.967**   |     0.733     | **0.963**  |    0.887    |    **0.955**    |
| MoLFI       |  **0.998**  | **0.957**  |   0.418    |     0.839     |     0.213     | **0.960**  |    0.824    |      0.646      |
|             |             |            |            |               |               |            |             |                 |
| **Tools**   | **Windows** | **Linux**  |  **Mac**   |  **Android**  | **HealthApp** | **Apache** | **OpenSSH** |  **Proxifier**  |
| SLCT        |    0.697    |   0.297    |   0.558    |     0.882     |     0.331     |   0.731    |    0.521    |      0.518      |
| AEL         |    0.690    |   0.673    |   0.764    |     0.682     |     0.568     |   **1***   |    0.538    |    0.518    |
| IPLoM       |    0.567    |   0.672    |   0.673    |     0.712     |     0.822     |   **1***   |    0.802    |    0.515    |
| LKE         |  **0.990**  |   0.519    |   0.369    |   **0.909**   |     0.592     |   **1***   |    0.426    |      0.495      |
| LFA         |    0.588    |   0.279    |   0.599    |     0.616     |     0.549     |   **1***   |    0.501    |      0.026      |
| LogSig      |    0.689    |   0.169    |   0.478    |     0.548     |     0.235     |   0.582    |    0.373    |      **0.967**      |
| SHISO       |    0.701    |   0.672    |   0.595    |     0.585     |     0.397     |   **1***   |    0.619    |      0.517      |
| LogCluster  |    0.713    |   0.629    |   0.604    |     0.798     |     0.531     |   0.709    |    0.426    |      **0.951**      |
| LenMa       |    0.566    |   0.701    |   0.698    |     0.880     |     0.174     |   **1***   |    **0.925**    |      0.508      |
| LogMine     |  **0.993**  |   0.612    |   0.872    |     0.504     |     0.684     |   **1***   |    0.431    |      0.517      |
| Spell       |  **0.989**  |   0.605    |   0.757    |   **0.919**   |     0.639     |   **1***   |    0.554    |      0.527      |
| Drain       |  **0.997**  |   0.690    |   0.787    |   **0.911**   |     0.780     |   **1***   |    0.788    |      0.527      |
| MoLFI       |    0.406    |   0.284    |   0.636    |   **0.788**   |     0.440     |   **1***   |    0.50    |        0.013        |


### Publications about logparser
+ [**Arxiv'18**] Jieming Zhu, Shilin He, Jinyang Liu, Pinjia He, Qi Xie, Zibin Zheng, Michael R. Lyu. [Tools and Benchmarks for Automated Log Parsing](https://arxiv.org/pdf/1811.03509.pdf). arXiv:1811.03509, 2018.
+ [**TDSC'17**] Pinjia He, Jieming Zhu, Shilin He, Jian Li, Michael R. Lyu. [Towards Automated Log Parsing for Large-Scale Log Data Analysis](http://jiemingzhu.github.io/pub/pjhe_tdsc2017.pdf). IEEE Transactions on Dependable and Secure Computing (TDSC), 2017.
+ [**ICWS'17**] Pinjia He, Jieming Zhu, Zibin Zheng, Michael R. Lyu. [Drain: An Online Log Parsing Approach with Fixed Depth Tree](http://jiemingzhu.github.io/pub/pjhe_icws2017.pdf). IEEE International Conference on Web Services (ICWS), 2017.
+ [**DSN'16**] Pinjia He, Jieming Zhu, Shilin He, Jian Li, Michael R. Lyu. [An Evaluation Study on Log Parsing and Its Use in Log Mining](http://jiemingzhu.github.io/pub/pjhe_dsn2016.pdf). IEEE/IFIP International Conference on Dependable Systems and Networks (DSN), 2016.

### Acknowledgement
Logparser is implemented based on a number of existing open-source projects:
+ [SLCT](http://ristov.github.io/slct/) (C++)
+ [LogCluster](https://github.com/ristov/logcluster) (perl)
+ [LenMa](https://github.com/keiichishima/templateminer) (python 2)
+ [MoLFI](https://github.com/SalmaMessaoudi/MoLFI) (python 3)

### Contribution
Contributions and suggestions are welcome! For any bugs or enquiries, please post to [the issue page](https://github.com/logpai/logparser/issues). 


