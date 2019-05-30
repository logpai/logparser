#!/usr/bin/env python
import sys
sys.path.append('../')
from logparser import Drain

resume_training = True
input_dir  = '../logs/HDFS/'  # The input directory of log file
output_dir = 'Drain_result/'  # The output directory of parsing results
history = "history"
log_file   = 'HDFS_1k_1.log'  # The input log file name
log_format = '<Date> <Time> <Pid> <Level> <Component>: <Content>'  # HDFS log format
# Regular expression list for optional preprocessing (default: [])
regex      = [
    r'blk_(|-)[0-9]+' , # block id
    r'(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)', # IP
    r'(?<=[^A-Za-z0-9])(\-?\+?\d+)(?=[^A-Za-z0-9])|[0-9]+$', # Numbers
]
st         = 0.5  # Similarity threshold
depth      = 4  # Depth of all leaf nodes

parser = Drain.LogParser(log_format, indir=input_dir, outdir=output_dir,  depth=depth, st=st, rex=regex, resume_training=resume_training, history=history)
parser.parse(log_file)

