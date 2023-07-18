#!/usr/bin/env python

import sys
sys.path.append('../../')
from logparser.LFA import LogParser

input_dir  = '../../data/loghub_2k/HDFS/' # The input directory of log file
output_dir = 'demo_result/' # The output directory of parsing results
log_file   = 'HDFS_2k.log' # The input log file name
log_format = '<Date> <Time> <Pid> <Level> <Component>: <Content>' # HDFS log format
regex      = [] # Regular expression list for optional preprocessing (default: [])

parser = LogParser(input_dir, output_dir, log_format, rex=regex)
parser.parse(log_file)
