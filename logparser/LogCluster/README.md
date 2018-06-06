# LogCluster

[LogCluster](http://ristov.github.io/logcluster/) is a Perl-based tool for log file clustering and mining line patterns from log files. The development of LogCluster was inspired by [SLCT](http://ristov.github.io/slct/), but LogCluster includes a number of novel features and data processing options. 

To provide a common interface for log parsing, we write a Python wrapper around the original [LogCluster source code in Perl](https://github.com/ristov/logcluster) (released under GPL license). This also eases our benchmarking experiments. The implementation has been tested on both Linux and Windows systems. Especially, [Strawberry Perl](http://strawberryperl.com/) was installed to run the Perl program on Windows.

Read more information about LogCluster from the following paper:

+ Risto Vaarandi, Mauno Pihelgas. [LogCluster - A Data Clustering and Pattern Mining Algorithm for Event Logs](http://ristov.github.io/publications/cnsm15-logcluster-web.pdf), *Proceedings of the 11th International Conference on Network and Service Management (CNSM)*, 2015.
