#In this demo, the rawlog.log file is the HDFS data set logs.
#If you want to test on other data sets or using other parsers, please modify the parameters in this file or in the parser source file

from LogSig import *

RawLogPath = './'
RawLogFile = 'rawlog.log'
OutputPath = './results/'

#Note: you need to set some other parameters when you try other parsers or data sets
#For example, the structured columns "removeCol" (e.g., timestamp column) that will be removed before parsing. For each data set, the structure columns are different. Wrong removeCol may result in wrong parsing results. 
#All parameter setting in our experiments are attached as comments.
para=Para(path=RawLogPath, logname=RawLogFile, savePath=OutputPath)

myparser=LogSig(para)
time=myparser.mainProcess()

print ('The running time of LogSig is', time)



#Parameters

#IPLoM
# =====For BGL=====
# 	ct = 0.4
# 	lowerBound = 0.01
# 	removeCol = [0,1,2,3,4,5,6,7,8]
#   regL = ['core\.[0-9]*']
# 
# =====For HPC=====
# 	ct = 0.175
# 	lowerBound = 0.25
# 	removeCol = [0]
#   regL = ['([0-9]+\.){3}[0-9]']

# =====For HDFS=====
# 	ct = 0.35
# 	lowerBound = 0.25
# 	removeCol = [0,1,2,3,4]
#   regL = ['blk_(|-)[0-9]+','(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)']
# 
# =====For Zookeeper=====
# 	ct = 0.4
# 	lowerBound = 0.7
# 	removeCol = [0,1,2,3,4,5]
#   regL = ['(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)']
# 
# =====For Proxifier=====
# 	ct = 0.6
# 	lowerBound = 0.25
# 	removeCol = [0,1,3,4]
#   regL = []

#LogSig
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

#LKE
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
# =====For HDFS=====
# (self,path='../Sca/',dataName='Sca_SOSP600',logname='rawlog.log',removable=True,removeCol=[0,1,2,3,4,5],threshold2=3,regular=True,
# rex=['blk_(|-)[0-9]+','(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)'],savePath='./results/',saveFileName='template'):
# =====For HPC=====
# (self,path='../Sca/',dataName='Sca_HPC600',logname='rawlog.log',removable=True,removeCol=[0,1],threshold2=4,regular=True,
# rex=['([0-9]+\.){3}[0-9]'],savePath='./results/',saveFileName='template'):# line 67,change the regular expression replacement code
#******************************************************************************************

#SLCT
#For SOSP: support is 12,False
#For HPC: support is 49, True
#For BGL: support is 5, True
#For Proxifier: support is 29, True
#For Zookeeper: support is 9, True