from LogSig import *

RawLogPath = './'
RawLogFile = 'rawlog.log'
OutputPath = './results/'
para=Para(path=RawLogPath, logname=RawLogFile, savePath=OutputPath)

myparser=LogSig(para)
time=myparser.mainProcess()

print ('The running time of LogSig is', time)
