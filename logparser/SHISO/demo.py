#!/usr/bin/env python

import sys
sys.path.append('../../')
from logparser.SHISO import LogParser

input_dir = ""  # The input directory of log file
output_dir = "demo_results/"  # The output directory of parsing results
log_file = "syslog"  # The input log file name
log_format = "<Date> <Time> <Pid> <Level> <Component>: <Content>"  # HDFS log format
# Regular expression list for optional preprocessing (default: [])
regex = [r"^(\S+)\s+(\w{3}\s+\d{2})\s+(\d{2}:\d{2}:\d{2})\s+(\S+)\s+(\S+)\s+(.*)$"]

maxChildNum = 4 # The maximum number of children for each internal node
mergeThreshold = 0.1 # Threshold for searching the most similar template in the children
formatLookupThreshold = 0.3 # Lowerbound to find the most similar node to adjust
superFormatThreshold  = 0.85 # Threshold of average LCS length, determing whether or not to create a super format

parser = LogParser(log_format,
                   indir=input_dir,
                   outdir=output_dir,
                   rex=regex,
                   maxChildNum=maxChildNum,
                   mergeThreshold=mergeThreshold,
                   formatLookupThreshold=formatLookupThreshold,
                   superFormatThreshold=superFormatThreshold)
parser.parse(log_file)
