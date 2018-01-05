import sys
sys.path.append('../LogSig')
sys.path.append('../logparser')

from LogSig import *
import evaluator

input_dir = '../logs/HDFS/'
output_dir = 'LogSig_result/'

log_file = 'HDFS_2k.log'
log_format = 'Date Time Pid Level Component: Content' # HDFS log format

regex = ['blk_(|-)[0-9]+', '(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)']

parser=LogSig(path=input_dir, savePath=output_dir, rex=regex,
                groupNum=14, logformat=log_format)

parser.parse(log_file)

evaluator.evaluate(os.path.join(input_dir, 'HDFS_2k.log_structured.csv'),
                   os.path.join(output_dir, 'HDFS_2k.log_structured.csv'))
