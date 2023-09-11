# Brain

-Abstract

Automated log analysis can facilitate failure diagnosis for developers and operators using a large volume of logs. Log parsing is a prerequisite step for automated log analysis, which parses semi-structured logs into structured logs. However, existing parsers are difficult to apply to software-intensive systems, due to their unstable parsing accuracy on various software. Although neural network-based approaches are stable, their inefficiency makes it challenging to keep up with the speed of log production.We found that a logging statement always generate the same template words, thus, the word with the most frequency in each log is more likely to be constant. However, the identical constant and variable generated from different logging statements may break this rule Inspired by this key insight, we propose a new stable log parsing approach, called Brain, which creates initial groups according to the longest common pattern. Then a bidirectional tree is used to hierarchically complement the constant words to the longest common pattern to form the complete log template efficiently. Experimental results on 16 benchmark datasets show that our approach outperforms the state-of-the-art parsers on two widely-used parsing accuracy metrics, and it only takes around 46 seconds to process one million lines of logs.

Read more information about Brain from the following papers:

+ Siyu Yu, Pinjia He, Ningjiang Chen, and Yifan Wu. [Brain: Log Parsing with Bidirectional Parallel Tree](https://ieeexplore.ieee.org/abstract/document/10109145), *IEEE Transactions on Service Computing*, 2023.

