
#!/usr/bin/env python


# =========================================================================
# demo.py: Example script for using the Drain log parser.
# This script demonstrates how to use the Drain algorithm to parse logs 
# and extract structured templates.
# =========================================================================

# Import necessary libraries
import sys  # System-specific parameters and functions
sys.path.append('../../')  # Add the root directory to the module search path
from logparser.Drain import LogParser  # Import the Drain log parser

# Input and output configurations
input_dir = '../../data/loghub_2k/HDFS/'  # Directory of input log file
output_dir = 'demo_result/'              # Directory for output parsing results
log_file = 'HDFS_2k.log'                 # Name of the log file to parse

# Define the log format for parsing
# For HDFS logs: "<Date> <Time> <Pid> <Level> <Component>: <Content>"
log_format = '<Date> <Time> <Pid> <Level> <Component>: <Content>'

# Regular expression list for optional preprocessing (default: [])
# Example: Replace block IDs with a generic identifier.
regex = [
    r'blk_(|-)[0-9]+',  # Replace block IDs (e.g., blk_123456)
]

# Parsing parameters
st = 0.5  # Similarity threshold for log clustering
depth = 4  # Depth of the parsing tree

# Initialize the LogParser
parser = LogParser(log_format, indir=input_dir, outdir=output_dir, depth=depth, st=st, rex=regex)

# Parse the logs
parser.parse(log_file)

