import os, sys, time
sys.path.append('../../')
sys.path.append('../')
from logparser import slct
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
        'saveLog': True, # whether to save log into file
        }
util.config(para)
#########################################################

startTime = time.time() # start timing

# load the dataset
logdata = dataloader.load(para)

# log template extraction
slct.extract(logdata, para)

logger.info('All done. Elaspsed time: ' + util.formatElapsedTime(time.time() - startTime)) # end timing
logger.info('==============================================')