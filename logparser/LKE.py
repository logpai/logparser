from numpy import *
import math
import pickle
import time
from pprint import pprint
import re
import os
import sys
#**********************PARAMETERS SETTING**************************************************
# Replace the parameters of def __init__ with the following ones according to the dataset.
# Please be noted that part of the codes in function termpairGene need to be altered according to the dataset
#******************************************************************************************
# =====For BGL=====
# (self,path='../Sca/',dataName='Sca_BGL600',logname='rawlog.log',removable=True,removeCol=[0,1,2,3,4,5,6,7,8,9],threshold2=5,regular=True,
# rex=['core\.[0-9]*'],savePath='./results/',saveFileName='template'):# line 67,change the regular expression replacement code
# =====For Proxifier=====
# (self,path='../Sca/',dataName='Sca_Proxifier600',logname='rawlog.log',removable=True,removeCol=[0,1,2,4,5],regular=True,threshold2=2,
# rex=[''],savePath='./results/',saveFileName='template'):
# =====For Zookeeper=====
# (self,path='../Sca/',dataName='Sca_Zookeeper600',logname='rawlog.log',removable=True,removeCol=[0,1,2,3,4,5,6],threshold2=2,regular=True,
# rex=['(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)'],savePath='./results/',saveFileName='template'):
# =====For SOSP=====
# (self,path='../Sca/',dataName='Sca_SOSP600',logname='rawlog.log',removable=True,removeCol=[0,1,2,3,4,5],threshold2=3,regular=True,
# rex=['blk_(|-)[0-9]+','(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)'],savePath='./results/',saveFileName='template'):
# =====For HPC=====
# (self,path='../Sca/',dataName='Sca_HPC600',logname='rawlog.log',removable=True,removeCol=[0,1],threshold2=4,regular=True,
# rex=['([0-9]+\.){3}[0-9]'],savePath='./results/',saveFileName='template'):# line 67,change the regular expression replacement code
#******************************************************************************************

class para:
	def __init__(self,path='../Sca/',dataName='Sca_BGL600',logname='rawlog.log',removable=True,removeCol=[0,1,2,3,4,5,6,7,8,9],threshold2=5,regular=True,
	rex=['core\.[0-9]*'],savePath='./results/',saveFileName='template'):# line 55,change the regular expression replacement code
		self.path=path
		self.logname=logname
		self.dataName=dataName
		self.removable=removable
		self.removeCol=removeCol
		self.threshold2=threshold2
		self.rex=rex
		self.savePath=savePath
		self.saveFileName=saveFileName
		self.regular=regular

