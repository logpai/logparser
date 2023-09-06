Drain
===

Drain is one of the representative algorithms for log parsing. It can parse logs in a streaming and timely manner. To accelerate the parsing process, Drain uses a fixed depth parse tree (See the figure below), which encodes specially designed rules for parsing.

![Sturcture of parse tree in Drain](https://ws1.sinaimg.cn/large/006tKfTcgy1ftuhiqqmazj30r40k4wgw.jpg)

Drain first preprocess logs according to user-defined domain knowledge, ie. regex. Second, Drain starts from the root node of the parse tree with the preprocessed log message. The 1-st layer nodes in the parse tree represent log groups whose log messages are of different log message lengths. Third,  Drain traverses from a 1-st layer node to a leaf node. Drain selects the next internal node by the tokens in the beginning positions of the log message.Then Drain calculate similarity between log message and log event of each log group to decide whether to put the log message into existing log group. Finally, Drain update the Parser Tree by scaning the tokens in the same position of the log message and the log event.

Read more information about Drain from the following paper:

+ Pinjia He, Jieming Zhu, Zibin Zheng, and Michael R. Lyu. [Drain: An Online Log Parsing Approach with Fixed Depth Tree](https://jiemingzhu.github.io/pub/pjhe_icws2017.pdf), *IEEE International Conference on Web Services (ICWS)*, 2017.
