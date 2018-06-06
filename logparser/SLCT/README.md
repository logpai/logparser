# SLCT - simple logfile clustering tool

[SLCT](http://ristov.github.io/slct/) is a tool that was designed to find clusters in logfile(s), so that each cluster corresponds to a certain line pattern that occurs frequently enough. With the help of SLCT, one can quickly build a model of logfile(s), and also identify rare lines that do not fit the model (and are possibly anomalous).

To provide a common interface for log parsing, we write a Python wrapper around the original [SLCT source code in C](http://ristov.github.io/slct/slct-0.05.tar.gz) (released under GPL license). This also eases our benchmarking experiments. Same with the original release, our implementation has only been tested successfully on Linux (compiled with GCC). We tried running the tool on Windows using cygwin with GCC installed, but failed with a crash. You are advised to use the SLCT tool on Linux. But it is still possible to work around the issue if some efforts are made. 

Read more information about SLCT from the following paper:
+ Risto Vaarandi. [A Data Clustering Algorithm for Mining Patterns from Event Logs](http://www.quretec.com/u/vilo/edu/2003-04/DM_seminar_2003_II/ver1/P12/slct-ipom03-web.pdf), *Proceedings of the 3rd IEEE Workshop on IP Operations & Management (IPOM)*, 2003.

