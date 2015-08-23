import os, sys, time
sys.path.append('..')
from loglyzer import slct
from commons.util import logger
from commons import util
from commons import dataloader


#########################################################
# config area
#
para = {'dataPath': '../data/', # data path
        'dataName': 'redlug.com', # set the dataset name
        'outPath': 'result/', # output path for results
        'supportThreshold': 1, # set support threshold
        'saveTimeInfo': False, # whether to keep track of the running time
        'saveLog': True, # whether to save log into file
        'debugMode': False, # whether to record the debug info
        'parallelMode': False # whether to leverage multiprocessing for speedup
        }

initConfig(para)
#########################################################

startTime = time.time() # start timing

# load the dataset
logdata = dataloader.load(para)

inputcmd="./slct -s 1 inputfile.log"

slct.process(inputcmd)

logger.info('All done. Elaspsed time: ' + util.formatElapsedTime(time.time() - startTime)) # end timing
logger.info('==============================================')
sys.path.remove('..')