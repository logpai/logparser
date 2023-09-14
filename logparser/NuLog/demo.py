#!/usr/bin/env python

import sys
sys.path.append('../../')
from logparser.NuLog import LogParser

input_dir = '../../data/loghub_2k/HDFS/' # The input directory of log file
output_dir = 'demo_result/'  # The output directory of parsing results
log_file = 'HDFS_2k.log'  # The input log file name
log_format = '<Date> <Time> <Pid> <Level> <Component>: <Content>'  # HDFS log format
# Regular expression list for optional preprocessing (default: [])
regex = [
    r'blk_(|-)[0-9]+' , # block id
    r'(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)', # IP
    r'(?<=[^A-Za-z0-9])(\-?\+?\d+)(?=[^A-Za-z0-9])|[0-9]+$', # Numbers
]
filters = "(\s+blk_)|(:)|(\s)"
k = 15
nr_epochs = 5 # Number of epochs to run
num_samples = 0

parser = LogParser(log_format=log_format, indir=input_dir, outdir=output_dir, filters=filters, k=k)
parser.parse(log_file, nr_epochs=nr_epochs, num_samples=num_samples)
