import re
import os
import time
from nltk import ngrams
import numpy as np
from queue import *
import gc

class Logcluster:
	def __init__(self, logTemplate='', logIDL=None):
		self.logTemplate = logTemplate
		if logIDL is None:
			logIDL = []
		self.logIDL = logIDL


class Node:
	def __init__(self, logClust=None, childD=None, token='', templateNo=0):
		self.logClust = logClust
		self.token = token
		self.templateNo = templateNo
		if childD is None:
			childD = dict()
		self.childD = childD

"""
path: the path of the input file
logName: the file name of the input file
savePath:the path of the output file
saveFileName: the file name of the output file
removable: remove columns of words in preprocessing or not
removeCol: the index of the columns to be removed
tau: how much percentage of tokens matched to merge a log message
"""

class Para:
	def __init__(self,path='./',tau=0.5, logName='rawlog.log',removable=True,removeCol=None,savePath='./results/',saveFileName='template', saveTempFileName='logTemplates.txt'):
		self.path = path
		self.logName = logName
		self.removable = removable
		self.removeCol = removeCol
		self.savePath = savePath
		self.saveFileName = saveFileName
		self.saveTempFileName = saveTempFileName
		self.tau = tau


class Spell:
	def __init__(self, para):
		self.para = para


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


	def SimpleLoopMatch(self, logClustL, seq):
		retLogClust = None

		for logClust in logClustL:
			if float(len(logClust.logTemplate)) < (0.5*len(seq)):
				continue
			
			#If the template is a subsequence of seq
			it = iter(seq)
			if all(token in seq or token=='*' for token in logClust.logTemplate):
				return logClust

		return retLogClust


	def PrefixTreeMatch(self, parentn, seq, idx, length):
		retLogClust = None	

		for i in range(idx, len(seq)):
			if seq[i] in parentn.childD:
				childn = parentn.childD[seq[i]]
				if (childn.logClust is not None):
					constLM = [w for w in childn.logClust.logTemplate if w!='*']
					if float(len(constLM))>=(0.5*length):
					# if float(len(childn.logClust.logTemplate))>(0.5*length):
						return childn.logClust
				else:
					return self.PrefixTreeMatch(childn, seq, i+1, length)

		return retLogClust


	def LCSMatch(self, logClustL, seq):
		retLogClust = None

		maxLen = -1
		maxlcs = []
		maxClust = None
		for logClust in logClustL:
			lcs = self.LCS(seq, logClust.logTemplate)
			if len(lcs)>maxLen or ( len(lcs)==maxLen and len(logClust.logTemplate)<len(maxClust.logTemplate) ):
				maxLen = len(lcs)
				maxlcs = lcs
				maxClust = logClust

		#Should be also large then tau*len(itself)
		if float(maxLen) > (self.para.tau*len(seq)):
			retLogClust = maxClust

		return retLogClust


	def getTemplate(self, lcs, seq1, seq2):
		parameterFlag = [ False for i in lcs]
		parameterFlag.append(False)

		#Whether there are parameters before constants
		i = j = 0
		while i<len(lcs) and j<len(seq1):
			if lcs[i]!=seq1[j]:
				parameterFlag[i] = True
				j += 1
			else:
				i += 1
				j += 1
		if j != len(seq1):
			parameterFlag[-1] = True

		i = j = 0
		while i<len(lcs) and j<len(seq2):
			if lcs[i]!=seq2[j]:
				parameterFlag[i] = True
				j += 1
			else:
				i += 1
				j += 1
		if j != len(seq2):
			parameterFlag[-1] = True

		#Generate template candidate
		tempVal = []
		for i in range(len(lcs)):
			if parameterFlag[i]:
				tempVal.append('*')
			tempVal.append(lcs[i])
		if tempVal[-1]:
			tempVal.append('*')

		#Combine consecutive *
		preAst = False
		retVal = []
		for temp in tempVal:
			if preAst:
				if temp == '*':
					continue
				else:
					preAst = False
					retVal.append(temp)
			else:
				if temp == '*':
					preAst = True
				retVal.append(temp)

		return retVal


	def addSeqToPrefixTree(self, rootn, newCluster):
		parentn = rootn
		seq = newCluster.logTemplate
		seq = [w for w in seq if w!='*']

		for i in range(len(seq)):
			tokenInSeq = seq[i]

			#Match
			if tokenInSeq in parentn.childD:
				matchedNode = parentn.childD[tokenInSeq]
				matchedNode.templateNo += 1
				if i+1==len(seq):
					if matchedNode.logClust is None:
						matchedNode.logClust = newCluster
					else:
						print ('add a already exist template')
				else:
					parentn = matchedNode							

			#Do not Match
			else:
				parentn.childD[tokenInSeq] = Node(token=tokenInSeq, templateNo=1)
				if i+1==len(seq):
					parentn.childD[tokenInSeq].logClust = newCluster
				parentn = parentn.childD[tokenInSeq]


	def removeSeqFromPrefixTree(self, rootn, newCluster):
		parentn = rootn
		seq = newCluster.logTemplate
		seq = [w for w in seq if w!='*']

		for tokenInSeq in seq:
			if tokenInSeq in parentn.childD:
				matchedNode = parentn.childD[tokenInSeq]
				if matchedNode.templateNo == 1:
					del parentn.childD[tokenInSeq]
					break
				else:
					matchedNode.templateNo -= 1
					parentn = matchedNode
				
			else:
				print ('Error: Try to remove non-exisiting node in trie.')

			


	def outputResult(self, logClustL):
		writeTemplate = open(self.para.savePath + self.para.saveTempFileName, 'w')

		idx = 1
		for logClust in logClustL:
			writeTemplate.write(' '.join(logClust.logTemplate) + '\n')
			writeID = open(self.para.savePath + self.para.saveFileName + str(idx) + '.txt', 'w')
			for logID in logClust.logIDL:
				writeID.write(str(logID) + '\n')
			writeID.close()
			idx += 1

		writeTemplate.close()


	def printTree(self, node, dep):
		pStr = ''	
		for i in xrange(dep):
			pStr += '\t'

		if node.token == '':
			pStr += 'No token node'
		else:
			pStr += node.token
			if node.logClust is not None:
				pStr += '-->' + ' '.join(node.logClust.logTemplate)
		print (pStr+' ('+ str(node.templateNo) + ')')
		if len(node.childD) == 0:
			return 1
		for child in node.childD:
			self.printTree(node.childD[child], dep+1)


	def deleteAllFiles(self, dirPath):
		fileList = os.listdir(dirPath)
		for fileName in fileList:
	 		os.remove(dirPath+fileName)


	def mainProcess(self):

		t1 = time.time()
		rootNode = Node()
		logCluL = []


		with open(self.para.path+self.para.logName) as lines:
			for line in lines:
				logID = int(line.split('\t')[0])
				logmessageL = line.strip().split('\t')[1].split()
				logmessageL = [word for i, word in enumerate(logmessageL) if i not in self.para.removeCol]
				constLogMessL = [w for w in logmessageL if w!='*']

				#Find an existing matched log cluster
				matchCluster = self.PrefixTreeMatch(rootNode, constLogMessL, 0, len(logmessageL))

				if matchCluster is None:
					matchCluster = self.SimpleLoopMatch(logCluL, constLogMessL)

					if matchCluster is None:
						matchCluster = self.LCSMatch(logCluL, logmessageL)


				#Match no existing log cluster
				if matchCluster is None:
					newCluster = Logcluster(logTemplate=logmessageL, logIDL=[logID])
					logCluL.append(newCluster)
					self.addSeqToPrefixTree(rootNode, newCluster)

				#Add the new log message to the existing cluster
				else:
					newTemplate = self.getTemplate(self.LCS(logmessageL, matchCluster.logTemplate), logmessageL, matchCluster.logTemplate)
					matchCluster.logIDL.append(logID)
					if ' '.join(newTemplate) != ' '.join(matchCluster.logTemplate):	
						self.removeSeqFromPrefixTree(rootNode, matchCluster)

						matchCluster.logTemplate = newTemplate
						self.addSeqToPrefixTree(rootNode, matchCluster)



		if not os.path.exists(self.para.savePath):
			os.makedirs(self.para.savePath)
		else:
			self.deleteAllFiles(self.para.savePath)

		self.outputResult(logCluL)
		t2 = time.time()

		print('this process takes',t2-t1)
		print('*********************************************')
		gc.collect()
		return t2-t1
