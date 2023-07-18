#!/usr/bin/env python
"""
This script demonstrates the usage of logparser to parse your own log data.
To get started, please first install the logparser via `pip install logpai`.
To get better parsing results, you are suggested to tune the hyper-parameters
`st` and `depth`.
"""

from logparser.Drain import LogParser

input_dir = '../data/test_log/' # The input directory of log file
output_dir = 'result/'  # The output directory of parsing results
log_file = 'unknow.log'  # The input log file name
log_format = '<Date> <Time> <Level>:<Content>' # Define log format to split message fields
# Regular expression list for optional preprocessing (default: [])
regex = [
    r'(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)' # IP
]
st = 0.5  # Similarity threshold
depth = 4  # Depth of all leaf nodes

parser = LogParser(log_format, indir=input_dir, outdir=output_dir,  depth=depth, st=st, rex=regex)
parser.parse(log_file)
