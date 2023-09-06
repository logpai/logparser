LKE
===

LKE (Log Key Extraction) is one of the representative algorithms for log parsing. It first leverages empirical rules for preprocessing and then uses weighted edit distance for hierarchical clustering of log messages. After further group splitting with fine-tuning, log keys are generated from the resulting clusters.

**Step 1**: Log clustering. Weighted edit distance is designed to evaluate the similarity between two logs, WED=\sum_{i=1}^{n}\frac{1}{1+e^{x_{i}-v}} . n is the number of edit operations to make two logs the same, x_{i} is the column index of the word which is edited by the i-th operation, v is a parameter to control weight. LKE links two logs if the WED between them is less than a threshold \sigma . After going through all pairs of logs, each connected component is regarded as a cluster. Threshold \sigma is automatically calculated by utilizing K-means clustering to separate all WED between all pair of logs into 2 groups, and the largest distance from the group containing smaller WED is selected as the value of \sigma .

**Step 2**: Cluster splitting. In this step, some clusters are further partitioned. LKE firstly finds out the longest common sequence (LCS) of all the logs in the same cluster. The rests of the logs are dynamic parts separated by common words, such as “/10.251.43.210:55700” or “blk_904791815409399662”. The number of unique words in each dynamic part column, which is denoted as |DP| , is counted. For example, |DP|=2 for the dynamic part column between “src:” and “dest:” in log 2 and log 3. If the smallest |DP| is less than threshold \phi , LKE will use this dynamic part column to partition the cluster.

**Step 3**: Log template extraction. This step is similar to step 4 of IPLoM. The only difference is that LKE removes all variables when they generate log templates, instead of representing them by wildcards.

Read more information about LKE from the following paper:

+ Qiang Fu, Jian-Guang Lou, Yi Wang, Jiang Li. [Execution Anomaly Detection in Distributed Systems through Unstructured Log Analysis](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/DM790-CR.pdf), *IEEE International Conference on Data Mining (ICDM)*, 2009.
