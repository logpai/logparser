from pyspark import SparkConf
from pyspark import SparkContext
from collections import Counter
import re
import operator

from scipy.cluster.hierarchy import dendrogram, linkage
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from scipy.cluster.hierarchy import cophenet
from scipy.spatial.distance import pdist
from scipy.cluster.hierarchy import fcluster

import os
import time

#user can change the parameters in conf to allocate computing resources
conf = (SparkConf().setAppName("myParser").set("spark.serializer", "org.apache.spark.serializer.KryoSerializer").set("spark.executor.cores", "5").set("spark.executor.instances", "16").set("spark.executor.memory", "25G").set("spark.ui.killEnabled", "true"))
sc = SparkContext(conf = conf)

eventL = []
notCombineRDDL = []
resultRDDL = []
resultEventL = []

dataset = 3
inputPath = 'hdfs:///pjhe/logs/sosp_29_withID.log'
dataName = 'time'
#Debug
####################################################
DEBUGMODE = False
if DEBUGMODE:
	writeDebug = open('debug.txt', 'w')


#Parameters
####################################################
outputPath = 'hdfs:///pjhe/test/'
useRemoveCol = True
useRegex = True
useSpecial = False
templateFile = './result/templates.txt'
writeTemplate = open(templateFile, 'w')
regexL = []
specialL = []
specialNum = 0


#BGL=1, HPC=2, HDFS=3, Zookeeper=4, Proxifier=5
if dataset == 1:
	#inputPath = 'hdfs:///pjhe/logs/2kBGL.log'
	step3Support = 0.6
	splitRel = 0.1
	splitAbs = 10
	removeCol = [0,1,2,3,4,5,6,7,8]
	regexL = ['core\.[0-9]*']
	maxDistance = 0
elif dataset == 2:
	#inputPath = 'hdfs:///pjhe/logs/2kHPC.log'
	step3Support = 0.6
	splitRel = 0.1
	splitAbs = 10
	removeCol = [0]
	regexL = ['([0-9]+\.){3}[0-9]']
	maxDistance = 0
elif dataset == 3:
	#inputPath = 'hdfs:///pjhe/logs/2kSOSP.log'
	step3Support = 0.6
	splitRel = 0.1
	splitAbs = 10
	removeCol = [0,1,2,3,4]
	regexL = ['blk_(|-)[0-9]+','(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)']
	maxDistance = 0
elif dataset == 4:
	#inputPath = 'hdfs:///pjhe/logs/2kZookeeper.log'
	step3Support = 0.6
	splitRel = 0.1
	splitAbs = 10
	removeCol = [0,1,2,3,4,5]
	regexL = ['(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)']
	maxDistance = 0
elif dataset == 5:
	#inputPath = 'hdfs:///pjhe/logs/2kProxifier.log'
	step3Support = 0.3
	splitRel = 0.1
	splitAbs = 5
	removeCol = [0,1,3,4]
	useRegex = False
	maxDistance = 10
	specialL = ['<1 sec']
	useSpecial = True



#broadcast the parameters
bcuseRemoveCol = sc.broadcast(useRemoveCol)
bcremoveCol = sc.broadcast(removeCol)
bcuseRegex = sc.broadcast(useRegex)
bcregexL = sc.broadcast(regexL)
bcspecialL = sc.broadcast(specialL)
####################################################


#Functions
####################################################
def my_tokenizer(s):
	return s.strip().split()

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
	while lenOfSeq1!=0 and lenOfSeq2!=0:
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

def seqLen(lenS, logLen):
	lenS.add(logLen)
	return lenS

def combLen(lenS1, lenS2):
	return lenS1.union(lenS2)

def findTemplate(log1L, log2L):
	assert len(log1L)==len(log2L)
	i = 0
	for word2 in log2L:
		if word2=='*' or log1L[i]=='*' or word2 != log1L[i]:
			log1L[i] = '*'
		i += 1

	return log1L

