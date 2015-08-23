########################################################
# util.py
# This is a script containing a bag of utilities.
# Author: Jamie Zhu <jimzhu@GitHub>
# Created: 2014/2/6
# Last updated: 2015/8/17
########################################################


import os, sys, time
import logging
import numpy as np

## global
logger = logging.getLogger('logger')   


########################################################
# Config the working paths and set up logger
#
def config(para):
    config = {'exeFile': os.path.basename(sys.argv[0]),  
              'workPath': os.path.abspath('.'),
              'dataPath': os.path.abspath(para['dataPath'] + para['dataName']),
              'logFile': os.path.basename(sys.argv[0]) + '.log'
              }
    
    # delete old log file
    if os.path.exists(config['logFile']):
        os.remove(config['logFile'])
    # add result folder
    if not os.path.exists(para['outPath']):
        os.makedirs(para['outPath'])

    # set up logger to record runtime info
    if 'debugMode' in para.keys() and para['debugMode']:  
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO) 
    # log to console
    cmdhandler = logging.StreamHandler()  
    cmdhandler.setLevel(logging.DEBUG)       
    formatter = logging.Formatter(
        '%(asctime)s (pid-%(process)d): %(message)s')
    cmdhandler.setFormatter(formatter)
    logger.addHandler(cmdhandler)   
    # log to file
    if para['saveLog']:
        filehandler = logging.FileHandler(config['logFile']) 
        filehandler.setLevel(logging.DEBUG)
        filehandler.setFormatter(formatter)       
        logger.addHandler(filehandler)  
    
    logger.info('==========================================')
    logger.info('Config:')
    config.update(para)
    for name in config:
        if type(config[name]) is np.ndarray:
            logger.info('%s = [%s]'%(name, ', '.join(format(s, '.2f') for s in config[name])))
        else:
            logger.info('%s = %s'%(name, config[name]))
    
    # set print format
    np.set_printoptions(formatter={'float': '{: 0.4f}'.format})
########################################################


########################################################
# Formatting the elapsed time into day-hour-min-sec format
#
def formatElapsedTime(elapsedtime):
    minutes, seconds = divmod(elapsedtime, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    years, days = divmod(days, 365.242199)
 
    minutes = long(minutes)
    hours = long(hours)
    days = long(days)
    years = long(years)
 
    duration = ''
    if years > 0:
        duration += ('%d year' % years + 's' * (years > 1) + ', ')
    if days > 0:
        duration += ('%d day' % days + 's' * (days > 1) + ', ')
    if hours > 0:
        duration += ('%d hour' % hours + 's' * (hours > 1) + ', ')
    if minutes > 0:
        duration += ('%d minute' % minutes + 's' * (minutes > 1) + ', ')
    if seconds > 0:
        duration += ('%.2f second' % seconds + 's' * (seconds > 1) + '.')
    return duration
########################################################
