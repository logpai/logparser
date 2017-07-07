import numpy
import random
import math
import time
import operator
import re
import os
import gc 
#**********************PARAMETERS SETTING**************************************************
# Replace the parameters of def __init__ with the following ones according to the dataset.
# Please be noted that part of the codes in function termpairGene need to be altered according to the dataset
#******************************************************************************************
# =====For BGL=====
# (self,path='../Data/2kBGL/',logname='rawlog.log',removable=True,removeCol=[0,1,2,3,4,5,6,7,8,9],regular=True,
# rex=['core\.[0-9]*'],savePath='./results_2kBGL/',saveFileName='template',groupNum=100):# line 66,change the regular expression replacement code
# =====For Proxifier=====
# (self,path='../Data/2kProxifier/',logname='rawlog.log',removable=True,removeCol=[0,1,2,4,5],regular=True,
# rex=[''],savePath='./results_2kProxifier/',saveFileName='template',groupNum=6):
# =====For Zookeeper=====
# (self,path='../Data/2kZookeeper/',logname='rawlog.log',removable=True,removeCol=[0,1,2,3,4,5,6],regular=True,
# rex=['(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)'],savePath='./results_2kZookeeper/',saveFileName='template',groupNum=46):
# =====For HDFS=====
# (self,path='../Data/2kHDFS/',logname='rawlog.log',removable=True,removeCol=[0,1,2,3,4,5],regular=True,
# rex=['blk_(|-)[0-9]+','(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)'],savePath='./results_2kHDFS/',saveFileName='template',groupNum=14):
# =====For HPC=====
# (self,path='../Data/2kHPC/',logname='rawlog.log',removable=True,removeCol=[0,1],regular=True,
# rex=['([0-9]+\.){3}[0-9]'],savePath='./results_2kHPC/',saveFileName='template',groupNum=51):# line 67,change the regular expression replacement code
#******************************************************************************************

class Para:
	def __init__(self,path='../Data/2kBGL/',logname='rawlog.log',removable=True,removeCol=[0,1,2,3,4,5],regular=True,
	rex=['blk_(|-)[0-9]+','(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)'],savePath='./results_2kBGL/',saveFileName='template',groupNum=14):# line 66,change the regular expression replacement code
		self.path=path
		self.logname=logname
		self.removable=removable
		self.removeCol=removeCol
		self.regular=regular
		self.rex=rex
		self.savePath=savePath
		self.saveFileName=saveFileName
		self.groupNum=groupNum   #partition into k groups