class LKE:
	def __init__(self,para,wordLL=[],wordLen=[],groups=[],loglineNumPerGroup=[],wordLenPerGroup=[],
		wordOccuOfPosiLLD=[],loglinesOfGroups=[],flatLogLineGroups=[],newGroups=[]):
		self.para=para
		self.wordLL=[]
		self.wordLen=[]
		self.groups=[]  #the list of list of words list, each group->each log lines->each words
		self.loglineNumPerGroup=[] #how many lines in each groups
		self.wordLenPerGroup=[] #maximum word positions in one group
		self.wordOccuOfPosiLLD=[]  #each word in each position in each group occurance/frequency
		self.loglinesOfGroups=[]
		self.flatLogLineGroups=[]
		self.newGroups=[]

	def paraErasing(self):
		print('Loading log files and split into words lists...')
		print('threshold2 is:',self.para.threshold2)
		print(self.para.path+self.para.dataName+'/'+self.para.logname)
		with open(self.para.path+self.para.dataName+'/'+self.para.logname) as lines:
			for line in lines:
				if self.para.regular:
					for currentRex in self.para.rex:
						line=re.sub(currentRex,'',line)
						#line=re.sub(currentRex,'core.',line) # For BGL data only
					#line=re.sub('node-[0-9]+','node-',line) #For HPC only 
				wordSeq=line.strip().split()
				if self.para.removable:
					wordSeq=[word for i, word in enumerate(wordSeq) if i not in self.para.removeCol]
				self.wordLen.append(len(wordSeq))
				self.wordLL.append(tuple(wordSeq))
		#delete all the files insidd this directory
		if not os.path.exists(self.para.savePath+self.para.dataName+'/'):
			os.makedirs(self.para.savePath+self.para.dataName+'/')
		else:
			deleteAllFiles(self.para.savePath+self.para.dataName+'/')

	def clustering(self,t1):
		sys.setrecursionlimit(100000000) #set the recursion limits number
		v=math.floor(sum(self.wordLen)/len(self.wordLen))
		print('the parameter v is: %d' %(v))
		logNum=len(self.wordLen)
		print('there are about %d loglines'%(logNum))
		loadDataTime=0
		calDataTime=0
		#In order to save time, load distArraydata, if exist, do not calculate the edit distance again:
		if os.path.exists(self.para.savePath+self.para.dataName+'editDistance.csv'):
			print('Loading data instead of calculating..')
			distMat=genfromtxt(self.para.savePath+self.para.dataName+'editDistance.csv',delimiter=',')
			distList=genfromtxt(self.para.savePath+self.para.dataName+'distArray.csv',delimiter=',')
			loadDataTime=time.time()-t1
		else:
			print('calculating distance....')
			path=self.para.savePath+self.para.dataName
			distMat,distList=calDistance(self.wordLL,v,path)
			calDataTime=time.time()-t1
		distArray=array(distList)
		threshold1=GetkMeansThreshold(distArray)
		print('the threshold1 is: %s'%(threshold1))
		
		#connect two loglines with distance < threshold, logDict is a dictionary
		#where the key is line num while 
		logDict={}
		for i in range(logNum):
			logLineSet=set()
			for j in range(i+1,logNum):
				if distMat[i,j]<threshold1:
					logLineSet.add(j)
			logDict[i]=logLineSet
		
		#use DFS to get the initial group. 
		flag=zeros((logNum,1)) # used to label whether line has been visited, 0 represents not visited
		for key in logDict:
			if flag[key]==1:
				continue
			groupLoglist=[]
			groupLoglist.append(key) # add the key of dict into the list firstly, and then add others
			flag[key]=1   #line is visited
			dfsTraversal(key,logDict,flag,groupLoglist)
			self.loglinesOfGroups.append(groupLoglist)
			self.loglineNumPerGroup.append(len(groupLoglist))

		print('================get the initial groups splitting=============')
		wordLenArray=array(self.wordLen)
		for row in self.loglinesOfGroups:
			eachLineLogList=[]
			self.wordLenPerGroup.append(max(wordLenArray[row]))
			for colu in row:
				eachLineLogList.append(self.wordLL[colu])
			self.groups.append(eachLineLogList)
		print('========================================================================')
		print('there are %s groups'%(len(self.wordLenPerGroup)))
		return loadDataTime,calDataTime
	#split the current group recursively.
	def splitting(self):
		print('splitting into different groups...')
		print ('the threshold2 is %d'%(self.para.threshold2))
		groupNum=len(self.groups) #how many groups initially
		for i in range(groupNum):
			splitEachGroup(self.groups[i],self.para.threshold2,self.loglinesOfGroups[i])	

		# to flat the list of list of list to list of many lists, that is only one layer lists nested
		mergeLists(self.groups,self.newGroups)
		mergeLists(self.loglinesOfGroups,self.flatLogLineGroups)
		print('Merge the lists together...')
		print('there are %s different groups'%(len(self.flatLogLineGroups)))

	#extract the templates according to the logs in each group
	def extracting(self):
		templates=[]
		for i in range(len(self.flatLogLineGroups)):
			groupLen=len(self.flatLogLineGroups[i])
			eachGroup=self.newGroups[i]
			if groupLen==1:
				templates.append(eachGroup[0])
			else:
				commonPart=LCS(eachGroup[0],eachGroup[1])
				for k in range(2,groupLen):
					if not comExit(commonPart,eachGroup[k]):
						commonPart=LCS(commonPart,eachGroup[k])
						if len(commonPart)==0:
							print('there is no common part in this group')
							commonPart=[]
							break
				if len(commonPart)!=0:
					templates.append(commonPart)
		with open(self.para.savePath+self.para.dataName+'/'+'logTemplates.txt','w') as fi:
			for j in range(len(templates)):
				fi.write(' '.join(templates[j]) + '\n')		

	#save to logs in groups into different template txt
	def templatetxt(self):
		for i in range(len(self.flatLogLineGroups)):
			groupLen=len(self.flatLogLineGroups[i])
			numLogOfEachGroup=self.flatLogLineGroups[i]
			with open(self.para.savePath+self.para.dataName+'/'+self.para.saveFileName+str(i+1)+'.txt', 'w') as f:
				for j in range(groupLen):
					f.write(str(numLogOfEachGroup[j]+1)+'\n')

	def mainProcess(self):
		self.paraErasing()
		t1=time.time()
		loadDataTime,calDataTime=self.clustering(t1)
		self.splitting()
		self.extracting()
		timeInterval=time.time()-t1
		self.templatetxt()
		print('this process takes',timeInterval)
		print('*********************************************')
		return loadDataTime,calDataTime,timeInterval

