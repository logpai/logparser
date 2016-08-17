from LogSig import *

LogSigDataPath = 'rawlog.log'
LogSigPara=Para(logname = LogSigDataPath)

LogSigInstance=LogSig(LogSigPara)
time=LogSigInstance.mainProcess()

print ('The running time of LogSig is', time)
