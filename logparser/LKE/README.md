# LKE - Log Key Extraction

LKE is one of the representative algorithms for log parsing. It first leverages empirical rules for preprocessing and then uses weighted edit distance for hierarchical clustering of log messsages. After further group splitting with fine tuning, log keys are generated from the resulting clusters.

Read more information about LKE from the following paper:

+ Qiang Fu, Jian-Guang Lou, Yi Wang, Jiang Li. [Execution Anomaly Detection in Distributed Systems through Unstructured Log Analysis](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/DM790-CR.pdf), *IEEE International Conference on Data Mining (ICDM)*, 2009.


