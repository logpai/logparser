import re
import os
import time
import numpy as np
import gc
import math


#Similarity layer
class Logcluster:
	def __init__(self, logTemplate='', st=0.1, outcell=None):
		self.logTemplate = logTemplate
		self.updateCount = 0
		self.st = st
		self.base = -1
		self.initst = -1
		self.outcell = outcell

#Length layer and Token layer
class Node:
	def __init__(self, childD=None, digitOrtoken=None):
		if childD is None:
			childD = dict()
		self.childD = childD
		self.digitOrtoken = digitOrtoken

#Output layer
class Ouputcell:
	def __init__(self, logIDL=None, parentL=None):
		if logIDL is None:
			logIDL = []
		self.logIDL = logIDL
		self.outTemplates = ''
		self.active = True
		parentL = []
		self.parentL = parentL

"""
rex: regular expressions used in preprocessing (step1) [(rex, substitude), ...]
path: the input path stores the input log file name
maxChild: max number of children of an internal node
logName:the name of the input file containing raw log messages
removeCol: the index of column needed to remove
savePath: the output path stores the file containing structured logs
saveTempFileName: the output template file name
mt: similarity threshold for the merge step
"""


class Para:
	def __init__(self, rex=None, path='', maxChild=120, logName='rawlog.log',removeCol=None,savePath='./results/',saveFileName='template', saveTempFileName='logTemplates.txt', delimiters=' ', mt=1):
		self.path = path
		self.maxChild = maxChild
		self.logName = logName
		self.savePath = savePath
		self.saveFileName = saveFileName
		self.saveTempFileName = saveTempFileName
		self.delimiters = delimiters
		self.mt = mt

		if removeCol is None:
			removeCol = []
		self.removeCol = removeCol

		if rex is None:
			rex = []
		self.rex = rex


