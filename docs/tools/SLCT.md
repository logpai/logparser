SLCT
====

[SLCT](http://ristov.github.io/slct/) is a simple logfile clustering tool designed to find clusters in logfile(s), so that each cluster corresponds to a certain line pattern that occurs frequently enough. With the help of SLCT, one can quickly build a model of logfile(s), and also identify rare lines that do not fit the model (and are possibly anomalous).


**Step 1**: Word vocabulary construction. SLCT makes a pass over the words in all the logs and count the occurence of them. In this step, the position of the word is also considered. For example, “send” as the 1st word of a log and “send” as the 2nd word of a log are considered different. Word occurs more than support threshold, say N, is defined as frequent word.

**Step 2**: Cluster candidates construction. In this step, SLCT makes the second pass over all the logs, while at this time it focuses on frequent words. All the frequent words in a log will be extracted be the log template of itself. The number of logs that match a certain log template is counted, and each log template represents a cluster candidate.

**Step 3**: Log template extraction. SLCT goes through all cluster candidates and log templates whose corresponding cluster contains more than N logs are selected as the output templates. The logs of clusters which are not selected are placed into outlier class.

**Step 4**: Cluster combination. This step is optional. SLCT could make a pass through all selected clusters and combine two clusters if one of them is the subcluster of the other. For example, cluster “PacketResponder 1 for block * terminating” is the subcluster of “PacketResponder * for block * terminating”. Therefore, these two clusters will be combined in this step.

To provide a common interface for log parsing, we write a Python wrapper around the original [SLCT source code in C](http://ristov.github.io/slct/slct-0.05.tar.gz) (released under GPL license). This also eases our benchmarking experiments. Same with the original release, our implementation has only been tested successfully on Linux (compiled with GCC). We tried running the tool on Windows using cygwin with GCC installed, but failed with a crash. You are advised to use the SLCT tool on Linux. But it is still possible to work around the issue if some efforts are made. 

Read more information about SLCT from the following paper:
+ Risto Vaarandi. [A Data Clustering Algorithm for Mining Patterns from Event Logs](http://www.quretec.com/u/vilo/edu/2003-04/DM_seminar_2003_II/ver1/P12/slct-ipom03-web.pdf), *IEEE Workshop on IP Operations & Management (IPOM)*, 2003.