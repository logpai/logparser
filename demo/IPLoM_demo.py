#!/usr/bin/env python
import sys
sys.path.append('../IPLoM')
sys.path.append('../logparser')
import IPLoM
import evaluator
import os

input_dir = '../logs/HDFS/'
output_dir = 'IPLoM_result/'

log_file = 'HDFS_2k.log'
log_format = 'Date Time Pid Level Component: Content' # HDFS log format
regex = ['blk_(|-)[0-9]+', '(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)']

parser = IPLoM.LogParser(log_format=log_format,indir=input_dir,outdir=output_dir,
                         maxEventLen=120, step2Support=0, CT=0.35, lowerBound=0.25,
                         upperBound=0.9, rex=regex)

parser.parse(log_file)

evaluator.evaluate(os.path.join(input_dir, 'HDFS_2k.log_structured.csv'),
                   os.path.join(output_dir, 'HDFS_2k.log_structured.csv'))
