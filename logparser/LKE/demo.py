#!/usr/bin/env python

import sys
sys.path.append('../../')
from logparser.LKE import LogParser

input_dir       = '../../data/loghub_2k/HDFS/' # The input directory of log file
output_dir      = 'demo_result/' # The output directory of parsing results
log_file        = 'HDFS_2k.log' # The input log file name
log_format      = '<Date> <Time> <Pid> <Level> <Component>: <Content>' # HDFS log format
regex           = [r'blk_-?\d+', r'(\d+\.){3}\d+(:\d+)?'] # Regular expression list for optional preprocessing (default: [])
split_threshold = 3 # The threshold used to determine group splitting (default: 4)

parser = LogParser(log_format=log_format, indir=input_dir, outdir=output_dir,
                   rex=regex, split_threshold=split_threshold)        
parser.parse(log_file)