class Drain:
	def __init__(self, para):
		self.para = para
		#create the list of the pointer
		self.pointer = dict()

	#Check if there is number
	def hasNumbers(self, s):
		return any(char.isdigit() for char in s)

	#Check if there is special character
	def hasPun(self, s):
		punStr = "#$&'*+,/<=>@^_`|~)"
		punChars = set(punStr)
		return any(char in punChars for char in s)

	#Check if there is special character,
	def lastTokenPun(self, s):
		punStr = ".#$&'*+,/<=>@^_`|~)"
		punChars = set(punStr)
		haspuns = any(char in punChars for char in s)

		if not haspuns:
			return False
		if re.match('^[\w]+[#$&\'*+,\/<=>@^_`|~.]+$', s):
			return False
		return True


	def treeSearch(self, rn, seq):
		retLogClust = None

		seqLen = len(seq)

		if seqLen not in rn.childD:
			return retLogClust

		#if the pointer exist, compare the pointer and the new log first
		logClust = self.pointer[seqLen]


		# if first token or last token matches with the key in the tree, them calculate similarity; otherwise, skip
		if (logClust.logTemplate[0]==seq[0] and not self.hasNumbers(seq[0]) and not self.hasPun(seq[0])) or (logClust.logTemplate[-1]==seq[-1] and not self.hasNumbers(seq[-1]) and not self.hasPun(seq[-1])) or (logClust.logTemplate[0]=='*' and logClust.logTemplate[-1]=='*'):
			curSim, curNumOfPara = self.SeqDist(logClust.logTemplate, seq)
			if  curSim >= logClust.st:
				retLogClust = logClust
				return retLogClust

		lenLayerNode = rn.childD[seqLen]

		tokenFirst = seq[0]
		tokenLast = seq[-1]

		tokenFirstKey = '00_Drain_' + tokenFirst
		tokenLastKey = '-1_Drain_' + tokenLast

		tokenLayerNode = None
		if tokenFirstKey in lenLayerNode.childD:
			tokenLayerNode = lenLayerNode.childD[tokenFirstKey]
		elif tokenLastKey in lenLayerNode.childD:
			tokenLayerNode = lenLayerNode.childD[tokenLastKey]
		elif self.hasNumbers(tokenFirst) and self.hasNumbers(tokenLast) and '*' in lenLayerNode.childD:
			tokenLayerNode = lenLayerNode.childD['*']
		else:
			return retLogClust

		logClustL = tokenLayerNode.childD

		retLogClust = self.FastMatch(logClustL, seq)

		# update the pointer
		if retLogClust is not None:
			self.pointer[len(seq)] = retLogClust

		return retLogClust


	def addSeqToTree(self, rn, logClust):
		seqLen = len(logClust.logTemplate)
		if seqLen not in rn.childD:
			lenLayerNode = Node(digitOrtoken=seqLen)
			rn.childD[seqLen] = lenLayerNode

			# add an others-node for the token layer
			newNode = Node(digitOrtoken='*')
			lenLayerNode.childD['*'] = newNode

		else:
			lenLayerNode = rn.childD[seqLen]


		tokenFirst = logClust.logTemplate[0]
		tokenLast = logClust.logTemplate[-1]

		tokenFirstKey = '00_Drain_' + tokenFirst
		tokenLastKey = '-1_Drain_' + tokenLast

		# if the index token already exists
		if (tokenFirstKey) in lenLayerNode.childD:
			tokenLayerNode = lenLayerNode.childD[tokenFirstKey]
		elif (tokenLastKey) in lenLayerNode.childD:
			tokenLayerNode = lenLayerNode.childD[tokenLastKey]
		else:			
			# need to add index token to the tree
			if len(lenLayerNode.childD) == self.para.maxChild:
				tokenLayerNode = lenLayerNode.childD['*']
			else:
				# first token has numbers
				if self.hasNumbers(tokenFirst):
					# last token has numbers
					if self.hasNumbers(tokenLast):
						tokenLayerNode = lenLayerNode.childD['*']
					# last token does not have numbers
					else:
						newNode = Node(digitOrtoken=tokenLastKey)
						lenLayerNode.childD[tokenLastKey] = newNode
						tokenLayerNode = newNode						

				# first token does not have numbers
				else:
					# last token has numbers
					if self.hasNumbers(tokenLast):
						newNode = Node(digitOrtoken=tokenFirstKey)
						lenLayerNode.childD[tokenFirstKey] = newNode
						tokenLayerNode = newNode
					# last token does not have numbers
					else:
						# last token has punctuations
						if self.hasPun(tokenLast):
							newNode = Node(digitOrtoken=tokenFirstKey)
							lenLayerNode.childD[tokenFirstKey] = newNode
							tokenLayerNode = newNode
						# first token has punctuations, last token does not have punctuations
						elif self.hasPun(tokenFirst):
							newNode = Node(digitOrtoken=tokenLastKey)
							lenLayerNode.childD[tokenLastKey] = newNode
							tokenLayerNode = newNode
						# first/last token has punctuations
						else:
							newNode = Node(digitOrtoken=tokenFirstKey)
							lenLayerNode.childD[tokenFirstKey] = newNode
							tokenLayerNode = newNode


		# add the cluster to the leave node
		if len(tokenLayerNode.childD) == 0:
			tokenLayerNode.childD = [logClust]
		else:
			tokenLayerNode.childD.append(logClust)

	#seq1 is template
	def SeqDist(self, seq1, seq2):
		assert len(seq1) == len(seq2)
		
		simTokens = 0
		numOfPar = 0

		for token1, token2 in zip(seq1, seq2):
			if token1 == '*':
				numOfPar += 1
				continue
			if token1 == token2:
				simTokens += 1

		numOfCon = len(seq1)-numOfPar
		if numOfCon == 0:
			if len(seq1)==1 and self.hasNumbers(seq2[0]):
				retVal = 1.0
			else:
				retVal = 0.0
		else:
			retVal = float(simTokens) / numOfCon

		return retVal, numOfPar


	#Find the most suitable log cluster in the leaf node, token-wise comparison, used to find the most similar cluster
	def FastMatch(self, logClustL, seq):
		retLogClust = None

		maxSim = -1
		maxNumOfPara = -1
		maxClust = None

		for logClust in logClustL:
			curSim, curNumOfPara = self.SeqDist(logClust.logTemplate, seq)
			# when similarity is the same, pick the one with more parameters
			if curSim>maxSim or (curSim==maxSim and curNumOfPara>maxNumOfPara):
				maxSim = curSim
				maxNumOfPara = curNumOfPara
				maxClust = logClust

		# if similarity is larger than st
		if maxClust is not None and maxSim >= maxClust.st:
			retLogClust = maxClust

		return retLogClust


	def getTemplate(self, seq1, seq2):
		assert len(seq1) == len(seq2)
		retVal = []

		updatedToken = 0
		for token1, token2 in zip(seq1, seq2):
			if token1 == token2:
				retVal.append(token1)
			else:
				if token2 != '*':
					updatedToken += 1
				retVal.append('*')

		return retVal, updatedToken


	# delete a folder
	def deleteAllFiles(self, dirPath):
		fileList = os.listdir(dirPath)
		for fileName in fileList:
	 		os.remove(dirPath+fileName)


	# print a tree with depth 'dep', root node is in depth 0
	def printTree(self, node, dep):
		pStr = ''
		for i in range(dep):
			pStr += '\t'

		if dep == 0:
			pStr += 'Root Node'
		elif dep == 1:
			pStr += '<' + str(node.digitOrtoken) + '>'
		else:
			pStr += node.digitOrtoken

		print (pStr)

		if dep == 2:
			for child in node.childD:
				print ('\t\t\t' + ' '.join(child.logTemplate))
			return 1
		for child in node.childD:
			self.printTree(node.childD[child], dep+1)


	# return the lcs in a list
	def LCS(self, seq1, seq2):
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


	def adjustOutputCell(self, logClust, logClustL):
		
		similarClust = None
		lcs = []
		similarity = -1
		logClustLen = len(logClust.logTemplate)


		for currentLogClust in logClustL:
			currentClustLen = len(currentLogClust.logTemplate)
			if currentClustLen==logClustLen or currentLogClust.outcell==logClust.outcell:
				continue
			currentlcs = self.LCS(logClust.logTemplate, currentLogClust.logTemplate)
			currentSim = float(len(currentlcs)) / min(logClustLen, currentClustLen)

			if currentSim>similarity or (currentSim==similarity and len(currentlcs)>len(lcs)):
				similarClust = currentLogClust
				lcs = currentlcs
				similarity = currentSim

		if similarClust is not None and similarity>self.para.mt:		
			similarClust.outcell.logIDL = similarClust.outcell.logIDL + logClust.outcell.logIDL

			removeOutputCell = logClust.outcell

			for parent in removeOutputCell.parentL:
				similarClust.outcell.parentL.append(parent)
				parent.outcell = similarClust.outcell

			removeOutputCell.logIDL = None
			removeOutputCell.active = False

		
				

	def outputResult(self, logClustL, rawoutputCellL):
		writeTemplate = open(self.para.savePath + self.para.saveTempFileName, 'w')

		outputCellL = []
		for currenOutputCell in rawoutputCellL:
			if currenOutputCell.active:
				outputCellL.append(currenOutputCell)			

		for logClust in logClustL:
			# it is possible that several logClusts point to the same outcell, so we present all possible templates separated by '\t---\t'
			currentTemplate = ' '.join(logClust.logTemplate) + '\t---\t'
			logClust.outcell.outTemplates = logClust.outcell.outTemplates + currentTemplate

		for idx, outputCell in enumerate(outputCellL):
			writeTemplate.write(str(idx+1) + '\t' + outputCell.outTemplates+'\n')

			writeID = open(self.para.savePath + self.para.saveFileName + str(idx+1) + '.txt', 'w')

			for logID in outputCell.logIDL:
				writeID.write(str(logID) + '\n')
			writeID.close()

			# print (outputCell.outTemplates)

		writeTemplate.close()


	def mainProcess(self):

		t1 = time.time()
		rootNode = Node()

		# list of nodes in the similarity layer containing similar logs clustered by heuristic rules
		logCluL = []

		# list of nodes in the final layer that outputs containing logs
		outputCeL = []

		with open(self.para.path+self.para.logName) as lines:
			for line in lines:
				logID = int(line.split('\t')[0])
				# logmessageL = re.split(self.para.delimiters, line.strip().split('\t')[1])
				logmessageL = line.strip().split('\t')[1].split()

				if self.para.removeCol is not None:
					logmessageL = [word for i, word in enumerate(logmessageL) if i not in self.para.removeCol]
				cookedLine = ' '.join(logmessageL)


				#LAYER--Preprocessing
				for currentRex in self.para.rex:
					cookedLine = re.sub(currentRex[0], currentRex[1], cookedLine)

				logmessageL = cookedLine.split()

				# length 0 logs, which are anomaly cases
				if len(logmessageL) == 0:
					continue
				matchCluster = self.treeSearch(rootNode, logmessageL)


				# match no existing log cluster
				if matchCluster is None:
					newOCell = Ouputcell(logIDL=[logID])
					# newOCell = Ouputcell(logIDL=[line.strip()]) #for debug

					newCluster = Logcluster(logTemplate=logmessageL, outcell=newOCell)
					newOCell.parentL.append(newCluster)

					# the initial value of st is 0.5 times the percentage of non-digit tokens in the log message
					numOfPar = 0
					for token in logmessageL:
						if self.hasNumbers(token):
							numOfPar += 1

					# "st" is the similarity threshold used by the similarity layer
					newCluster.st = 0.5 * (len(logmessageL)-numOfPar) / float(len(logmessageL))
					newCluster.initst = newCluster.st

					# when the number of numOfPar is larger, the group tend to accept more log messages to generate the template
					newCluster.base = max(2, numOfPar + 1)

					logCluL.append(newCluster)
					outputCeL.append(newOCell)

					self.addSeqToTree(rootNode, newCluster)

					# update the cache
					self.pointer[len(logmessageL)] = newCluster

				#successfully match an existing cluster, add the new log message to the existing cluster
				else:
					newTemplate, numUpdatedToken = self.getTemplate(logmessageL, matchCluster.logTemplate)
					matchCluster.outcell.logIDL.append(logID)
					# matchCluster.outcell.logIDL.append(line.strip()) #for debug

					if ' '.join(newTemplate) != ' '.join(matchCluster.logTemplate):
						matchCluster.logTemplate = newTemplate

						# the update of updateCount
						matchCluster.updateCount = matchCluster.updateCount + numUpdatedToken						
						matchCluster.st = min( 1, matchCluster.initst + 0.5*math.log(matchCluster.updateCount+1, matchCluster.base) )
						
						# if the merge mechanism is used, them merge the nodes
						if self.para.mt < 1:
							self.adjustOutputCell(matchCluster, logCluL)					


		if not os.path.exists(self.para.savePath):
			os.makedirs(self.para.savePath)
		else:
			self.deleteAllFiles(self.para.savePath)

		self.outputResult(logCluL, outputCeL)
		t2 = time.time()

		print('this process takes',t2-t1)
		print('*********************************************')
		gc.collect()
		return t2-t1
