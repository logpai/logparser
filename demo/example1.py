#In this demo, the rawlog.log file is the HDFS data set logs.
#If you want to test on other data sets or using other parsers, please modify the parameters in this file or in the parser source file

from Drainjournal import *
from pprint import pprint
from RI_precision import *


delimiters = '\s+'
dataPath = './'
removeCol = [0,1,2,3,4]
rex = [('blk_(|-)[0-9]+', 'blkID'), ('(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)', 'IPAddandPortID')]
mt = 1
delimiters = '\s+'

#Note: you need to set some other parameters when you try other parsers or data sets
#For example, the structured columns "removeCol" (e.g., timestamp column) that will be removed before parsing. For each data set, the structure columns are different. Wrong removeCol may result in wrong parsing results. 
#All parameter setting in our experiments are attached as comments.
logName = dataPath + 'rawlog.log'
myPara = Para(logName=logName, removeCol=removeCol, rex=rex, delimiters=delimiters, mt=mt)

myParser = Drain(myPara)
runningTime = myParser.mainProcess()


# if dataset == 1:
# 	dataPath = './datasets/BGL/'
# 	# removeCol = [0,1,2,3,4,5,6,7,8,9,10]
# 	removeCol = [0,1,2,3,4,5,6,7,8]

# 	rex = [('core\.[0-9]*', 'coreNum')]
# 	mt = 1

# elif dataset == 2:
# 	dataPath = './datasets/HPC/'
# 	removeCol = [0]
# 	rex = [('([0-9]+\.){3}[0-9]', 'IPAdd'), ('node-[0-9]+', 'nodeNum')]
# 	mt = 1

# elif dataset == 3:
# 	dataPath = './datasets/Thunderbird/'
# 	rex = [('([0-9]+\.){3}[0-9]+', 'IPAdd')]
# 	mt = 1

# elif dataset == 4:
# 	dataPath = './datasets/HDFS/'
# 	removeCol = [0,1,2,3,4]
# 	rex = [('blk_(|-)[0-9]+', 'blkID'), ('(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)', 'IPAddandPortID')]
# 	mt = 1
# 	delimiters = '\s+'

# elif dataset == 5:
# 	dataPath = './datasets/Zookeeper/'
# 	# removeCol = [0,1,2,3,4,5,6,7,8]
# 	removeCol = [0,1,2,3,4,5]

# 	rex = [('(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)', 'IPAddandPortID')]
# 	mt = 1.0

# elif dataset == 6:
# 	dataPath = './datasets/Hadoop/'
# 	rex = []
# 	mt = 1

# elif dataset == 7:
# 	dataPath = './datasets/Spark/'
# 	rex = []
# 	mt = 1

# elif dataset == 8:
# 	dataPath = './datasets/Windows/'
# 	rex = []
# 	mt = 1

# elif dataset == 9:
# 	dataPath = './datasets/Linux/'
# 	rex = [('([0-9]+\.){3}[0-9]+', 'IPAdd')]
# 	mt = 1

# elif dataset == 10:
# 	dataPath = './datasets/Mac/'
# 	rex = []
# 	mt = 1

# elif dataset == 11:
# 	dataPath = './datasets/Apache/'
# 	rex = []
# 	mt = 1

# else:
# 	dataPath = './datasets/Proxifier/'
# 	removeCol = [0,1,3,4]
# 	rex = []
# 	mt = 0.95
# 	# mt = 1
