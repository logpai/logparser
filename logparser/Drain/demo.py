#!/usr/bin/env python

import sys

sys.path.append("../../")
from logparser.Drain import LogParser

input_dir = ""  # The input directory of log file
output_dir = "demo_results/"  # The output directory of parsing results
log_file = "syslog"  # The input log file name
log_format = "<Date> <Time> <Pid> <Level> <Component>: <Content>"  # HDFS log format
# Regular expression list for optional preprocessing (default: [])
regex = [r"^(\S+)\s+(\w{3}\s+\d{2})\s+(\d{2}:\d{2}:\d{2})\s+(\S+)\s+(\S+)\s+(.*)$"]
st = 0.5  # Similarity threshold
depth = 4  # Depth of all leaf nodes

parser = LogParser(
    log_format, indir=input_dir, outdir=output_dir, depth=depth, st=st, rex=regex
)
parser.parse(log_file)
