## Datasets

+ [Loghub_2k](#loghub_2k)
+ [Loghub_2k_corrected](#loghub_2k_corrected)
+ [Loghub](#loghub)
+ [LogPub](#logpub)

### Loghub_2k
The loghub_2k datasets are sampled from [loghub logs](https://github.com/logpai/loghub), containing 2,000 lines of log messages for each log. The message templates are extracted based on regular expressions and then manually validated and annotated. The loghub_2k datasets have been initially used for benchmarking log parsers by the work "[Tools and Benchmarks for Automated Log Parsing](https://arxiv.org/pdf/1811.03509.pdf)" in ICSE 2019.

### Loghub_2k_corrected
The loghub_2k_corrected datasets are developed by the work "[Guidelines for Assessing the Accuracy of Log Message Template Identification Techniques](https://dl.acm.org/doi/abs/10.1145/3510003.3510101)" in ICSE 2022, which further refines and fixes some of the incorrected ground-truth event templates of the original loghub_2k datasets.

### Loghub
Loghub provides a large collection of system log datasets, which are freely accessible for AI-driven log analytics research. The raw logs can be accessed at https://github.com/logpai/loghub.

### LogPub
Loghub provides large-scale raw logs, but lacks annotated event templates in such scale. To evaluate log parsers in a more rigorous and practical setting, LogPub provides large-scale mannual annotations for raw logs in Loghub. The LogPub datasets can be accessed at https://github.com/logpai/LogPub.
