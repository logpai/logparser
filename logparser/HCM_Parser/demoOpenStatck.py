#!/usr/bin/env python

import sys
sys.path.append('../../')
from logparser.MLParser import LogParser

input_dir  = '../../data/loghub_2k/OpenStack/'  # The input directory of log file
output_dir = '/demo_result/'  # The output directory of parsing results
log_file   = 'OpenStack_test.log'  # The input log file name
log_format = '<Logrecord> <Date> <Time> <Pid> <Level> <Component> \[<ADDR>\] <Content>'  # HDFS log format
# Regular expression list for optional preprocessing (default: [])
regex      = [r"((\d+\.){3}\d+,?)+", r"/.+?\s", r"\\d+"]
# regex = [
#     r'(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)',  # IP
# ]
st         = 0.5  # Similarity threshold
depth      =5  # Depth of all leaf nodes
tau        = 0.75  # Message type threshold (default: 0.5)
#delimiter_pattern = r"\.|/|_"
delimiter_pattern = r""

parser = LogParser(log_format, indir=input_dir, outdir=output_dir,  depth=depth, st=st, tau=tau, rex=regex, delimiter_pattern=delimiter_pattern)
parser.parse(log_file)
