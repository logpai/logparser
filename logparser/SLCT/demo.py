#!/usr/bin/env python

import sys
sys.path.append('../../')
from logparser.SLCT import LogParser

input_dir  = '../../data/loghub_2k/HDFS/'  # The input directory of log file
output_dir = 'demo_result/'  # The output directory of parsing results
log_file   = 'HDFS_2k.log'  # The input log file name
log_format = '<Date> <Time> <Pid> <Level> <Component>: <Content>'  # HDFS log format
support    = 10  # The minimum support threshold
regex      = []  # Regular expression list for optional preprocessing (default: [])

parser = LogParser(log_format=log_format, indir=input_dir, outdir=output_dir,
                   support=support, rex=regex)
parser.parse(log_file)