#merge the list of lists(many layer) into one list of list
def mergeLists(initGroup,flatLogLineGroups):
	for i in range(len(initGroup)):
		if not listContained(initGroup[i]):
			flatLogLineGroups.append(initGroup[i])
		else:
			mergeLists(initGroup[i],flatLogLineGroups)

#find out whether a list contained a list 
def listContained(group):
	for i in range(len(group)):
		if str(type(group[i]))=="<type 'list'>":
			return True
	return False

#for each group, According to the splittable and groupLen, decide whether to split 
#it iteratively until it cannot be splitted any more  
def splitEachGroup(eachGroup,threshold2,loglinesEachGroup):
		groupLen=len(eachGroup)
		if groupLen<=1:
			return
		returnValues=posiToSplit(eachGroup,threshold2)
		splittable=returnValues['splittable']
		if splittable=='yes':
			diffwords=returnValues['diffWordList']
			posi=returnValues['minIndex']
			conOrParaDivi=returnValues['conOrParaDivi']
			print('the different words are:',diffwords)
			#each item in the diffwords corresponds to a group
			for k in range(len(diffwords)):
				newgroups=[]
				newloglineGroup=[]
				for t in range(groupLen):  #each line in a group
					if len(conOrParaDivi[t])<posi+1:
						newgroups.append(eachGroup[t])
						newloglineGroup.append(loglinesEachGroup[t])
						break
					if conOrParaDivi[t][posi]== diffwords[k]:
						newgroups.append(eachGroup[t])
						newloglineGroup.append(loglinesEachGroup[t])

				eachGroup.append(newgroups)
				loglinesEachGroup.append(newloglineGroup)
			for t in range(groupLen):
				eachGroup.pop(0)
				loglinesEachGroup.pop(0)
			for i in range(len(diffwords)):
				splitEachGroup(eachGroup[i],threshold2,loglinesEachGroup[i])

def deleteAllFiles(dirPath):
	fileList = os.listdir(dirPath)
	for fileName in fileList:
 		os.remove(dirPath+"/"+fileName)
	
