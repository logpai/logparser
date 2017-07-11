#!/usr/bin/env python
import sys
import logparser

input_dir = '../logs/HDFS/'
output_dir = 'result/'

log_file = 'HDFS_2k.log'
event_template = 'HDFS_2k_templates_groundtruth.csv'
log_format = 'Date Time Pid Level Component: Content' # HDFS log format

parser = logparser.Parser(logformat=log_format, indir=input_dir, outdir=output_dir)
parser.parse(log_file, event_template)
