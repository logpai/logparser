#!/usr/bin/env python

import sys
sys.path.append('../../')
from logparser.LogMine import LogParser

input_dir  = '../../data/loghub_2k/HDFS/' # The input directory of log file
output_dir = 'demo_result/' # The output directory of parsing results
log_file   = 'HDFS_2k.log' # The input log file name
log_format = '<Date> <Time> <Pid> <Level> <Component>: <Content>' # HDFS log format
levels     = 2 # The levels of hierarchy of patterns
max_dist   = 0.001 # The maximum distance between any log message in a cluster and the cluster representative
k          = 1 # The message distance weight (default: 1)
regex      = []  # Regular expression list for optional preprocessing (default: [])

parser = LogParser(input_dir, output_dir, log_format, rex=regex, levels=levels, max_dist=max_dist, k=k)
parser.parse(log_file)
