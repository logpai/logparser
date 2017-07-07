#!/usr/bin/env python
from pprint import pprint
from RI_precision import *
from LogSig import *
import gc
import numpy as np


dataset = 3
dataPath = './data/'

if dataset == 1:
	dataName = 'BGL'
	groupNum = 100
	removeCol = [0,1,2,3,4,5,6,7,8,9]
	regL = ['core\.[0-9]*']
	# regL = []
elif dataset == 2:
	dataName = 'HPC'
	groupNum = 51
	removeCol = [0,1]
	regL = ['([0-9]+\.){3}[0-9]']
	# regL = []
elif dataset == 3:
	dataName = 'HDFS'
	groupNum = 14
	removeCol = [0,1,2,3,4,5]
	regL = ['blk_(|-)[0-9]+','(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)']
	# regL = [] 
elif dataset == 4:
	dataName = 'Zookeeper'
	groupNum = 46
	removeCol = [0,1,2,3,4,5,6]
	regL = ['(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)']
	# regL = []
elif dataset == 5:
	dataName = 'Proxifier'
	groupNum = 6
	removeCol = [0,1,2,4,5]
	regL = [] 


result = np.zeros((1,9))

for i in range(0,1,1):
	print ('the ', i+1, 'th experiment starts here!')
	parserPara = Para(path=dataPath+dataName+'/', groupNum=groupNum, removeCol=removeCol, rex=regL, savePath='./results/')
	myParser = LogSig(parserPara)
	runningTime = myParser.mainProcess()

	parameters=prePara(groundTruthDataPath=dataPath+dataName+'/', geneDataPath='./results/')

	TP,FP,TN,FN,p,r,f,RI=process(parameters)
	result[i,:]=TP,FP,TN,FN,p,r,f,RI,runningTime
	
	pprint(result)

	gc.collect()

