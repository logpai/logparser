#!/usr/bin/env python
import sys
sys.path.append('../logparser')
import logparser

input_dir = '../logs/' # The input log data directory
output_dir = 'result/' # The result directory
num_workers = 1 # Set the number of processors to run in parallel

if __name__ == "__main__":
    # ### Parse HDFS log
    log_dir = input_dir + 'HDFS/'
    log_file = 'HDFS_2k.log'
    log_format = 'Date Time Pid Level Component: Content' # HDFS log format
    hashtag = ['Level', 'Component'] # Hashtags to slice log to chunks
    parser = logparser.Parser(log_format, indir=log_dir, outdir=output_dir, n_workers=num_workers, hashtag=hashtag)
    parser(log_file)
    # logparser.evaluate(log_dir + log_file + '_structured.csv', output_dir + log_file + '_structured.csv')

    # ### Parse Hadoop log
    # log_dir = input_dir + 'Hadoop/'
    # log_file = 'Hadoop_2k.log'
    # log_format = 'Date Time Level \[Process\] Component: Content' # Hadoop log format
    # hashtag = ['Level', 'Component'] # Hashtags to slice log to chunks
    # parser = logparser.Parser(log_format, indir=log_dir, outdir=output_dir, n_workers=num_workers, hashtag=hashtag)
    # parser(log_file)
    # logparser.evaluate(log_dir + log_file + '_structured.csv', output_dir + log_file + '_structured.csv')
 
    # ## Parse Spark log
    # log_dir = input_dir + 'Spark/'
    # log_file = 'Spark_2k.log'
    # log_format = 'Date Time Level Component: Content' # Spark log format
    # hashtag = ['Level', 'Component'] # Hashtags to slice log to chunks
    # parser = logparser.Parser(log_format, indir=log_dir, outdir=output_dir, n_workers=num_workers, hashtag=hashtag)
    # parser(log_file)
    # logparser.evaluate(log_dir + log_file + '_structured.csv', output_dir + log_file + '_structured.csv')

    # ## Parse Zookeeper log
    # log_dir = input_dir + 'Zookeeper/'
    # log_file = 'Zookeeper_2k.log'
    # log_format = 'Date Time - Level  \[Node:Component@LineId\] - Content' # Zookeeper log format
    # hashtag = ['Level', 'LineId'] # Hashtags to slice log to chunks
    # parser = logparser.Parser(log_format, indir=log_dir, outdir=output_dir, n_workers=num_workers, hashtag=hashtag)
    # parser(log_file)
    # logparser.evaluate(log_dir + log_file + '_structured.csv', output_dir + log_file + '_structured.csv')

    # ## Parse BGL log
    # log_dir = input_dir + 'BGL/'
    # log_file = 'BGL_2k.log'
    # log_format = 'Label Timestamp Date Node Time NodeRepeat Type Component Level Content' # BGL log format
    # hashtag = ['Level', 'Component'] # Hashtags to slice log to chunks
    # parser = logparser.Parser(log_format, indir=log_dir, outdir=output_dir, n_workers=num_workers, hashtag=hashtag)
    # parser(log_file)
    # logparser.evaluate(log_dir + log_file + '_structured.csv', output_dir + log_file + '_structured.csv')    
    
    # ## Parse HPC log
    # log_dir = input_dir + 'HPC/'
    # log_file = 'HPC_2k.log'
    # log_format = 'LogId Node Component State Time Flag Content' # HPC log format
    # hashtag = ['State', 'Component'] # Hashtags to slice log to chunks
    # parser = logparser.Parser(log_format, indir=log_dir, outdir=output_dir, n_workers=num_workers, hashtag=hashtag)
    # parser(log_file)
    # logparser.evaluate(log_dir + log_file + '_structured.csv', output_dir + log_file + '_structured.csv')

    # ## Parse Thunderbird log
    # log_dir = input_dir + 'Thunderbird/'
    # log_file = 'Thunderbird_2k.log'
    # log_format = 'Label Timestamp Date User Month Day Time Location Component(\[PID\])?: Content' # Thunderbird log format
    # hashtag = ['Component'] # Hashtags to slice log to chunks
    # parser = logparser.Parser(log_format, indir=log_dir, outdir=output_dir, n_workers=num_workers, hashtag=hashtag)
    # parser(log_file)
    # logparser.evaluate(log_dir + log_file + '_structured.csv', output_dir + log_file + '_structured.csv')
    
    # ### Parse Linux log
    # log_dir = input_dir + 'Linux/'
    # log_file = 'Linux_2k.log'
    # log_format = 'Month Date Time Level Component(\[PID\])?: Content' # Linux log format
    # hashtag = ['Level', 'Component'] # Hashtags to slice log to chunks
    # parser = logparser.Parser(log_format, indir=log_dir, outdir=output_dir, n_workers=num_workers, hashtag=hashtag)
    # parser(log_file)
    # logparser.evaluate(log_dir + log_file + '_structured.csv', output_dir + log_file + '_structured.csv') 

    # ## Parse Windows log
    # log_dir = input_dir + 'Windows/'
    # log_file = 'Windows_2k.log'
    # log_format = 'Date Time, Level                  Component    Content' # Windows log format
    # hashtag = ['Level', 'Component'] # Hashtags to slice log to chunks
    # parser = logparser.Parser(log_format, indir=log_dir, outdir=output_dir, n_workers=num_workers, hashtag=hashtag)
    # parser(log_file)
    # logparser.evaluate(log_dir + log_file + '_structured.csv', output_dir + log_file + '_structured.csv')

    # ## Parse Mac log
    # log_dir = input_dir + 'Mac/'
    # log_file = 'Mac_2k.log'
    # log_format = 'Month  Date Time User Component\[PID\]( \(Address\))?: Content' # Mac log format
    # hashtag = ['Component'] # Hashtags to slice log to chunks
    # parser = logparser.Parser(log_format, indir=log_dir, outdir=output_dir, n_workers=num_workers, hashtag=hashtag)
    # parser(log_file)
    # logparser.evaluate(log_dir + log_file + '_structured.csv', output_dir + log_file + '_structured.csv')
    

    # ## Parse Andriod log


    # ## Parse Apache log
    # log_dir = input_dir + 'Apache/'
    # log_file = 'Apache_2k.log'
    # log_format = '\[Time\] \[Level\] Content' # Apache log format
    # hashtag = ['Level'] # Hashtags to slice log to chunks
    # parser = logparser.Parser(log_format, indir=log_dir, outdir=output_dir, n_workers=num_workers, hashtag=hashtag)
    # parser(log_file)
    # logparser.evaluate(log_dir + log_file + '_structured.csv', output_dir + log_file + '_structured.csv')    

    # ## Parse Proxifier log
    # log_dir = input_dir + 'Proxifier/'
    # log_file = 'Proxifier_2k.log'
    # log_format = '\[Time\] Program - Content' # Proxifier log format
    # hashtag = ['Program'] # Hashtags to slice log to chunks
    # parser = logparser.Parser(log_format, indir=log_dir, outdir=output_dir, n_workers=num_workers, hashtag=hashtag)
    # parser(log_file)
    # logparser.evaluate(log_dir + log_file + '_structured.csv', output_dir + log_file + '_structured.csv')

