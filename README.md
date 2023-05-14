<p align="center"> <a href="https://github.com/logpai"> <img src="https://github.com/logpai/logpai.github.io/blob/master/img/logpai_logo.jpg" width="425"></a></p>


# Logparser  
[![Documentation Status](https://readthedocs.org/projects/logparser/badge/?version=latest)](https://logparser.readthedocs.io/en/latest/?badge=latest)
[![license](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE.md)

Logparser provides a toolkit and benchmarks for automated log parsing, which is a crucial step towards structured log analytics. By applying logparser, users can automatically learn event templates from unstructured logs and convert raw log messages into a sequence of structured events. In the literature, the process of log parsing is sometimes refered to as message template extraction, log key extraction, or log message clustering. 

<p align="center"><img src="./docs/img/example.png" width="502"><br>An illustrative example of log parsing</p>

:point_right: Read the docs: https://logparser.readthedocs.io

:telescope: If you use any of our tools or benchmarks in your research for publication, please kindly cite the following papers.
+ [**ICSE'19**] Jieming Zhu, Shilin He, Jinyang Liu, Pinjia He, Qi Xie, Zibin Zheng, Michael R. Lyu. [Tools and Benchmarks for Automated Log Parsing](https://arxiv.org/pdf/1811.03509.pdf). *International Conference on Software Engineering (ICSE)*, 2019.
+ [**DSN'16**] Pinjia He, Jieming Zhu, Shilin He, Jian Li, Michael R. Lyu. [An Evaluation Study on Log Parsing and Its Use in Log Mining](https://jiemingzhu.github.io/pub/pjhe_dsn2016.pdf). *IEEE/IFIP International Conference on Dependable Systems and Networks (DSN)*, 2016.

### Log parsers currently available:

| Tools | References |
| :--- | :--- |
| SLCT | [**IPOM'03**] [A Data Clustering Algorithm for Mining Patterns from Event Logs](http://www.quretec.com/u/vilo/edu/2003-04/DM_seminar_2003_II/ver1/P12/slct-ipom03-web.pdf), by Risto Vaarandi. |
| AEL | [**QSIC'08**] [Abstracting Execution Logs to Execution Events for Enterprise Applications](https://www.researchgate.net/publication/4366728_Abstracting_Execution_Logs_to_Execution_Events_for_Enterprise_Applications_Short_Paper), by Zhen Ming Jiang, Ahmed E. Hassan, Parminder Flora, Gilbert Hamann. <br> [**JSME'08**] [An Automated Approach for Abstracting Execution Logs to Execution Events](http://www.cse.yorku.ca/~zmjiang/publications/jsme2008.pdf), by Zhen Ming Jiang, Ahmed E. Hassan, Gilbert Hamann, Parminder Flora.  |
| IPLoM | [**KDD'09**] [Clustering Event Logs Using Iterative Partitioning](https://web.cs.dal.ca/~makanju/publications/paper/kdd09.pdf), by Adetokunbo Makanju, A. Nur Zincir-Heywood, Evangelos E. Milios. <br> [**TKDE'12**] [A Lightweight Algorithm for Message Type Extraction in System Application Logs](http://ieeexplore.ieee.org/abstract/document/5936060/), by Adetokunbo Makanju, A. Nur Zincir-Heywood, Evangelos E. Milios.  |
| LKE | [**ICDM'09**] [Execution Anomaly Detection in Distributed Systems through Unstructured Log Analysis](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/DM790-CR.pdf), by Qiang Fu, Jian-Guang Lou, Yi Wang, Jiang Li. [**Microsoft**]  |
| LFA | [**MSR'10**] [Abstracting Log Lines to Log Event Types for Mining Software System Logs](http://www.se.rit.edu/~mei/publications/pdfs/Abstracting-Log-Lines-to-Log-Event-Types-for-Mining-Software-System-Logs.pdf), by Meiyappan Nagappan, Mladen A. Vouk. |
| LogSig | [**CIKM'11**] [LogSig: Generating System Events from Raw Textual Logs](https://users.cs.fiu.edu/~taoli/pub/liang-cikm2011.pdf), by Liang Tang, Tao Li, Chang-Shing Perng.  |
| SHISO | [**SCC'13**] [Incremental Mining of System Log Format](http://ieeexplore.ieee.org/document/6649746/), by Masayoshi Mizutani. |
| LogCluster | [**CNSM'15**] [LogCluster - A Data Clustering and Pattern Mining Algorithm for Event Logs](http://dl.ifip.org/db/conf/cnsm/cnsm2015/1570161213.pdf), by Risto Vaarandi, Mauno Pihelgas.  |
| LenMa | [**CNSM'15**] [Length Matters: Clustering System Log Messages using Length of Words](https://arxiv.org/pdf/1611.03213.pdf), by Keiichi Shima. |
| LogMine | [**CIKM'16**] [LogMine: Fast Pattern Recognition for Log Analytics](http://www.cs.unm.edu/~mueen/Papers/LogMine.pdf), by Hossein Hamooni, Biplob Debnath, Jianwu Xu, Hui Zhang, Geoff Jiang, Adbullah Mueen. [**NEC**] |
| Spell | [**ICDM'16**] [Spell: Streaming Parsing of System Event Logs](https://www.cs.utah.edu/~lifeifei/papers/spell.pdf), by Min Du, Feifei Li.  |
| Drain | [**ICWS'17**] [Drain: An Online Log Parsing Approach with Fixed Depth Tree](https://jiemingzhu.github.io/pub/pjhe_icws2017.pdf), by Pinjia He, Jieming Zhu, Zibin Zheng, and Michael R. Lyu. <br> [IBM-Drain3](https://github.com/IBM/Drain3): IBM's upgrade version of Drain in Python 3.6 with additional features. |
| MoLFI | [**ICPC'18**] [A Search-based Approach for Accurate Identification of Log Message Formats](http://publications.uni.lu/bitstream/10993/35286/1/ICPC-2018.pdf), by Salma Messaoudi, Annibale Panichella, Domenico Bianculli, Lionel Briand, Raimondas Sasnauskas.  |

### Get started

Code organization:

+ [benchmark](./benchmark): the benchmark scripts to reproduce the evaluation results of log parsing 
+ [demo](./demo): the demo files to show how to run logparser on HDFS logs.
+ [logparser](./logparser): the logparser package
+ [logs](./logs): Some log samples and manually parsed structured logs with their templates (ground truth).

Please follow the [installation steps](https://logparser.readthedocs.io/en/latest/installation/dependency.html) and [demo](https://logparser.readthedocs.io/en/latest/demo.html) in the docs to get started. 

### Benchmarking results
All the log parsers have been evaluated across 16 different logs available in [loghub](https://github.com/logpai/loghub). We report parsing accuracy as the percentage of accurately parsed log messages. To reproduce the experimental results, please run the [benchmark](./benchmark) scripts.

<p align="center"><a href="https://arxiv.org/abs/1811.03509"><img src="./docs/img/parsers.png" width="768"></a></p>

<details>
 <summary>:point_down: Check the detailed bechmarking result table (click to expand)</summary>

 <p align="center"><a href="https://arxiv.org/abs/1811.03509"><img src="./docs/img/accuracy.png" width="908"></a></p>

 In the table, accuracy values above 0.9 are marked in bold, and the best accuracy results achieved are marked with \*. Some of the accuracy values may be lower than what have been reported by previous studies (e.g., Drain, LogMine). The reasons are two-fold: 1) We use a more rigorous accuracy metric which rejects events that are only partially matched. 2)  For fairness of comparison, we apply only a few preprocessing regular expressions (e.g., IP or number replacement) to each log parser. Adding more preprocessing rules can boost parsing accuracy, but requires more manual efforts as well.

</details>


### Publications about logparser
+ [**ICSE'19**] Jieming Zhu, Shilin He, Jinyang Liu, Pinjia He, Qi Xie, Zibin Zheng, Michael R. Lyu. [Tools and Benchmarks for Automated Log Parsing](https://arxiv.org/pdf/1811.03509.pdf). International Conference on Software Engineering (ICSE), 2019.
+ [**TDSC'18**] Pinjia He, Jieming Zhu, Shilin He, Jian Li, Michael R. Lyu. [Towards Automated Log Parsing for Large-Scale Log Data Analysis](https://jiemingzhu.github.io/pub/pjhe_tdsc2017.pdf). IEEE Transactions on Dependable and Secure Computing (TDSC), 2018.
+ [**ICWS'17**] Pinjia He, Jieming Zhu, Zibin Zheng, Michael R. Lyu. [Drain: An Online Log Parsing Approach with Fixed Depth Tree](https://jiemingzhu.github.io/pub/pjhe_icws2017.pdf). IEEE International Conference on Web Services (ICWS), 2017.
+ [**DSN'16**] Pinjia He, Jieming Zhu, Shilin He, Jian Li, Michael R. Lyu. [An Evaluation Study on Log Parsing and Its Use in Log Mining](https://jiemingzhu.github.io/pub/pjhe_dsn2016.pdf). IEEE/IFIP International Conference on Dependable Systems and Networks (DSN), 2016.

### Publications using logparser

| Year | Conference                                          | Paper Title                                                  | Code                                              |
| ---- | --------------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------- |
| 2023 | ICSE                                                | Van-Hoang Le, Hongyu Zhang. [Log Parsing with Prompt-based Few-shot Learning](https://arxiv.org/abs/2302.07435) | [Link](https://github.com/LogIntelligence/LogPPT) |
| 2023 | ICSE                                                | Zhenhao Li, Chuan Luo, Tse-Hsun Chen, Weiyi Shang, Shilin He, Qingwei Lin, Dongmei Zhang. [Did We Miss Something Important? Studying and Exploring Variable-Aware Log Abstraction](https://arxiv.org/abs/2304.11391) |                                                   |
| 2023 | ICSE                                                | Yintong Huo, Yuxin Su, Cheryl Lee, Michael R. Lyu. [SemParser: A Semantic Parser for Log Analysis](https://arxiv.org/abs/2112.12636) | [Link](https://github.com/YintongHuo/SemParser.)  |
| 2023 | IEEE Transaction on Severice Computing              | Siyu Yu, Pinjia He, Ningjiang Chen, Yifan Wu. [Brain: Log Parsing with Bidirectional Parallel Tree](https://ieeexplore.ieee.org/document/10109145) | [Link](https://github.com/gaiusyu/Brain)          |
| 2023 | IEEE Transactions on Network and Service Management | Xiao T, Quan Z, Wang Z J, et al. [LPV: A Log Parsing Framework Based on Vectorization](https://ieeexplore.ieee.org/iel7/4275028/5699970/10050551.pdf?casa_token=-AJXiduy4wwAAAAA:_m2W_1uCYaqgW8UQ-l_F_paLRo8axYTvw5O0w1YsCNoGTbcf1nxVEi5g8izd0eoX6NdxTw-CdOk) |                                                   |
| 2023 | WWW                                                 | Liming Wang, Hong Xie, Ye Li, Jian Tan, John C.S. Lui. [Interactive Log Parsing via Light-weight User Feedback](https://arxiv.org/abs/2301.12225) |                                                   |
| 2023 | TKDE                                                | [Zhang T, Qiu H, Castellano G, et al. System Log Parsing: A Survey](https://ieeexplore.ieee.org/iel7/69/4358933/10025560.pdf?casa_token=-f9GU67NplgAAAAA:pjc2PafAjd-wqkHZfXvcOlLaEp8DlF6_tVHCLFSG1d6Xakv83sLHfOFGrk-v1IKNmyMC3Fyx). IEEE Transactions on Knowledge and Data Engineering, 2023. |                                                   |
| 2022 | ICSME                                               | I. Sedki, A. Hamou-Lhadj, O. Ait-Mohamed, M. Shehab. [An Effective Approach for Parsing Large Log Files](https://ieeexplore.ieee.org/iel7/9977440/9977441/09978179.pdf?casa_token=_OS4R1AgdhQAAAAA:t-lzlYfc8kPrspY2btSU6mGTVTC-KLY2Uk4QK1iMcuuOFzHi-xQ-ffm0Ba3Y-EgMlh1jxMyE) | [Link](https://github.com/SRT-Lab/ULP)            |
| 2022 | FSE (**best paper**)                                | Xuheng Wang, Xu Zhang, Liqun Li, Shilin He, et al. [SPINE: a scalable log parser with feedback guidance](https://dl.acm.org/doi/abs/10.1145/3540250.3549176?casa_token=cKh8puONUA8AAAAA:iFgQWoWJbwdJFVf23aMiPpLAETPV_CpGdWiSyZjaCFaNXSEK2ErqKxQeQ9a9YmnVKiRWwNy-2kce) |                                                   |
| 2022 | WWW                                                 | Liu Y, Zhang X, He S, et al. [Uniparser: A unified log parser for heterogeneous log data](https://dl.acm.org/doi/pdf/10.1145/3485447.3511993?casa_token=_ThuiSd7bO4AAAAA:Cr-8Yo1O2Z8S_YdNmiuj7m80RPZLoJhI_Gzidn1fntdcZh-chcnEr3Mvi2urjdiVtaxocxVndSSf) |                                                   |
| 2021 | ICDE                                                | Chu G, Wang J, Qi Q, et al. [Prefix-Graph: A Versatile Log Parsing Approach Merging Prefix Tree with Probabilistic Graph](https://ieeexplore.ieee.org/iel7/9458599/9458600/09458609.pdf?casa_token=-JCm_FmC0gMAAAAA:-_A_ZmFmSIsPJcwFFuJmCgueEf8rRRi59800lIHRCclm_l0kbYVMnOZ-STK7uC9nd7qZ50Hq) |                                                   |
| 2020 | TSE                                                 | Dai H, Li H, Chen C S, et al. [Logram: Efficient Log Parsing Using n-Gram Dictionaries](https://ieeexplore.ieee.org/iel7/32/4359463/09134790.pdf?casa_token=TfhNtJnLWrUAAAAA:q1Gc9DVCaGgfZGu_9JB5RS7kxOtfAnHUUZGupZpOcKBMsTSN2g6YLMzWL1yVBvh4MwfYm3xP) | [Link](https://github.com/BlueLionLogram/Logram)  |
| 2020 | PKDD                                                | Nedelkoski S, Bogatinovski J, Acker A, et al. [https://arxiv.org/pdf/2003.07905](https://arxiv.org/pdf/2003.07905) |                                                   |
|      |                                                     |                                                              |                                                   |
|      |                                                     |                                                              |                                                   |
|      |                                                     |                                                              |                                                   |
|      |                                                     |                                                              |                                                   |
|      |                                                     |                                                              |                                                   |





### Acknowledgement

Logparser is implemented based on a number of existing open-source projects:
+ [SLCT](http://ristov.github.io/slct/) (C++)
+ [LogCluster](https://github.com/ristov/logcluster) (perl)
+ [LenMa](https://github.com/keiichishima/templateminer) (python 2.7)
+ [MoLFI](https://github.com/SalmaMessaoudi/MoLFI) (python 3.6)

### Feedback
For any questions or feedback, please post to [the issue page](https://github.com/logpai/logparser/issues). 



