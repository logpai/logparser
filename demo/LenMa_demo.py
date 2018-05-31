#!/usr/bin/env python
import sys
sys.path.append('../')
from logparser import LenMa

input_dir  = '../logs/HDFS/' # The input directory of log file
output_dir = 'Lenma_result/' # The output directory of parsing results
log_file   = 'HDFS_2k.log' # The input log file name
log_format = '<Date> <Time> <Pid> <Level> <Component>: <Content>' # HDFS log format
threshold  = 0.9 # TODO description (default: 0.9)
regex      = [] # Regular expression list for optional preprocessing (default: [])

parser = LenMa.LogParser(input_dir, output_dir, log_format, threshold=threshold, rex=regex)
parser.parse(log_file)
