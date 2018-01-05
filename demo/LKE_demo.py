#!/usr/bin/env python
import sys
sys.path.append('../LKE')
sys.path.append('../logparser')
import LKE
import evaluator
import os

input_dir = '../logs/HDFS/'
output_dir = 'LKE_result/'

log_file = 'HDFS_2k.log'
log_format = 'Date Time Pid Level Component: Content' # HDFS log format
regex = ['blk_(|-)[0-9]+', '(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)']

parser = LKE.LogParser(log_format=log_format, indir=input_dir, outdir=output_dir,
                       dataName='HDFS', rex=regex, threshold2=5)

parser.parse(log_file)

evaluator.evaluate(os.path.join(input_dir, 'HDFS_2k.log_structured.csv'),
                   os.path.join(output_dir, 'HDFS_2k.log_structured.csv'))
