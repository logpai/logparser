Parsers: A Brief Introduction of Principle of the Parsers 
======

SLCT
--------
SLCT is the first log parser, which is proposed by Vaarandi in [#SLCT03]. Inspired by association rule, SLCT parses logs in four steps.

* Step 1: Word vocabulary construction. SLCT makes a pass over the words in all the logs and count the occurence of them. In this step, the position of the word is also considered. For example, “send” as the 1st word of a log and “send” as the 2nd word of a log are considered different. Word occurs more than support threshold, say N, is defined as frequent word.

* Step 2: Cluster candidates construction. In this step, SLCT makes the second pass over all the logs, while at this time it focuses on frequent words. All the frequent words in a log will be extracted be the log template of itself. The number of logs that match a certain log template is counted, and each log template represents a cluster candidate.

* Step 3: Log template extraction. SLCT goes through all cluster candidates and log templates whose corresponding cluster contains more than N logs are selected as the output templates. The logs of clusters which are not selected are placed into outlier class.

* Step 4: Cluster combination. This step is optional. SLCT could make a pass through all selected clusters and combine two clusters if one of them is the subcluster of the other. For example, cluster “PacketResponder 1 for block * terminating” is the subcluster of “PacketResponder * for block * terminating”. Therefore, these two clusters will be combined in this step.

IPLoM
--------


LKE
--------


LogSig
--------