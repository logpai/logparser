LogSig
======

LogSig is a message signature based algorithm to generate system events from textual log messages. By searching
the most representative message signatures, logSig categorizes log messages into a set of event types. logSig can
handle various types of log data, and is able to incorporate human’s domain knowledge to achieve a high performance. We implemented LogSig using Python with a nice interface for benchmarking purpose.


**Step 1**: Word pair generation. In this step, each log is converted to a set of word pairs. For example, "Verification succeeded for blk_904791815409399662" is converted to the following word pairs: (Verification, succeeded), (Verification, for), (Verification, blk_904791815409399662), (succeeded, for), (succeeded, blk_904791815409399662), (for, blk_904791815409399662). Each word pair preserves the order information of the original log.

**Step 2**: Clustering. LogSig requires users to determine the number of clusters, say k, which leads to k
  randomly partitioned clusters of logs at the beginning of clustering. In each iteration of clustering, LogSig goes through all the logs and move them to other clusters if needed. For each log, potential value, which is based on word pairs generated in step 1, is calculated to decide to which cluster the log should be moved. LogSig keeps clustering untill no log is decided to move in one iteration.

**Step 3**: Log template extraction. At this point, there are k
  clusters of logs. For each cluster, words in more than half of the logs are selected as candidate words of the template. To figure out the order of candidate words, LogSig goes through all the logs in the cluster and count how many times each permutation appears. The most frequent one is the log template of the cluster.

Read more information about LogSig from the following papers:

+ Liang Tang, Tao Li, Chang-Shing Perng. [LogSig: Generating System Events from Raw Textual Logs](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.222.9320&rep=rep1&type=pdf), *ACM International Conference on Information and Knowledge Management (CIKM)*, 2011.
  