import os, sys, time
sys.path.append('../../')
sys.path.append('../..//')
sys.path.append('../')
from logparser import slct
from logparser.slct import *
import logging 
from commons import util
from commons import dataloader
import commands
from templatesPreprocess import *

def SLCT(para,dataPath,data,curData):
	util.config(para)
	startTime = time.time() # start timing
	# load the dataset
	loglines = dataloader.load(para)
	# log template extraction
	slct.extract(loglines, para)
	timeInterval=time.time() - startTime
	print('execution time is: %f (precision calculation,data preprocessing and templates splitting not counted)'%(timeInterval))
	tempParameter=tempPara(dataname=data[curData]+'/',savePath=dataPath)
	tempProcess(tempParameter)
	return timeInterval