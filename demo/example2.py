#In this demo, the rawlog.log file is the HDFS data set logs.
#If you want to test on other data sets, please modify the parameters in this file or in the parser source file

from LogSig import *

RawLogPath = './'
RawLogFile = 'rawlog.log'
OutputPath = './results/'
para=Para(path=RawLogPath, logname=RawLogFile, savePath=OutputPath) #You can set parameters here

myparser=LogSig(para)
time=myparser.mainProcess()

print ('The running time of LogSig is', time)
