from numpy import *
import os
from pprint import pprint
import time
import multiprocessing

class tempPara:
	def __init__(self,path='../../../Sca/SLCT_Processed/',dataname='Sca/',logname='new_rawlog.log',savePath='./results_TTT/',
		templateName='templates.txt',geneGroupNamePat='template',outlierName='outliers.log'):
		self.path=path
		self.dataname=dataname
		self.logname=logname
		self.savePath=savePath
		self.templateName=templateName
		self.geneGroupNamePat=geneGroupNamePat
		self.outlierName=outlierName

def tempProcess(tempPara):
	t1=time.time()
	print('templates preprocessing...')
	if not os.path.exists(tempPara.savePath+tempPara.dataname):
		os.makedirs(tempPara.savePath+tempPara.dataname)
	else:
		deleteAllFiles(tempPara.savePath+tempPara.dataname)

	#read the preprocessed logs
	logs=[]
	with open(tempPara.path+tempPara.dataname+tempPara.logname) as lines:
		for line in lines:
			logs.append(line)
	logNum=len(logs)

	#read the templates
	templates=[]
	with open('./'+tempPara.templateName) as tl:
		for line in tl:
			templates.append(line)

	tempNum=len(templates)
	#initialize the groups for outlier and templates
	groups=[]
	for i in range(tempNum+1):
		newgroup=[]
		groups.append(newgroup)
	#read the outlier and save its id
	outliers=[]
	removeId=[]
	with open('./'+tempPara.outlierName) as ol:
		for line in ol:
			outliers.append(line)
			Id=int(line.split('\t')[0])
			removeId.append(Id)
	print(time.time()-t1)

	logLabel=matchTempLog(templates,logs,removeId)
	#print logLabel
	print(time.time()-t1)
	for i in range(len(logLabel)):
		label=int(logLabel[i])
		groups[label+1].append(i+1)
	#label -1 means outliers 
	print('start saving log files')
	i=0
	for numLogOfEachGroup in groups:
		with open(tempPara.savePath+tempPara.dataname+tempPara.geneGroupNamePat+str(i+1)+'.txt', 'w') as f:
			for ids in numLogOfEachGroup:
				f.write(str(ids)+'\n')
		i+=1
	print(time.time()-t1)

#match the templates with Logs
def matchTempLog(templates, logs,removeId):
	tempNum=len(templates)
	logNum=len(logs)
	logLabel=-1*ones((logNum,1))
	for i in range(logNum):
		maxValue=-1;maxIndex=-1
		if i+1 in removeId:
			continue
		for j in range(tempNum):
			lcs=LCS(logs[i],templates[j])
			if lcs>=maxValue:
				maxValue=lcs
				maxIndex=j
		logLabel[i]=maxIndex
	return logLabel

#calculate the LCS
def LCS(seq1, seq2):
    lengths = [[0 for j in range(len(seq2)+1)] for i in range(len(seq1)+1)]
    # row 0 and column 0 are initialized to 0 already
    for i in range(len(seq1)):
        for j in range(len(seq2)):
            if seq1[i] == seq2[j]:
                lengths[i+1][j+1] = lengths[i][j] + 1
            else:
                lengths[i+1][j+1] = max(lengths[i+1][j], lengths[i][j+1])
    return lengths[-1][-1]

def deleteAllFiles(dirPath):
	fileList = os.listdir(dirPath)
	for fileName in fileList:
 		os.remove(dirPath+"/"+fileName)

# tempParameter=tempPara()
# tempProcess(tempParameter)