#find the position that should be splitted, that is to find minimum num of different variable parts of each position or find the entropy 
def posiToSplit(eachGroup,threshold2):
	groupLen=len(eachGroup)
	wordLabel=[]
	noCommon=False
	commonPart=LCS(eachGroup[0],eachGroup[1])
	Splittable='yes'
	returnValues={}
	for i in range(2,groupLen):
		if not comExit(commonPart,eachGroup[i]):
			commonPart=LCS(commonPart,eachGroup[i])
			if len(commonPart)==0:
				noCommon=True
				print('there is no common part in this group')
				break

	for k in range(groupLen):
		newWordLabel=[]
		for t in range(len(eachGroup[k])): 
			if eachGroup[k][t] in commonPart:
				newWordLabel.append(1) #1 represent constant
			else: 
				newWordLabel.append(0) #0 represents variable
		wordLabel.append(newWordLabel)

	conOrParaDivi=[]
	partLabel=[]
	seqLen=[]
	#connect the continuous constant words or variable words as a big part(be a sequence) 
	for i in range(groupLen):
		start=0
		newconOrParaLL=[]
		newPartLabel=[]
		j=1
		end=-1
		while j < len(eachGroup[i]):
			if wordLabel[i][j-1]!=wordLabel[i][j]:
				end=j-1
				newconOrPara=[]
				newconOrPara=newappend(start,end,eachGroup[i],newconOrPara)
				newconOrParaLL.append(newconOrPara)
				newPartLabel.append(wordLabel[i][end])
				start=j
			j+=1

		lastnewconOrPara=[]
		for j in range(end+1,len(eachGroup[i]),1):
			lastnewconOrPara.append(eachGroup[i][j])
		newconOrParaLL.append(lastnewconOrPara)
		newPartLabel.append(wordLabel[i][end+1])
		conOrParaDivi.append(newconOrParaLL)
		partLabel.append(newPartLabel)
		seqLen.append(len(newPartLabel))

	maxLen=max(seqLen)

	#convert list into tuple as list could not be the key of dict
	for i in range(groupLen):
		for j in range(len(conOrParaDivi[i])):
			conOrParaDivi[i][j]=tuple(conOrParaDivi[i][j])

	#initialize the list of dict of (part: occurance)
	partOccuLD=list()
	for t in range(maxLen):#wordLenPerGroup is the maximum number of positions in one group
		wordOccuD={}
		partOccuLD.append(wordOccuD)

	for j in range(groupLen):    #the j-th word sequence
	    for k in range(len(conOrParaDivi[j])):     # the k-th word in word sequence 
			key=conOrParaDivi[j][k]
			if key not in partOccuLD[k]:
				partOccuLD[k][key]=1
				continue
			partOccuLD[k][key]+=1
	numOfDiffParts=list()
	numOfPosi=len(partOccuLD)
	for i in range(numOfPosi):
		numOfDiffParts.append(len(partOccuLD[i]))

	minNum=inf
 	minIndex=-1
	for i in range(numOfPosi):
		if numOfDiffParts[i]==1:
			continue
		if numOfDiffParts[i]<threshold2:
			if numOfDiffParts[i]<minNum:
				minNum=numOfDiffParts[i]
	if minNum==inf:
		Splittable='no'
		returnValues['splittable']='no' #no minmum that smaller than threshold2,which means all position except are parameters, no need to split
		return returnValues
	
	indexOfMinItem=[]
	for i in range(numOfPosi):
		if numOfDiffParts[i]==minNum:
			indexOfMinItem.append(i)
	
	if len(indexOfMinItem)==1:
		minIndex=indexOfMinItem[0]            #minmum position

	#multiple position that has same minmum num of words
	minEntropy=inf
	if len(indexOfMinItem)>1:
		for j in range((len(indexOfMinItem)-1),-1,-1):
			entropy_J=entropy(partOccuLD[indexOfMinItem[j]],numOfDiffParts[indexOfMinItem[j]])
			if entropy_J<minEntropy:
				minEntropy=entropy_J
				minIndex=j

	diffWordList=list(partOccuLD[minIndex].keys())
	returnValues['splittable']='yes'
	if len(diffWordList)==1:
		returnValues['splittable']='no'	
	returnValues['minIndex']=minIndex
	returnValues['diffWordList']=diffWordList
	returnValues['conOrParaDivi']=conOrParaDivi
	return returnValues

def comExit(commonPart,seq):
	for i,itemI in enumerate(seq):
		if itemI not in commonPart:
			return False
	return True

