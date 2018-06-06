# AEL - Abstracting Execution Logs

AEL is one of the state-of-the-art log parsing approaches, which comprises four steps: anonymize, tokenize, categorize, and reconcile. In particular, in the reconcile step, the original algorithm merges events that have only a different token. However, this process cannot handle the cases where one single template multiple different parameter tokens. To improve the generability of this algorithm, we use a parameter merge_percent to set the percentage of different tokens when merging two events.

Read more information about AEL from the following papers:

+ Zhen Ming Jiang, Ahmed E. Hassan, Parminder Flora, Gilbert Hamann. [Abstracting Execution Logs to Execution Events for Enterprise Applications](https://www.researchgate.net/profile/Ahmed_E_Hassan/publication/4366728_Abstracting_Execution_Logs_to_Execution_Events_for_Enterprise_Applications_Short_Paper/links/5577f2cf08aeacff200054cd/Abstracting-Execution-Logs-to-Execution-Events-for-Enterprise-Applications-Short-Paper.pdf), **, 2008.

+ Zhen Ming Jiang, Ahmed E. Hassan, Gilbert Hamann, Parminder Flora. [An Automated Approach for Abstracting Execution Logs to Execution Events](http://www.cse.yorku.ca/~zmjiang/publications/jsme2008.pdf), *J. Softw. Maint. Evol.: Res. Pract. (JSME)*, 2008.


