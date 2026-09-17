# Drain + "Preprocessing is All You Need"

## What Are the New Framework Features?

Getting tired of low parsing accuracies? Our log preprocessing framework is here to save your day! Go to ```./benchmark/logparser/utils/preprocessing.py``` to check the implementation details.

### More Regexes
Our study identified several categories of variables that are not matched by the default Loghub regexes but can be identified using **consistent and generalizable** regexes. Therefore, we enriched the regex set used for log preprocessing. The regexes used in our new framework are introduced in the following table: 

| Semantic       | Regex                                                                                                         | Introduction                                                           |
|----------------|---------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------|
| IPv4_port      | r'(/\|)(\d+\.){3}\d+(:\d+)?'                                                                                  | IPv4 addresses (optional: with port).                                  |
| host_port      | r'([\w-]+\.)+[\w-]+\:\d+'                                                                                     | Domain host names with port.                                           |
| package_host   | r'([\w-]+\.){2,}[\w-]+(\$[\w-]+)*(\@[\w-]+)?'                                                                 | Package (optional: with port and node)/Domain host names without port. |
| Mac_address    | r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'                                                                  | MAC addresses.                                                         |
| IPv6           | r'(([0-9a-fA-F]{1,4}:){7}([0-9a-fA-F]{1,4}\|:)\|(([0-9a-fA-F]{1,4}:){1,7}\|:):((:[0-9a-fA-F]{1,4}){1,7}\|:))' | IPv6 addresses.                                                        |
| path           | r'(/\|)(([\w.-]+\|\<\*\>)/)+([\w.-]+\|\<\*\>)'                                                                | File paths.                                                            |
| size           | r'\b\d+\.?\d*\s?([KGTMkgtm]?(B\|b)\|([KGTMkgtm]))\b'                                                          | Memory sizes.                                                          |
| duration       | r'\b\<?\d+\s?(sec\|s\|ms)\b'                                                                                    | Time duration.                                                         |
| block          | r'blk\_\-?\d+'                                                                                                | (System specific) Block identifier.                                    |
| time           | r'\b\d{2}:\d{2}(:\d{2}\|:\d{2},\d+)?\b'                                                                       | Time information.                                                      |
| date           | r'\b(\d{4}-\d{2}-\d{2})\|\d{4}/\d{2}/\d{2}\b'                                                                 | Date information.                                                      |
| numerical      | r'\b(\-?\+?\d+\.?\d*)\b\|\b0[Xx][a-fA-F\d]+\b\|\b[a-fA-F\d]{4,}\b'                                            | Numerical values: integers, floats, or hexidecimal.                    |
| url            | r'\bhttps?:\/\/(www\.)?[a-zA-Z0-9-]+(\.[a-zA-Z]{2,})+(:[0-9]{1,5})?(\/[^\s]*)?\b'                             | URL.                                                                   |
| weekday_months | r'\b(%s)\b' % '\|'.join(weekday_abb+weekday+month_abb+months)                                                 | Weekdays or months (full names or abbreviations).                      |

### Well Organized Orders
The variable identification in preprocessing is done in a sequence: a token will be converted into a placeholder once it has been identified as a variable. Therefore, a poorly organized identification order may cause problems in parsing and lead to parsing accuracy decrement. For example, if time variables are detected before MAC addresses, then a MAC address "00:00:00:12:34:56" will be replaced as "<\*>:<\*>" instead of the correct form "<\*>." Therefore, we carefully organized the detection sequence as:
```
'url', 'IPv4_port', 'host_port', 'package_host', 'IPv6', 'Mac_address', 'time', 'path', 'block', 'date', 'duration', 'size', 'numerical', 'weekday_months'
```

### Customizable Masks
Our framework allows users to customize the masks for variables. For example, an IPv4 address with port can be masked as either the finegrained "<\*>:<\*>" or the standard form "<\*>". The framework leverages "<\*>" for default parsing, but customizable masks can be managed using the ```regex_map``` dictionary and enabled in parsers.

### Easy Knowledge Management
Have some domain specific regexes in your mind? Add it to the regex set! Update the ```regex_match``` dictionary and ```sequence``` list to preprocess your log.

## Know Your Targets (the variables)
Loghub provides various regexes for log preprocessing. These regexes were selected based on the domain knowledge for each system. We summarized the regexes and de-duplicated them as follows: 
![image](./plots/default-regex.png?raw=true)

According to RQ1, we found that using all these default regexes is insufficient for variable detection in the preprocessing stage. Hence, we carried out a study on the non-matchable variables from Loghub-2k and manually categorized them. The two authors independently labeled a small subset and discussed the category range. Leveraging the range, the two authors then labeled the remaining variables independently and discussed the final labels. The labeled variables can be checked at ``not_matched_variables.csv``. A summary of the variable types and their ratios is available here:

![image](./plots/non-matchable.png?raw=true)

Our framework aims to reduce the not-matching number of generalizable (i.e., not customized or system-specific) variables (e.g., IPv6 addresses).

## Dataset
We used the smaller-scale dataset ``Loghub-2k`` for variable extraction and categorization; the framework is developed based on the findings in this dataset. To replicate the log parsing process and test the generalizability of our findings, we used the ``Loghub 2.0`` dataset for framework impact evaluation. The two datasets contain labeled log messages from 14 different systems. Both 2k and the full 2.0 version log data, along with their detailed introductions, can be found at https://github.com/logpai/loghub-2.0.

## Parsing Tools
Our work focuses on improving the performance of statistic-based parsers with **manageable, interpretable, and generalizable** knowledge provided in the preprocessing stage. According to the Loghub 2.0 results, only four statistic-based log parsers (i.e., Drain, IPLoM, LFA, and LogCluster) can parse all the full-sized log files in 12 hours. Considering the applicability of these four tools in real-life usage, we only evaluated them in our study. The implementation codes are inherited from the Loghub 2.0 repository. 



## Replicate the Results
Result replication is made easy! 

### Overall Performance
Run the following commands to obtain the parsing result and evaluations (GA, PA, FGA, FTA) on all log messages:

```
cd benchmark/
./run_all_full.sh
```

We illustrate the evaluation results of the four statistic-based parsers in the following box plot. The blue boxes indicate the parsers with the original preprocessing function, while the yellow boxes show the results of parsers with the new preprocessing framework. The red lines show the medians and the green arrows indicate the means.

![image](./plots/comparison_full.png?raw=true)

### Performance on Different Complexity Subgroups
The log messages are divided into three subgroups according to the number of variables in the message: ``#Param=0 (complexity=1)``, ``0<#Param<5 (complexity=2)``, and ``#Param>=5 (complexity=3)``. Run the following commands to obtain the parsing result and evaluations (GA, PA, FGA, FTA) on log messages in different subgroups:

```
cd benchmark/
./run_complexity_full.sh
```

The following plot visualizes the average evaluation results of log parsers on logs with different numbers of variables. The red dot lines illustrate the original results obtained with the previous preprocessing function.

![image](./plots/complexity_full_all.png?raw=true)

### Performance on Different Frequency Subgroups
We extract the messages with the most frequent 10\% and the least frequent 10\% templates and evaluate the impact brought by our framework. Run the following commands to obtain the parsing result and evaluations (GA, PA, FGA, FTA) on log messages in different subgroups:

```
cd benchmark/
./run_frequency_full.sh
```

The following plot visualizes the average evaluation results of log parsers on logs with different frequencies (i.e., the most frequent 10% and the least frequent 10%.) The red dot lines illustrate the original results obtained with the previous preprocessing function.

![image](./plots/frequency_full_all.png?raw=true)
