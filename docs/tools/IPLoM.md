IPLoM
=====

IPLoM (Iterative Partitioning Log Mining) is one of the state-of-the-art algorithms for log parsing. It leverages the unique characteristics of log messages for iterative log partitioning, which thus enables efficient message type extraction. Since the original open-source implementation is not available anymore, we re-implement the algorithm using Python with a nice interface provided. We describe the process of IPLoM as follows.


**Step 1**: Partition by event size. Logs are partitioned into different clusters according to its length. In real world logs, it is possible that logs belong to one template are in variable length. In this case, the result of IPLoM should be postprocessed manually.

**Step 2**: Partition by token posistion. At this point, each cluster contains logs with the same length. Assuming there are m logs whose length are n in a cluster, this cluster can be regarded as an m-by-n matrix. This step based on the assumption that the column with least number of unique words (split word position) is the one contains constants. Thus, the split word position is used to partition each cluster, i.e. each generated cluster has the same word in the split word position.

**Step 3**: Partition by search for mapping. In this step, two columns of the logs are selected for further partitioning based on the mapping relation between them. To determine the two columns, the number of unique words in each column is counted (i.e. word count) and the two columns with the most frequently appearing word count are selected. There are four mapping relations: 1-1, 1-M, M-1, M-M. In the case of 1-1 relations, logs contains the same 1-1 relations in the two selected columns are partitioned to the same cluster. For 1-M and M-1 relations, we should firstly decide whether the M side column contains constants or variables. If the M side contains constants, the M side column is used partition logs in 1-M/M-1 relations. Otherwise, the 1 side column is used. Finally, logs in M-M relations are partitioned to one cluster.

**Step 4**: Log template extraction. IPLoM processes through all the clusters generated in previous steps and generates one log template for each of them. For each column in a cluster, the number of unique words is counted. If there is only one unique word in a column, the word is regarded as constant. Otherwise, the words in the column are variables and will be replaced by a wildcard in the output.


Read more information about IPLoM from the following papers:

+ Adetokunbo Makanju, A. Nur Zincir-Heywood, Evangelos E. Milios. [Clustering Event Logs Using Iterative Partitioning](https://web.cs.dal.ca/~makanju/publications/paper/kdd09.pdf), *ACM SIGKDD Conference on Knowledge Discovery and Data Mining (KDD)*, 2009.

+ Adetokunbo Makanju, A. Nur Zincir-Heywood, Evangelos E. Milios. [A Lightweight Algorithm for Message Type Extraction in System Application Logs](http://ieeexplore.ieee.org/abstract/document/5936060/), *IEEE Transactions on Knowledge and Data Engineering (TKDE)*, 2012.