#!/usr/bin/env python
import sys
sys.path.append('../logparser')
import logparser

input_dir = '../logs/HPC/'
output_dir = 'result/'

log_file = 'HPC_2k.log'
log_format = 'ID Node Component State Time Flag Content' # HPC log format
# log_format = 'Month Date Time Level Component: Content' # Linux log format
# log_format = '\[Time\] \[Level\] Content' # Apache log format
# log_format = 'Date Time, Level                  Component    Content' # Windows log format
# log_format = 'Date Time Pid Level Component: Content' # HDFS log format

parser = logparser.Parser(logformat=log_format, indir=input_dir, outdir=output_dir)
parser.parse(log_file)



# Match mode
# event_template = 'HDFS_2k_templates_groundtruth.csv'
# parser.parse(log_file, event_template)

