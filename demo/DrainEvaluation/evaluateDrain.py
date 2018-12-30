from Drainjournal import *
from pprint import pprint
from RI_precision import *

delimiters = '\s+'

dataPath = './data/HDFS/'
removeCol = [0,1,2,3,4]
rex = [('blk_(|-)[0-9]+', 'blkID'), ('(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)', 'IPAddandPortID')]
mt = 1
delimiters = '\s+'


logName = dataPath + 'rawlog.log'
myPara = Para(logName=logName, removeCol=removeCol, rex=rex, delimiters=delimiters, mt=mt)

myParser = Drain(myPara)
runningTime = myParser.mainProcess()


#Evaluate code
result = zeros((1,9))
evaPara = prePara(groundTruthDataPath=dataPath, geneDataPath='./results/')
TP,FP,TN,FN,p,r,f,RI=process(evaPara)
result[0,:]=TP,FP,TN,FN,p,r,f,RI,runningTime
	
pprint(result)
