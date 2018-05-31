#!/usr/bin/env python
import sys
sys.path.append('../')
from logparser import SHISO

input_dir   = '../logs/HDFS/' # The input directory of log file
output_dir  = 'SHISO_result/' # The output directory of parsing results
log_file    = 'HDFS_2k.log' # The input log file name
log_format  = '<Date> <Time> <Pid> <Level> <Component>: <Content>' # HDFS log format
regex       = [r'blk_-?\d+', r'(\d+\.){3}\d+(:\d+)?'] # Regular expression list for optional preprocessing (default: [])
maxChildNum = 4 # ToDo description
mergeThreshold = 0.1 # ToDo description
formatLookupThreshold = 0.3 # ToDo description
superFormatThreshold  = 0.85 # ToDo description

parser = SHISO.LogParser(log_format,indir=input_dir,outdir=output_dir, rex=regex, maxChildNum=maxChildNum, 
                         mergeThreshold=mergeThreshold, formatLookupThreshold=formatLookupThreshold, 
                         superFormatThreshold=superFormatThreshold)
parser.parse(log_file)
