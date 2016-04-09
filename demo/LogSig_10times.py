#!/usr/bin/env python
from pprint import pprint
from RI_precision import *
from LogSig import *
result=zeros((10,9))

LogSigDataPath=['../Sca/Sca_BGL400/','../Sca/Sca_BGL4k/','../Sca/Sca_BGL40k/','../Sca/Sca_BGL400k/','../Sca/Sca_BGL4m/']

dataName=['Sca_BGL400','Sca_BGL4k','Sca_BGL40k','Sca_BGL400k','Sca_BGL4m']
curData=3
for i in range(0,10,1):
	print 'the ', i+1, 'th experiment starts here!'
	LogSigPara=para(LogSigDataPath[curData])
	LogSigInstance=LogSig(LogSigPara)
	time=LogSigInstance.mainProcess()
	parameters=prePara(LogSigDataPath[curData])
	TP,FP,TN,FN,p,r,f,RI=process(parameters)
	result[i,:]=TP,FP,TN,FN,p,r,f,RI,time
	pprint(result)
	savetxt('10experiment_withRE'+dataName[curData]+'.csv',result,delimiter=',')

