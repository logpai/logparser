#!/usr/bin/env python

import sys
sys.path.append('../../')
from logparser.logmatch import RegexMatch

input_dir = '../../data/loghub_2k/HDFS/' # The input directory
output_dir = 'logmatch_result/' # The result directory
log_file = input_dir + 'HDFS_2k.log' # The input log file path
log_format = '<Date> <Time> <Pid> <Level> <Component>: <Content>' # HDFS log format
n_workers = 1 # The number of workers in parallel
template_file = log_file + '_templates.csv' # The event template file path

if __name__ == "__main__":
    matcher = RegexMatch(outdir=output_dir, n_workers=n_workers, logformat=log_format)
    matcher.match(log_file, template_file)
