#!/usr/bin/env python

from pprint import pprint
from RI_precision import *
from LogSig import *
result=zeros((10,9))

LogSigDataPath=['../Sca/Sca_BGL400/','../Sca/Sca_BGL4k/','../Sca/Sca_BGL40k/','../Sca/Sca_BGL400k/','../Sca/Sca_BGL4m/']

dataName=['Sca_BGL400','Sca_BGL4k','Sca_BGL40k','Sca_BGL400k','Sca_BGL4m']
curData=3
for i in range(0,10,1):
	print 'the ', i+1, 'th experiment starts here!'
	LogSigPara=Para(LogSigDataPath[curData])
	LogSigInstance=LogSig(LogSigPara)
	time=LogSigInstance.mainProcess()
	parameters=prePara(LogSigDataPath[curData])
	TP,FP,TN,FN,p,r,f,RI=process(parameters)
	result[i,:]=TP,FP,TN,FN,p,r,f,RI,time
	pprint(result)
	savetxt('10experiment_withRE'+dataName[curData]+'.csv',result,delimiter=',')

#IPLoM
#For 2kHDFS data:
#       (self,path='../Data/2kHDFS/',logname='NoID_2kHDFS.log',removable=True,removeCol=[0,1,2,3,4],regular=True,
#		rex=['blk_(|-)[0-9]+','(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)'],savePath='./results_2kHDFS/',saveFileName='template',groupNum=14):
#For 2kZookeeper:
# 		(self,path='../Data/2kZookeeper/',logname='NoID_2kZookeeper.log',removable=True,removeCol=[0,1,2,3,4,5],regular=True,
# 		rex=['(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)'],savePath='./results_2kZookeeper/',saveFileName='template',groupNum=46):
#For 2kBGL: 
#		(self,path='../Data/2kBGL/',logname='NoID_2kBGL.log',removable=True,removeCol=[0,1,2,3,4,5,6,7,8],regular=True,
#		rex=['core\.[0-9]*'],savePath='./results_2kBGL/',saveFileName='template',groupNum=100):# line 55,change the regular expression replacement code
#For 2kHPC:
#		(self,path='../Data/2kHPC/',logname='NoID_2kHPC.log',removable=True,removeCol=[0,1],regular=True,
#		rex=['([0-9]+\.){3}[0-9]'],savePath='./results_2kHPC/',saveFileName='template',groupNum=51):# line 55,change the regular expression replacement code
#For 2kProxifier:
#       (self,path='../Data/2kProxifier/',logname='NoID_2kProxifier.log',removable=False,removeCol=[0,1,3,4],regular=True,
#		rex=[''],savePath='./results_2kProxifier/',saveFileName='template',groupNum=6):

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