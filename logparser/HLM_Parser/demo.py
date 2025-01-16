#!/usr/bin/env python

import sys
sys.path.append('../../')
# from logparser.Drain import LogParser
from logparser.HLM_Parser import LogParser

input_dir  = '../../data/loghub_2k/HDFS/' # The input directory of log file
output_dir = 'demo_result/'  # The output directory of parsing results
log_file   = 'HDFS_14template1.log'  # The input log file name
log_format = '<Date> <Time> <Pid> <Level> <Component>: <Content>'  # HDFS log format
# Regular expression list for optional preprocessing (default: [])
# regex      = [
#     r'blk_(|-)[0-9]+' , # block id
#     r'(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)', # IP
#     r'(?<=[^A-Za-z0-9])(\-?\+?\d+)(?=[^A-Za-z0-9])|[0-9]+$', # Numbers
# ]
regex = [
    r'(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)',  # IP
]
st         = 0.5  # Similarity threshold
depth      = 4  # Depth of all leaf nodes
tau        = 0.57  # Message type threshold (default: 0.5)
delimiter_pattern = r"\.|/|_"
#delimiter_pattern = r""

parser = LogParser(log_format, indir=input_dir, outdir=output_dir,  depth=depth, st=st, tau=tau, rex=regex, delimiter_pattern=delimiter_pattern)
parser.parse(log_file)
