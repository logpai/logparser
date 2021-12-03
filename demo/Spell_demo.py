#!/usr/bin/env python
import sys
sys.path.append('../')
from logparser import Spell

input_dir  = '../logs/f/'  # The input directory of log file
output_dir = 'f_result/'  # The output directory of parsing results
log_file   = 'result.log'  # The input log file name
log_format = "<Date> <Time> <Type> <Component> <Content>"
tau        = 0.3  # Message type threshold (default: 0.5)
regex      = ["::(.*)"]  # Regular expression list for optional preprocessing (default: [])
regex_remove = ['-{2,99}',"/\s\s+/g,"] # Regular expression list for removing certain patterns from the data before Spell starts (for example remove multiple ":" or remove multiple spaces including tabs)

parser = Spell.LogParser(input_dir, output_dir, log_format, tau, regex, regex_remove=regex_remove)
parser.parse(log_file)
