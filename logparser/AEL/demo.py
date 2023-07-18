#!/usr/bin/env python

import sys
sys.path.append('../../')
from logparser.AEL import LogParser

input_dir     = '../../data/loghub_2k/HDFS/' # The input directory of log file
output_dir    = 'demo_result/' # The output directory of parsing results
log_file      = 'HDFS_2k.log' # The input log file name
log_format    = '<Date> <Time> <Pid> <Level> <Component>: <Content>' # HDFS log format
minEventCount = 2 # The minimum number of events in a bin
merge_percent = 0.5 # The percentage of different tokens
regex         = [r'blk_-?\d+', r'(\d+\.){3}\d+(:\d+)?'] # Regular expression list for optional preprocessing (default: [])

parser = LogParser(input_dir, output_dir, log_format, rex=regex,
                   minEventCount=minEventCount, merge_percent=merge_percent)
parser.parse(log_file)
