#!/usr/bin/env python

#In this demo, we assume the POP.py is under the same directory as this file.

import os
import subprocess
import commands
from pprint import pprint

hadoopOutputDir = '/pjhe/test/'
hadoopInputDir = '/pjhe/logs/'


#upload you raw log file from local file system to HDFS
os.system('hadoop fs -put rawlog.log ' + hadoopInputDir)

#remove the files in the output directory (initialization)
os.system('hadoop fs -rmr ' + hadoopOutputDir)

#submit the POP application to Spark
os.system('spark-submit --master=yarn POP.py')















