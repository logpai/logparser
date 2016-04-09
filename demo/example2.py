from LogSig import *

LogSigDataPath = 'rawlog.log'
LogSigPara=para(logname = LogSigDataPath)

LogSigInstance=LogSig(LogSigPara)
time=LogSigInstance.mainProcess()

print ('The running time of LogSig is', time)