# find the common part of two sequences
def LCS(seq1, seq2):
    lengths = [[0 for j in range(len(seq2)+1)] for i in range(len(seq1)+1)]
    # row 0 and column 0 are initialized to 0 already
    for i in range(len(seq1)):
        for j in range(len(seq2)):
            if seq1[i] == seq2[j]:
                lengths[i+1][j+1] = lengths[i][j] + 1
            else:
                lengths[i+1][j+1] = max(lengths[i+1][j], lengths[i][j+1])
    # read the substring out from the matrix
    result = []
    lenOfSeq1, lenOfSeq2 = len(seq1), len(seq2)
    while lenOfSeq1 != 0 and lenOfSeq2 != 0:
        if lengths[lenOfSeq1][lenOfSeq2] == lengths[lenOfSeq1-1][lenOfSeq2]:
            lenOfSeq1 -= 1
        elif lengths[lenOfSeq1][lenOfSeq2] == lengths[lenOfSeq1][lenOfSeq2-1]:
            lenOfSeq2 -= 1
        else:
            assert seq1[lenOfSeq1-1] == seq2[lenOfSeq2-1]
            result.insert(0,seq1[lenOfSeq1-1])
            lenOfSeq1 -= 1
            lenOfSeq2 -= 1
    return result

def newappend(start,end,wordList,newconOrPara):
	for i in range(start,end+1,1):
		newconOrPara.append(wordList[i])
	return newconOrPara

def entropy(wordsOnPosit,totalNum):
	entropy=0
	for key in wordsOnPosit:
		temp=float(wordsOnPosit[key])/totalNum
		entropy-=math.log(temp)*temp
	return entropy

def dfsTraversal(key,logDict,flag,groupLoglist):
	for nodes in logDict[key]:
		if flag[nodes]==0:	
			groupLoglist.append(nodes)
			flag[nodes]=1
			dfsTraversal(nodes,logDict,flag,groupLoglist)	

#k-means where k equals 2 to divide the edit distance into two groups
def GetkMeansThreshold(distArray):
	print('kMeans calculation...')
	distArraySize=len(distArray)
	#random choose two centroids
	minValue=min(distArray)
	centroids=zeros((2,1))
	rangeValue=float(max(distArray)-minValue)
	centroids[:]=random.rand(2,1)*rangeValue+minValue
	maxInnerDist=zeros((2,1))
	clusterChanged=True
	clusterAssment=zeros((distArraySize,1))
	while clusterChanged:
		clusterChanged=False
		for i in range(distArraySize):
			minIndex=-1
			if math.fabs(distArray[i]-centroids[0])<math.fabs(distArray[i]-centroids[1]):
				minIndex=0
			else:
				minIndex=1
			if clusterAssment[i]!=minIndex:
				clusterChanged=True
			clusterAssment[i]=minIndex
		for cent in range(2):
			indexs=where(clusterAssment==cent)[0]
			disInClust=distArray[indexs]
			maxInnerDist[cent]=min(disInClust)
			centroids[cent]=mean(disInClust,axis=0)
	return max(maxInnerDist)

#calculate the distance betweent each two logs and save into a matrix		
def calDistance(wordLL,v,path):
	print('calculate distance between every two logs...')
	logNum=len(wordLL)
	distList=[]
	distMat=zeros((logNum,logNum))
	for i in range(logNum):
		for j in range(i,logNum):
			dist=editDistOfSeq(wordLL[i],wordLL[j],v)
			distMat[i][j]=distMat[j][i]=dist
			distList.append(dist)
	distArray=array(distList)
	savetxt(path+'editDistance.csv',distMat,delimiter=',')
	savetxt(path+'distArray.csv',distArray,delimiter=',')
	return distMat,distArray

#the edit distance of two logs
def editDistOfSeq(wordList1,wordList2,v):
    m = len(wordList1)+1
    n = len(wordList2)+1
    d = []           
    t=s=0
    for i in range(m):
        d.append([t])
        t+=1/(math.exp(i-v)+1)
    del d[0][0]    
    for j in range(n):
        d[0].append(s)
        s+=1/(math.exp(j-v)+1)       
    for i in range(1,m):
        for j in range(1,n):
            if wordList1[i-1]==wordList2[j-1]:
                d[i].insert(j,d[i-1][j-1])           
            else:
            	weight=1.0/(math.exp(i-1-v)+1)
                minimum = min(d[i-1][j]+weight, d[i][j-1]+weight, d[i-1][j-1]+2*weight)
                d[i].insert(j, minimum)
    return  d[-1][-1]

# t1=time.time()
# logKeyPara=para(threshold2=6)
# x=logkeyExtraction(logKeyPara)
# x.mainProcess()
# print('time is ',time.time()-t1)
