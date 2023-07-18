#!/usr/bin/env python

import sys
sys.path.append('../../')
from logparser.SHISO import LogParser

input_dir   = '../../data/loghub_2k/HDFS/' # The input directory of log file
output_dir  = 'demo_result/' # The output directory of parsing results
log_file    = 'HDFS_2k.log' # The input log file name
log_format  = '<Date> <Time> <Pid> <Level> <Component>: <Content>' # HDFS log format
regex       = [r'blk_-?\d+', r'(\d+\.){3}\d+(:\d+)?'] # Regular expression list for optional preprocessing (default: [])
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
