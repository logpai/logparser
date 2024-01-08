#!/usr/bin/env python

import sys

sys.path.append("../../")
from logparser.LFA import LogParser

input_dir = ""  # The input directory of log file
output_dir = "demo_results/"  # The output directory of parsing results
log_file = "syslog"  # The input log file name
log_format = "<Date> <Time> <Pid> <Level> <Component>: <Content>"  # HDFS log format
# Regular expression list for optional preprocessing (default: [])
regex = [r"^(\S+)\s+(\w{3}\s+\d{2})\s+(\d{2}:\d{2}:\d{2})\s+(\S+)\s+(\S+)\s+(.*)$"]

parser = LogParser(input_dir, output_dir, log_format, rex=regex)
parser.parse(log_file)
