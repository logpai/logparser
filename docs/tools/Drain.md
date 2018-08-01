Drain
===

Drain is one of the representative algorithms for log parsing. It can parse logs in a streaming and timely manner. To accelerate the parsing process, Drain uses a fixed depth parse tree (See the figure below), which encodes specially designed rules for parsing.

![Sturcture of parse tree in Drain](https://ws1.sinaimg.cn/large/006tKfTcgy1ftuhiqqmazj30r40k4wgw.jpg)

**Step 1**: **Preprocess by Domain Knowledge.**

Drain allows users to provide simple regular expressions based on domain knowledge that represent commonly-used variables. Then Drain will remove the tokens matched from the raw log message by these regular expressions.

**Step 2: Search by Log Message Length.** 

Drain starts from the root node of the parse tree with the preprocessed log message. The 1-st layer nodes in the parse tree represent log groups whose log messages are of different log message lengths.

**Step 3:  Search by Preceding Tokens** .

In this step, Drain traverses from a 1-st layer node to a leaf node. Drain selects the next internal node by the tokens in the beginning positions of the log message.

**Step 4: Search by Token Similarity.** 

In this step, Drain selects the most suitable log group from the log group list. We calculate the similarity simSeq between the log message and the log event of each log group. simSeq is defined as following:

![image-20180801203750601](https://ws4.sinaimg.cn/large/006tKfTcgy1ftuhd0378sj30ge02sgls.jpg)

where $seq1$ and $seq2$ represent the log message and the log event respectively; $seq(i)$ is the $i-th$ token of the sequence; $n$ is the log message length of the sequences; function $equ$ is defined as following:





![image-20180801203904528](https://ws1.sinaimg.cn/large/006tKfTcgy1ftuheb9y8hj30ds044glw.jpg)

where $t1$ and $t2$ are two tokens. After finding the log group with the largest $simSeq$, we compare it with a predefined similarity threshold st. If $simSeq ≥ st$, Drain returns the group as the most suitable log group. Otherwise, Drain returns a flag (e.g., None in Python) to indicate no suitable log group.

**Step 5: Update the Parse Tree** 

Drain scans the tokens in the same position of the log message and the log event. If the two tokens are the same, we do not modify the token in that token position. Otherwise, we update the token in that token position by wildcard (i.e., *) in the log event. If Drain cannot find a suitable log group, it creates a new log group based on the current log message, where log IDs contains only the ID of the log message and log event is exactly the log message. Then, Drain will update the parse tree with the new log group.

![Parse Tree Update Example](https://ws4.sinaimg.cn/large/006tKfTcgy1ftuhm0xv24j30ns0fkdhb.jpg)



Read more information about Drain from the following paper:

+ Pinjia He, Jieming Zhu, Zibin Zheng, and Michael R. Lyu. [Drain: An Online Log Parsing Approach with Fixed Depth Tree](http://jiemingzhu.github.io/pub/pjhe_icws2017.pdf), *IEEE International Conference on Web Services (ICWS)*, 2017.