def seqLS(tokenLS, log):
	length = len(tokenLS)
	wordSeq = log.strip().split()
	for columnIdx in range(length):		
		if len(tokenLS[columnIdx]) == 99:
			tokenLS[columnIdx] = set(range(100))
		elif len(tokenLS[columnIdx]) > 99:
			continue
		else:
			tokenLS[columnIdx].add(wordSeq[columnIdx])

	return tokenLS

def combLS(tokenLS1, tokenLS2):
	length = len(tokenLS1)
	for columnIdx in range(length):
		tokenLS1[columnIdx] = tokenLS1[columnIdx].union(tokenLS2[columnIdx])
		if len(tokenLS1[columnIdx]) > 99:
			tokenLS1[columnIdx] = set(range(100))
	return tokenLS1

#Preprocessing
def preprocess(log, uRemoveCol, removeC, uRegex, regL):
	global dataset
	if uRemoveCol:
		wordL = log.strip().split()
		wordL = [word for i, word in enumerate(wordL) if i not in removeC]
		log = ' '.join(wordL)

	if uRegex:
		for currentRex in regL:
			if dataset == 1:
				log = re.sub(currentRex,'core.',log)
			else:
				log = re.sub(currentRex, '', log)
		if dataset == 2:
			log = re.sub('node-[0-9]+','node-',log)
			#print '---------------------------------------------'

	return log

def isNotSpecial(speL, log):
	result = True
	for spe in speL:
		if re.search(spe, log) is None:
			continue
		else:
			result = False
			break
	return result

def step3(partitionRDD, eventLen, dep):
	global notCombineRDDL, eventL, step3Support, splitRel, splitAbs
	
	if dep==-1:
		step4(partitionRDD, eventLen)
		return 1

	initialValue = []
	for i in range(eventLen):
		initialValue.append(set())

	#count the number of unique words in a column, [{set1}, {set2}, {set3}, ...]
	step3TokenCountLS = partitionRDD.map(lambda (ID, log): log).aggregate(initialValue, seqLS, combLS)

	count_1 = 0
	step3SplitPos = -1
	minTokenCountN1 = 100

	#count the number of count_1 among all columns, and find out the column with second smallest unique words
	for i in range(eventLen):
		if len(step3TokenCountLS[i]) == 1:
			count_1 += 1
		elif len(step3TokenCountLS[i]) < minTokenCountN1:
			step3SplitPos = i
			minTokenCountN1 = len(step3TokenCountLS[i])

	#if the number of count_1 is larger than a threshold, it indicates that this group doesn't need further split
	if float(count_1)/eventLen>step3Support or step3SplitPos==-1:
		step4(partitionRDD, eventLen)
		return 1

	#count the number of logs in this group
	numOfLogstep2 = partitionRDD.count()


	#if the column with the second smallest unique word contains variables directly go to step 4
	if minTokenCountN1>numOfLogstep2*splitRel and minTokenCountN1>splitAbs:
		step4(partitionRDD, eventLen)
		return 1

	#if the column with the second smallest unique word contains constants, recursively split until all logs in the group share the same template 
	step3SplitUniqueWordS = step3TokenCountLS[step3SplitPos]
	
	for uniqueWord in step3SplitUniqueWordS:
		step3halfRDD = partitionRDD.filter(lambda (ID, log): log.split()[step3SplitPos] == uniqueWord)
		step3(step3halfRDD, eventLen, dep+1)

# partitionRDD - (ID, log)
def step4(partitionRDD, eventLen):
	global notCombineRDDL, eventL, maxDistance, resultEventL, specialNum

	if maxDistance ==0:
		logEventL = partitionRDD.map(lambda (ID, log): log.split()).reduce(findTemplate)
		resultEventL.append(" ".join(logEventL))
		partitionRDD.map(lambda (ID, log): ID).saveAsTextFile(outputPath + str(len(resultEventL)+specialNum))
	else:
		partitionRDD.cache()
		partitionRDD.count()
		notCombineRDDL.append(partitionRDD)
		logEventL = partitionRDD.map(lambda (ID, log): log.split()).reduce(findTemplate)
		eventL.append( " ".join(logEventL) )
	


