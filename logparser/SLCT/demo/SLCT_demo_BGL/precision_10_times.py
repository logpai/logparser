import os, sys, time
sys.path.append('../../')
sys.path.append('../..//')
sys.path.append('../')
from RI_SLCT import *
from SLCT_complete import *
#For SOSP: support is 12,False
#For HPC: support is 49, True
#For BGL: support is 5, True
#For Proxifier: support is 29, True
#For Zookeeper: support is 9, True

# If the dataset(.log file) is in current directory, then we need to set parameters as: para['dataPath'] = '', para['dataName'] = './'
#For SLCT, we only need to run once
data=['Sca_BGL400','Sca_BGL4k','Sca_BGL40k','Sca_BGL400k','Sca_BGL4m']
dataPath='./results_BGL/'
curData=0
result=zeros((1,9))
for i in range(0,1,1):
	para = {'dataPath': '../../../Sca/SLCT_Processed/', # data path
        'dataName': data[curData]+'/', # set the dataset name
        'para_j':True, #use the parameter j
        'outPath': './result/', # output path for results
        'supportThreshold': 5, # set support threshold
        'saveLog': False, # whether to save log into file
        }
	print('***********************************************')
	print 'the ', i+1, 'th experiment!'
	print 'current support is',para['supportThreshold']
	
	timeInterval = SLCT(para,dataPath,data,curData)

	parameters=prePara(dataname=data[curData]+'/',geneDataPath=dataPath)
	TP,FP,TN,FN,p,r,f,RI=process(parameters)
	result[i,:]=TP,FP,TN,FN,p,r,f,RI,timeInterval
	pprint(result)
savetxt('SLCT_'+data[curData]+'.csv',result,delimiter=',')

