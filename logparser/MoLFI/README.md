# MoLFI
Multi-objective Log message Format Identification

MoLFI is a tool implementing a search-based approach to solve the problem of log message format identification.
More details on this approach is available in this paper:

> Salma Messaoudi, Annibale Panichella, Domenico Bianculli, Lionel Briand, and Raimondas Sasnauskas. __A Search-based Approach for Accurate Identification of Log Message Formats__. In Proceedings of ICPC ’18: 26th IEEE/ACM International Conference on Program Comprehension (ICPC ’18).  Available online at http://hdl.handle.net/10993/35286


A log message template is a two parts message; one fixed and one variable.

     For example: "File config.xml sent at 191.168.1.3"

     "File", "sent" and "at" are the fixed part because the represent an event of sending a file.

     "config.xml" and "191.168.1.3" are the variable part because they change with the occurrence of the sending event.

MoLFI uses an evolutionary approach based on NSGA-II to solve this problem.

MoLFI applies the following steps:

1. Pre-processing the log file (detect trivial variable parts using domain knowledge).
1. Run NSGA-II algorithm.
1. Post-processing: apply corrections to the resulting solutions.

MoLFI is implemented as a python project (v3.6.0).

This package contains the source code of the tool with two executable scripts.

* **MoLFI.py**: the script used to run MoLFI. This script can be used from the command line.   

* **validation.py**: this script is used to validate the generated templates. It will apply a comparison between the generated templates and the correct templates (the oracle files)


To re-run the experiments, the **MoLFI** and the datasets used for the evaluation **ICPC-2018-Artifacts** should be under the same directory

-> The ICPC-2018-Artifacts repository is accessible from the following link: https://github.com/SalmaMessaoudi/ICPC-2018-Artifacts.git

-> go under the folder **ICPC-2018-Artifacts** and run **make**.

Under the same folder (ICPC-2018-Artifacts), a new folder will be created (Experiments_Results) with a sub-folder called "Metrics" containing the validation scores for each dataset and another sub-folder "Validation" with the generated templates being compared with the oracle.

To run MoLFI on a single log file:

- from the command line, run the MoLFI.py script and precise the following arguments:
*  -l : specify the log file
*  -s : specify the separator of the log file contents (e.g. a comma, a tab character)
*  -c : precise the position of the log messages in the log file (e.g. 3 for third column)
*  -p : specify where to save the generated templates.
*  -r : provide the regular expressions if any (one after the other, separated by a normal space)

Example:

python3.6 MoLFI.py -l ../MoLFI_experiments/Datasets/BGL/2K/BGL_2K_log_messages.txt -s "\n" -c 0 -p templates.pkl -r "core\.[0-9]*" "0x([a-zA-Z]|[0-9])+"
