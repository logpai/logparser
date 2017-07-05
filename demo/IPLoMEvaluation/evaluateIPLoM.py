#!/usr/bin/env python
from pprint import pprint
from RI_precision import *
from IPLoM import *
import gc


dataset = 3
dataPath = './data/'

if dataset == 1:
	dataName = 'BGL'
	ct = 0.4
	lowerBound = 0.25
	removeCol = [0,1,2,3,4,5,6,7,8]
	regL = ['core\.[0-9]*']
elif dataset == 2:
	dataName = 'HPC'
	ct = 0.175
	lowerBound = 0.25
	removeCol = [0]
	regL = ['([0-9]+\.){3}[0-9]']
elif dataset == 3:
	dataName = 'HDFS'
	ct = 0.35
	lowerBound = 0.25
	removeCol = [0,1,2,3,4]
	regL = ['blk_(|-)[0-9]+','(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)'] 
elif dataset == 4:
	dataName = 'Zookeeper'
	ct = 0.4
	lowerBound = 0.7
	removeCol = [0,1,2,3,4,5]
	regL = ['(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)']
elif dataset == 5:
	dataName = 'Proxifier'
	ct = 0.6
	lowerBound = 0.25
	removeCol = [0,1,3,4] 
	regL = [] 


result = np.zeros((1,9))

for i in range(0,1,1):
	print ('the ', i+1, 'th experiment starts here!')
	parserPara = Para(path=dataPath+dataName+'/', CT=ct, lowerBound=lowerBound, removeCol=removeCol, rex=regL)
	myParser = IPLoM(parserPara)
	runningTime = myParser.mainProcess()

	parameters=prePara(groundTruthDataPath=dataPath+dataName+'/', geneDataPath='./results/')

	TP,FP,TN,FN,p,r,f,RI=process(parameters)
	result[i,:]=TP,FP,TN,FN,p,r,f,RI,runningTime
	
	pprint(result)

	gc.collect()

