from numpy import *
import re
from pprint import pprint 
from glob import *
import math
#**********************PARAMETERS SETTING For LogSig**************************************************
# Parameters could be setted when this function be invoked by other scripts.
# This script is used to calculate the TP, TN, FP, FN, Precision, Recall, F_measure, RI, which utilize
# the method in http://nlp.stanford.edu/IR-book/html/htmledition/evaluation-of-clustering-1.html
#*****************************************************************************************************
#***********************************For SLCT ONLY**************************************************

class prePara:
	def __init__(self,groundTruthDataPath='../../../Sca/',dataname='Sca/',logName='rawlog.log',groundTruthTempName='templates.txt',
	groundTruthGroupNamePat='template',geneDataPath='./results_TTT/',geneTempName='logTemplates.txt',geneGroupNamePat='template',beta=1):
		self.groundTruthDataPath=groundTruthDataPath
		self.dataname=dataname
		self.logName=logName
		self.groundTruthTempName=groundTruthTempName
		self.groundTruthGroupNamePat=groundTruthGroupNamePat
		self.geneDataPath=geneDataPath
		self.geneTempName=geneTempName
		self.geneGroupNamePat=geneGroupNamePat
		self.beta=beta
		
def process(prePara):
	logNum=0
	with open(prePara.groundTruthDataPath+prePara.dataname+prePara.logName) as lines:
		for line in lines:
			logNum+=1
	print logNum
	gtLogLabel=-1*ones((logNum,1))   #index start from 0
	gtfilepath=prePara.groundTruthDataPath+prePara.dataname+prePara.groundTruthGroupNamePat
	gtfileNum=len(glob(gtfilepath+'[0-9]*.txt'))
	print 'there are altogether',gtfileNum, 'files'
	gtLogNumOfEachGroup=zeros((gtfileNum,1))
	getGtLabel(gtfilepath,gtLogLabel,gtfileNum,gtLogNumOfEachGroup)

	#process the groups that produced by algorithm
	geneFilePath=prePara.geneDataPath+prePara.dataname+prePara.geneGroupNamePat
	print(geneFilePath)
	fileNum=len(glob(geneFilePath+'[0-9]*.txt'))
	geneClusterLabel=list()  #geneClusterLabel is a list of dictionary, for each group by algorithm, 
	#it has a dictionary, with key of ID, value of label from groundtruth
	geneLogNumOfEachGroup=zeros((fileNum,1))
	print 'there are altogether',fileNum, 'files'
	for i in range(fileNum):
		filename=geneFilePath+str(i+1)+'.txt'
		#print filename
		labelDict=dict()
		count=0
		with open(filename) as lines:
			for line in lines:
				count+=1
				ID = int(line.split('\t')[0])
				label=int(gtLogLabel[ID-1])
				if label not in labelDict:
					labelDict[label]=1
				else:
					labelDict[label]+=1
			#print 'there are ',count,'logs in cluster',i+1
			geneLogNumOfEachGroup[i]=count
		geneClusterLabel.append(labelDict)

	TP_FP=0
	for i in range(fileNum):
		if geneLogNumOfEachGroup[i]>1:
			TP_FP+=nCr(geneLogNumOfEachGroup[i],2)

	TP_FN=0
	for i in range(gtfileNum):
		if gtLogNumOfEachGroup[i]>1:
			TP_FN+=nCr(gtLogNumOfEachGroup[i],2)

	TP=0
	for i in range(len(geneClusterLabel)):
		labelD=geneClusterLabel[i]
		for key,value in labelD.items():
			if value>1:
				TP+=nCr(value,2)

	TP_FP_TN_FN=nCr(logNum,2)
	FN=TP_FN-TP
	FP=TP_FP-TP
	TN=TP_FP_TN_FN-TP_FP-FN
	#print 'TP_FP,TP_FN,TP_FP_TN_FN',TP_FP,TP_FN,TP_FP_TN_FN
	print 'TP,FP,TN,FN are:',TP,FP,TN,FN
	precision=float(TP)/(TP_FP)
	recall=float(TP)/(TP_FN)
	b=prePara.beta
	F_measure=float(b*b+1)*precision*recall/(b*b*precision+recall)
	RI=float(TP+TN)/TP_FP_TN_FN
	print ('precision is %.4f'%(precision))
	print ('recall is %.4f'%(recall))
	print ('F measure is %.4f'%(F_measure))
	print ('RI is %.4f'%(RI))
	return TP,FP,TN,FN,precision,recall,F_measure,RI


def getGtLabel(filePath,gtLogLabel,fileNum,gtLogNumOfEachGroup):
	for i in range(fileNum):
		count=0
		filename=filePath+str(i+1)+'.txt'
		#print filename
		with open(filename) as lines:
			label=i+1
			for line in lines:
				count+=1
				ID = int(line.split('\t')[0])
				gtLogLabel[ID-1]=label
		gtLogNumOfEachGroup[i]=count

def nCr(n,r):
	result = 1
	denominator = r
	numerator = n
	for i in range(r):
		result *= float(numerator)/denominator
		denominator -= 1
		numerator -= 1
	return result

# preParameters=prePara()
# process(preParameters)