class LogSig:
	def __init__(self,para,wordLL=[],loglineNum=0,termpairLLT=[],logNumPerGroup=[],groupIndex=dict(),termPairLogNumLD=[],logIndexPerGroup=[]):
		self.para=para
		self.wordLL=[]
		self.loglineNum=0
		self.termpairLLT=[]
		self.logNumPerGroup=[]
		self.groupIndex=dict()   #each line corresponding to which group
		self.termPairLogNumLD=[]
		self.logIndexPerGroup=[]

	#Load datasets and use regular expression to split it and remove some columns
	def termpairGene(self):
		print('Loading Log File...')
		print(self.para.path+self.para.logname)
		print(self.para.regular)
		print(self.para.groupNum)
		with open(self.para.path+self.para.logname) as lines:
			for line in lines:
				if self.para.regular:
					for currentRex in self.para.rex:
						line=re.sub(currentRex,'',line)
						# line=re.sub(currentRex,'core.',line) # For BGL data only
					#line=re.sub('node-[0-9]+','node-',line) #For HPC only 
				wordSeq=line.strip().split()
				if self.para.removable:
					wordSeq=[word for i, word in enumerate(wordSeq) if i not in self.para.removeCol]
				self.wordLL.append(tuple(wordSeq))
	
	#initialize different variables
	def initialization(self):
		print('Generating term pairs...')
		i = 0
		for wordL in self.wordLL:
			wordLT=[]	
			for j in range(len(wordL)):
				for k in range(j+1,len(wordL),1):
					termpair=(wordL[j],wordL[k])
					wordLT.append(termpair)
			self.termpairLLT.append(wordLT)
			i += 1

		print('initializing...')
		#termPairLogNumLD, used to account the occurance of each termpair of each group 
		for i in range(self.para.groupNum):
			newDict=dict()
			self.termPairLogNumLD.append(newDict)
			#initialize the item value to zero
			self.logNumPerGroup.append(0)

		#divide logs into initial groupNum groups randomly, the group number of each log is stored in the groupIndex
		self.loglineNum=len(self.wordLL)
		for i in range(self.loglineNum):
			ran=random.randint(0,self.para.groupNum-1) # group number from 0 to k-1
			self.groupIndex[i]=ran
			self.logNumPerGroup[ran]+=1   #count the number of loglines per group
 
		#count the frequency of each termpairs per group 
		i = 0
		for termpairLT in self.termpairLLT:
			j = 0
			for key in termpairLT:
				currGroupIndex=self.groupIndex[i]
				if key not in self.termPairLogNumLD[currGroupIndex]:
					self.termPairLogNumLD[currGroupIndex][key]=1
				else:
					self.termPairLogNumLD[currGroupIndex][key]+=1
				j += 1
			i += 1
		print('=======initial group division(Random Select)=====================')
		print('Log Number of each group is: ',self.logNumPerGroup)

	#use local search, for each log, find the group that it should be moved to.
	#in this process, termpairs occurange should also make some changes and logNumber of corresponding should be changed 
	def LogMessParti(self):
		changed=True
		while changed:
			changed=False
			i = 0
			for termpairLT in self.termpairLLT:
				curGroup=self.groupIndex[i]
				alterGroup=potenFunc(curGroup,self.termPairLogNumLD,self.logNumPerGroup,i,termpairLT,self.para.groupNum)
				if curGroup != alterGroup:
					changed=True
					self.groupIndex[i]=alterGroup
					#update the dictionary of each group					
					for key in termpairLT:
						#minus 1 from the current group count on this key 
						self.termPairLogNumLD[curGroup][key]-=1
						if self.termPairLogNumLD[curGroup][key]==0:
							del self.termPairLogNumLD[curGroup][key]
						#add 1 to the alter group
						if key not in self.termPairLogNumLD[alterGroup]:
							self.termPairLogNumLD[alterGroup][key]=1
						else:
							self.termPairLogNumLD[alterGroup][key]+=1						
					self.logNumPerGroup[curGroup]-=1
					self.logNumPerGroup[alterGroup]+=1
				i += 1
		print('===================================================')
		print(self.logNumPerGroup)
		print('===================================================')

	#calculate the occurancy of each word of each group, and for each group, save the words that
	#happen more than half all log number to be candidateTerms(list of dict, words:frequency),	
	def signatConstr(self):
		#create the folder to save the resulted templates
		if not os.path.exists(self.para.savePath):
			os.makedirs(self.para.savePath)
		else:
			deleteAllFiles(self.para.savePath)

		wordFreqPerGroup=[]
		candidateTerm=[]
		candidateSeq=[]
		signature=[]

		#save the all the log indexs of each group: logIndexPerGroup
		for t in range(self.para.groupNum):
			dic=dict()
			newlogIndex=[]
			newCandidate=dict()
			wordFreqPerGroup.append(dic)
			self.logIndexPerGroup.append(newlogIndex)
			candidateSeq.append(newCandidate)

		#count the occurence of each word of each log per group
		#and save into the wordFreqPerGroup, which is a list of dictionary,
		#where each dictionary represents a group, key is the word, value is the occurence
		lineNo = 0
		for wordL in self.wordLL:
			groupIndex=self.groupIndex[lineNo]
			self.logIndexPerGroup[groupIndex].append(lineNo)
			for key in wordL:
				if key not in wordFreqPerGroup[groupIndex]:
					wordFreqPerGroup[groupIndex][key]=1
				else:
					wordFreqPerGroup[groupIndex][key]+=1
			lineNo += 1

		#calculate the halfLogNum and select those words whose occurence is larger than halfLogNum 
		#as constant part and save into candidateTerm 
		for i in range(self.para.groupNum):
			halfLogNum=math.ceil(self.logNumPerGroup[i]/2.0)
			dic=dict((k,v) for k, v in wordFreqPerGroup[i].items() if v >= halfLogNum)
			candidateTerm.append(dic)

		#scan each logline's each word that also is a part of candidateTerm, put these words together 
		#as a new candidate sequence, thus, each raw log will have a corresponding candidate sequence
		#and count the occurence of these candidate sequence of each group and select the most frequent
		#candidate sequence as the signature, i.e. the templates
		lineNo = 0
		for wordL in self.wordLL:
			curGroup=self.groupIndex[lineNo]
			newCandiSeq=[]
			
			for key in wordL:
				if key in candidateTerm[curGroup]:
					newCandiSeq.append(key)
				
			keySeq=tuple(newCandiSeq)
			if keySeq not in candidateSeq[curGroup]:
				candidateSeq[curGroup][keySeq]=1
			else:
				candidateSeq[curGroup][keySeq]+=1	
			lineNo += 1

		for i in range(self.para.groupNum):
			sig=max(candidateSeq[i].items(), key=operator.itemgetter(1))[0]
			#sig=max(candidateSeq[i].iteritems(), key=operator.itemgetter(1))[0]
			signature.append(sig)
		print(signature) 

		#save the templates
		with open(self.para.savePath+'logTemplates.txt','w') as fi:
			for j in range(len(signature)):
				#pjhe
				fi.write(' '.join(signature[j]) + '\n')

	#save the grouped loglines into different templates.txt 
	def templatetxt(self):
		for i in range(len(self.logIndexPerGroup)):
			numLogOfEachGroup=self.logIndexPerGroup[i]
			with open(self.para.savePath+self.para.saveFileName+str(i+1)+'.txt', 'w') as f:
				for log_ID in numLogOfEachGroup:
					f.write(str(log_ID+1) + '\n')
					
	def mainProcess(self):
		self.termpairGene()
		t1=time.time()
		self.initialization()
		self.LogMessParti()
		self.signatConstr()
		timeInterval=time.time()-t1
		self.templatetxt()
		print('this process takes',timeInterval)
		print('*********************************************')
		gc.collect()
		return timeInterval

	#calculate the potential value that would be used in the local search 