def step5(max_d):
	global eventL, notCombineRDDL, resultEventL, resultRDDL, outputPath, specialNum

	#vectorize the text
	vectorizer = CountVectorizer(analyzer = "word", tokenizer = my_tokenizer, preprocessor = None, stop_words = ['*'], max_features = 10000) 

	train_data_features = vectorizer.fit_transform(eventL)
	train_data_features = train_data_features.toarray()

	#hierarchical clustering
	Z = linkage(train_data_features, 'complete', 'cityblock')
	#c, coph_dists = cophenet(Z, pdist(train_data_features))
	#print 'The goodness of cluster result:', c

	clusters = fcluster(Z, max_d, criterion='distance')

	#initialize RDD list and Event list
	resultEventLL = []
	resultRDDLL = []
	numCombinedEvents = max(clusters)
	for i in range(numCombinedEvents):
		resultRDDLL.append([])
		resultEventLL.append([])

	#Put event/RDD that belong to the same cluster into the same list
	currentEventNum = 0
	for clusterNum in clusters:
		resultRDDLL[clusterNum-1].append(notCombineRDDL[currentEventNum])
		resultEventLL[clusterNum-1].append(eventL[currentEventNum])
		currentEventNum +=1
	
	#Merge the event/RDD in the same list
	for sameEventL in resultEventLL:

		if len(sameEventL) == 1:
			resultEventL.append(sameEventL[0])
		else:
			combinedEvent = sameEventL[0].strip().split()
			count = 0
			for currentEvent in sameEventL:
				if count == 0:
					count += 1
					continue
				else:
					combinedEvent = LCS(combinedEvent, currentEvent.strip().split())
					count += 1
			resultEventL.append(' '.join(combinedEvent))

	for sameRDDL in resultRDDLL:
		if len(sameRDDL) == 1:
			resultRDDL.append(sameRDDL[0])
		else:
			resultRDDL.append(sc.union(sameRDDL))

		resultRDDL[-1].map(lambda (ID, log): ID).saveAsTextFile(outputPath + str(len(resultRDDL)+specialNum))
		#resultRDDL[-1].map(lambda (ID, log): str(ID)+'\t'+log).saveAsTextFile(outputPath + str(len(resultRDDL)+specialNum))
			

####################################################



text_file = sc.textFile(inputPath, 20)

#step 1
#-RDD (ID, log)
step1halfRDD = text_file.map( lambda x: (x.split('\t')[0], preprocess(x.strip().split('\t')[1], bcuseRemoveCol.value, bcremoveCol.value, bcuseRegex.value, bcregexL.value)) )

if useSpecial:
	for special in specialL:
		currentRDD = step1halfRDD.filter(lambda (ID, log): re.search(special, log) is not None)
		logEvent = currentRDD.take(1)[0][0]
		resultEventL.append(logEvent)
		specialNum += 1
		currentRDD.map(lambda (ID, log): ID).saveAsTextFile(outputPath + str(specialNum))

	step1RDD = step1halfRDD.filter(lambda (ID, log): isNotSpecial(bcspecialL.value, log)).cache()
else:
	step1RDD = step1halfRDD.cache()

step1RDD.count()


print "******************************************Step 1 is done******************************************"

#step 2
eventLens = step1RDD.map(lambda (ID, log): len(log.split())).aggregate(set(), seqLen, combLen)

print "Step 2 number of event: ", len(eventLens)
print "Step 2 event lengths: ", eventLens
print "******************************************Step 2 is done******************************************"

#step 3
for eventLen in eventLens:
	print ("Step 3 on event with length: " + str(eventLen))

	#-RDD (ID, log) | Each RDD contains (ID, log) in the same partition
	step2RDD = step1RDD.filter(lambda (ID, log): len(log.split()) == eventLen).cache()	                   
	
	step3(step2RDD, eventLen, 1)
	
if maxDistance>0:
	step5(maxDistance)

for currentEvent in resultEventL:
	writeTemplate.write(currentEvent + '\n')
					
writeTemplate.close()



if DEBUGMODE:
	writeDebug.close()
