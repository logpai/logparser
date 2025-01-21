#!/usr/bin/env python

import sys
sys.path.append('../../')
from logparser.Drain import LogParser

input_dir  = '../../data/loghub_2k/OpenStack/' # The input directory of log file
output_dir = 'demo_result/'  # The output directory of parsing results
log_file   = 'OpenStack_2k.log'  # The input log file name
log_format = '<Logrecord> <Date> <Time> <Pid> <Level> <Component> \[<ADDR>\] <Content>'  # HDFS log format
# Regular expression list for optional preprocessing (default: [])
# regex= [
#             r"((\d+\.){3}\d+,?)+",
#             r"/.+?\s",
#             #r"\d+, (\[instance:\s*)[^]]+(\])"
#         ],

regex = [r'((\d+\.){3}\d+,?)+',
         r'/.+?\s',
         r'\d+'],

# regex = [ r'(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)' ]
# regex      = [
#     r'blk_(|-)[0-9]+' , # block id
#     r'(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)', # IP
#     r'(?<=[^A-Za-z0-9])(\-?\+?\d+)(?=[^A-Za-z0-9])|[0-9]+$', # Numbers
# ]

st         = 0.5  # Similarity threshold
depth      = 5  # Depth of all leaf nodes

parser = LogParser(log_format, indir=input_dir, outdir=output_dir,  depth=depth, st=st, rex=regex)
parser.parse(log_file)

# "OpenStack": {
#     "log_file": "OpenStack/OpenStack_2k.log",
#     "log_format": "<Logrecord> <Date> <Time> <Pid> <Level> <Component> \[<ADDR>\] <Content>",
#     "regex": [r"((\d+\.){3}\d+,?)+", r"/.+?\s", r"\d+"],
#     "st": 0.5,
#     "depth": 5,
# },

# "OpenStack": {
#     "log_file": "OpenStack/OpenStack_2k.log",
#     "log_format": "<Logrecord> <Date> <Time> <Pid> <Level> <Component> \[<ADDR>\] <Content>",
#     "regex": [r"((\d+\.){3}\d+,?)+", r"/.+?\s", r"\d+"],
#     "st": 0.5,
#     "depth": 5,
# },