def potenFunc(curGroupIndex,termPairLogNumLD,logNumPerGroup,lineNum,termpairLT,k):
	maxDeltaD=0
	maxJ=curGroupIndex
	for i in range(k):
		returnedDeltaD=getDeltaD(logNumPerGroup,termPairLogNumLD,curGroupIndex,i,lineNum,termpairLT)
		if returnedDeltaD>maxDeltaD:
			maxDeltaD=returnedDeltaD
			maxJ=i
	return maxJ

	#part of the potential function
def getDeltaD(logNumPerGroup,termPairLogNumLD,groupI,groupJ,lineNum,termpairLT):
	deltaD=0
	Ci=logNumPerGroup[groupI]
	Cj=logNumPerGroup[groupJ]
	for r in termpairLT:
		if r in termPairLogNumLD[groupJ]:
			deltaD+=(pow(((termPairLogNumLD[groupJ][r]+1)/(Cj+1.0)),2)-pow((termPairLogNumLD[groupI][r]/(Ci+0.0)),2))
		else:
			deltaD+=(pow((1/(Cj+1.0)),2)-pow((termPairLogNumLD[groupI][r]/(Ci+0.0)),2))
	deltaD=deltaD*3
	return deltaD
	
	#delete the files under this dirPath
def deleteAllFiles(dirPath):
	fileList = os.listdir(dirPath)
	for fileName in fileList:
 		os.remove(dirPath+"/"+fileName)
