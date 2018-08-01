Spell
===

Spell is an online streaming method to parse logs, which utilizes a longest common subsequence based approach. The key observation is that, if we view the output by a log printing statement (which is a log entry) as a sequence , in most log printing statements, the constant that represents a message type often takes a majority part of the sequence and the parameter values take only a small portion. If two log entries are produced by the same log printing statement stat , but only differ by having different parameter values, the LCS of the two sequences is very likely to be the constant in the code stat , implying a message type.

Initially, the LCSMap list is empty. When a new log entry $e_i$  arrives, it is firstly parsed into a token sequence $s_i$  using a set of delimiters.  After that, we compare $s_i$  with the LCSseq’s from all LCSObjects in the current LCSMap, to see if $s_i$  “matches” one of the existing LCSseq’s (hence, line id $i$  is added to the lineIds of the corresponding LCSObject), or we need to create a new LCSObject for LCSMap.

Spell's wordflow is as follows:

![image-20180801205611035](https://ws4.sinaimg.cn/large/006tKfTcgy1ftuhw22syvj31j608ujtu.jpg)





Read more information about Drain from the following paper:

+ Min Du, Feifei Li. [Spell: Streaming Parsing of System Event Logs](https://www.cs.utah.edu/~lifeifei/papers/spell.pdf), *IEEE International Conference on Data Mining (ICDM)*, 2016.

