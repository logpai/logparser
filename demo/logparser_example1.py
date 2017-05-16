#In this demo, the rawlog.log file is the HDFS data set logs.
#If you want to test on other data sets or using other parsers, please modify the parameters in this file or in the parser source file

import logparser

log_file = './HDFS_2k_sample.log'
output_dir = './'
log_format = 'Date Time Pid Level Component: Content'

print 
#Note: you need to set some other parameters when you try other parsers or data sets
#For example, the structured columns "removeCol" (e.g., timestamp column) that will be removed before parsing. For each data set, the structure columns are different. Wrong removeCol may result in wrong parsing results. 
#All parameter setting in our experiments are attached as comments.


logparser.parse(log_file, logformat=log_format)




