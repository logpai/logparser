"""
Description : This file implements the Drain algorithm for log parsing
Author      : LogPAI team
License     : MIT
"""
import pickle
import re
import os
import numpy as np
import pandas as pd
import hashlib
from datetime import datetime


class HistoryManager:
    """
    Imports and exports history. History consists of the tree (recursively retrieved from
    rootNode), the log clusters (logCluL), total number of log lines read (use to extract
    only the new log lines to save to {}_structured.csv)
    """

    rootNode = None
    logCluL = None
    rootDict = None
    logClustersList = None
    lastLineCount = 0

    def __init__(self, rootNode=None, logCluL=None, history=None, lastLineCount=0):
        if history is not None:
            self.import_history(history)
        else:
            self.rootNode = rootNode
            self.logCluL = logCluL
            self.lastLineCount = lastLineCount

    def import_history(self, history):
        with open(history, 'rb') as frb:
            raw_history_data = pickle.load(frb)
        self.rootDict = raw_history_data["rootDict"]
        self.lastLineCount = raw_history_data["lastLineCount"]
        self.recreate_tree()
        self.recreate_log_clusters()

    def export_history(self, history, force=False):
        if os.path.exists(history) and not force:
            if os.path.exists(history + "_backup"):
                os.remove(history + "_backup")
            os.rename(history, history + "_backup")
        raw_history_data = {'rootDict': self.rootNode.export_as_dict(),
                            'lastLineCount': self.lastLineCount}
        with open(history, 'wb') as fwb:
            pickle.dump(raw_history_data, fwb)

    def recreate_log_clusters(self):
        """
        Recreates logCluL using the tree instead of generating from history to match pointers between
        the objects
        """
        self.logCluL = self.recursive_subroutine_recreate_log_clusters(self.rootNode)

    def recursive_subroutine_recreate_log_clusters(self, node):
        if isinstance(node.childD, list):  # Is leaf
            return node.childD
        else:
            result = list()
            for child_id, child_item in node.childD.items():
                result.extend(self.recursive_subroutine_recreate_log_clusters(child_item))
            return result

    def recreate_tree(self):
        self.rootNode = self.recursive_subroutine_recreate_tree(self.rootDict)

    def recursive_subroutine_recreate_tree(self, node):
        if isinstance(node['childD'], list):  # Is leaf
            logClustersList = []
            for x in node['childD']:
                logClustersList.append(Logcluster(dict_input=x))
            return Node(childD=logClustersList, depth=node['depth'], digitOrtoken=node['digitOrtoken'])
        else:
            temp_child_dict = dict()
            for child_id, child_item in node['childD'].items():
                temp_child_dict[child_id] = self.recursive_subroutine_recreate_tree(child_item)
            return Node(childD=temp_child_dict, depth=node['depth'], digitOrtoken=node['digitOrtoken'])


class Logcluster:
    def __init__(self, logTemplate='', logIDL=None, dict_input=None):
        if dict_input is not None:
            self.logTemplate = dict_input['logTemplate']
            self.logIDL = dict_input['logIDL']
        else:
            self.logTemplate = logTemplate
            if logIDL is None:
                logIDL = []
            self.logIDL = logIDL

    def export_as_dict(self):
        return {"logIDL": self.logIDL,
                "logTemplate": self.logTemplate}


class Node:
    def __init__(self, childD=None, depth=0, digitOrtoken=None):
        if childD is None:
            childD = dict()
        self.childD = childD
        self.depth = depth
        self.digitOrtoken = digitOrtoken

    def export_as_dict(self):
        if isinstance(self.childD, list):  # Is leaf
            return {"depth": self.depth,
                    "digitOrtoken": self.digitOrtoken,
                    "childD": [x.export_as_dict() for x in self.childD]}
        else:
            temp_child_dict = dict()
            for child_id, child_item in self.childD.items():
                temp_child_dict[child_id] = child_item.export_as_dict()
            return {"depth": self.depth,
                    "digitOrtoken": self.digitOrtoken,
                    "childD": temp_child_dict}


class LogParser:
    def __init__(self, log_format, indir='./', outdir='./result/', depth=4, st=0.4,
                 maxChild=100, rex=[], keep_para=True, resume_training=False, history="history"):
        """
        Attributes
        ----------
            rex : regular expressions used in preprocessing (step1)
            path : the input path stores the input log file name
            depth : depth of all leaf nodes
            st : similarity threshold
            maxChild : max number of children of an internal node
            logName : the name of the input file containing raw log messages
            savePath : the output path stores the file containing structured logs
            resume_training : True to continue training from an existing history, history must not be None
            history : history file name to continue training model, will be appended to outdir to get full file path
        """
        self.path = indir
        self.depth = depth - 2
        self.st = st
        self.maxChild = maxChild
        self.logName = None
        self.savePath = outdir
        self.df_log = None
        self.log_format = log_format
        self.rex = rex
        self.keep_para = keep_para
        self.history = os.path.join(outdir, history)
        self.resume_training = resume_training
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        if resume_training:
            if not os.path.exists(self.history):
                print("No history found at {} to resume training!".format(self.history))
                print("Starting training from scratch")
                self.resume_training = False

    def hasNumbers(self, s):
        return any(char.isdigit() for char in s)

    def treeSearch(self, rn, seq):
        retLogClust = None

        seqLen = len(seq)
        if seqLen not in rn.childD:
            return retLogClust

        parentn = rn.childD[seqLen]

        currentDepth = 1
        for token in seq:
            if currentDepth >= self.depth or currentDepth > seqLen:
                break

            if token in parentn.childD:
                parentn = parentn.childD[token]
            elif '<*>' in parentn.childD:
                parentn = parentn.childD['<*>']
            else:
                return retLogClust
            currentDepth += 1

        logClustL = parentn.childD

        retLogClust = self.fastMatch(logClustL, seq)

        return retLogClust

    def addSeqToPrefixTree(self, rn, logClust):
        seqLen = len(logClust.logTemplate)
        if seqLen not in rn.childD:
            firtLayerNode = Node(depth=1, digitOrtoken=seqLen)
            rn.childD[seqLen] = firtLayerNode
        else:
            firtLayerNode = rn.childD[seqLen]

        parentn = firtLayerNode

        currentDepth = 1
        for token in logClust.logTemplate:

            #Add current log cluster to the leaf node
            if currentDepth >= self.depth or currentDepth > seqLen:
                if len(parentn.childD) == 0:
                    parentn.childD = [logClust]
                else:
                    parentn.childD.append(logClust)
                break

            #If token not matched in this layer of existing tree. 
            if token not in parentn.childD:
                if not self.hasNumbers(token):
                    if '<*>' in parentn.childD:
                        if len(parentn.childD) < self.maxChild:
                            newNode = Node(depth=currentDepth + 1, digitOrtoken=token)
                            parentn.childD[token] = newNode
                            parentn = newNode
                        else:
                            parentn = parentn.childD['<*>']
                    else:
                        if len(parentn.childD)+1 < self.maxChild:
                            newNode = Node(depth=currentDepth+1, digitOrtoken=token)
                            parentn.childD[token] = newNode
                            parentn = newNode
                        elif len(parentn.childD)+1 == self.maxChild:
                            newNode = Node(depth=currentDepth+1, digitOrtoken='<*>')
                            parentn.childD['<*>'] = newNode
                            parentn = newNode
                        else:
                            parentn = parentn.childD['<*>']
            
                else:
                    if '<*>' not in parentn.childD:
                        newNode = Node(depth=currentDepth+1, digitOrtoken='<*>')
                        parentn.childD['<*>'] = newNode
                        parentn = newNode
                    else:
                        parentn = parentn.childD['<*>']

            #If the token is matched
            else:
                parentn = parentn.childD[token]

            currentDepth += 1

    #seq1 is template
    def seqDist(self, seq1, seq2):
        assert len(seq1) == len(seq2)
        simTokens = 0
        numOfPar = 0

        for token1, token2 in zip(seq1, seq2):
            if token1 == '<*>':
                numOfPar += 1
                continue
            if token1 == token2:
                simTokens += 1 

        retVal = float(simTokens) / len(seq1)

        return retVal, numOfPar


    def fastMatch(self, logClustL, seq):
        retLogClust = None

        maxSim = -1
        maxNumOfPara = -1
        maxClust = None

        for logClust in logClustL:
            curSim, curNumOfPara = self.seqDist(logClust.logTemplate, seq)
            if curSim>maxSim or (curSim==maxSim and curNumOfPara>maxNumOfPara):
                maxSim = curSim
                maxNumOfPara = curNumOfPara
                maxClust = logClust

        if maxSim >= self.st:
            retLogClust = maxClust  

        return retLogClust

    def getTemplate(self, seq1, seq2):
        assert len(seq1) == len(seq2)
        retVal = []

        i = 0
        for word in seq1:
            if word == seq2[i]:
                retVal.append(word)
            else:
                retVal.append('<*>')

            i += 1

        return retVal

    def outputResult(self, logClustL, last_line_count=0):
        log_templates = [0] * (self.df_log.shape[0] + last_line_count)
        log_templateids = [0] * (self.df_log.shape[0] + last_line_count)
        df_events = []
        for logClust in logClustL:
            template_str = ' '.join(logClust.logTemplate)
            occurrence = len(logClust.logIDL)
            template_id = hashlib.md5(template_str.encode('utf-8')).hexdigest()[0:8]
            for logID in logClust.logIDL:
                logID -= 1
                log_templates[logID] = template_str
                log_templateids[logID] = template_id
            df_events.append([template_id, template_str, occurrence])

        df_event = pd.DataFrame(df_events, columns=['EventId', 'EventTemplate', 'Occurrences'])
        self.df_log['EventId'] = log_templateids[-self.df_log.shape[0]:]
        self.df_log['EventTemplate'] = log_templates[-self.df_log.shape[0]:]

        if self.keep_para:
            self.df_log["ParameterList"] = self.df_log.apply(self.get_parameter_list, axis=1)
        self.df_log.to_csv(os.path.join(self.savePath, self.logName + '_structured.csv'), index=False)


        templates_series = pd.Series(log_templates)
        occ_dict = dict(templates_series.value_counts())
        df_event = pd.DataFrame()
        df_event['EventTemplate'] = templates_series.unique()
        df_event['EventId'] = df_event['EventTemplate'].map(lambda x: hashlib.md5(x.encode('utf-8')).hexdigest()[0:8])
        df_event['Occurrences'] = df_event['EventTemplate'].map(occ_dict)
        df_event.to_csv(os.path.join(self.savePath, self.logName + '_templates.csv'), index=False,
                        columns=["EventId", "EventTemplate", "Occurrences"])

        return len(log_templates)

    def printTree(self, node, dep):
        pStr = ''   
        for i in range(dep):
            pStr += '\t'

        if node.depth == 0:
            pStr += 'Root'
        elif node.depth == 1:
            pStr += '<' + str(node.digitOrtoken) + '>'
        else:
            pStr += node.digitOrtoken

        print(pStr)

        if node.depth == self.depth:
            return 1
        for child in node.childD:
            self.printTree(node.childD[child], dep+1)


    def parse(self, logName):
        print('Parsing file: ' + os.path.join(self.path, logName))
        start_time = datetime.now()
        self.logName = logName

        if self.resume_training:
            hm = HistoryManager(history=self.history)
            hm.import_history(self.history)
            rootNode = hm.rootNode
            logCluL = hm.logCluL
        else:
            rootNode = Node()
            logCluL = []
            hm = HistoryManager(rootNode=rootNode, logCluL=logCluL)

        self.load_data()

        count = 0
        last_line = hm.lastLineCount
        for idx, line in self.df_log.iterrows():
            logID = line['LineId'] + last_line
            logmessageL = self.preprocess(line['Content']).strip().split()
            # logmessageL = filter(lambda x: x != '', re.split('[\s=:,]', self.preprocess(line['Content'])))
            matchCluster = self.treeSearch(rootNode, logmessageL)

            #Match no existing log cluster
            if matchCluster is None:
                newCluster = Logcluster(logTemplate=logmessageL, logIDL=[logID])
                logCluL.append(newCluster)
                self.addSeqToPrefixTree(rootNode, newCluster)

            #Add the new log message to the existing cluster
            else:
                newTemplate = self.getTemplate(logmessageL, matchCluster.logTemplate)
                matchCluster.logIDL.append(logID)
                if ' '.join(newTemplate) != ' '.join(matchCluster.logTemplate): 
                    matchCluster.logTemplate = newTemplate

            count += 1
            if count % 1000 == 0 or count == len(self.df_log):
                print('Proscessed {0:.1f}% of log lines.'.format(count * 100.0 / len(self.df_log)))

        if not self.resume_training:
            last_line_count = self.outputResult(logCluL)
        else:
            last_line_count = self.outputResult(logCluL, hm.lastLineCount)

        hm.lastLineCount = last_line_count
        hm.export_history(self.history, force=not self.resume_training)

        print('Parsing done. [Time taken: {!s}]'.format(datetime.now() - start_time))

    def load_data(self):
        headers, regex = self.generate_logformat_regex(self.log_format)
        self.df_log = self.log_to_dataframe(os.path.join(self.path, self.logName), regex, headers, self.log_format)

    def preprocess(self, line):
        for currentRex in self.rex:
            line = re.sub(currentRex, '<*>', line)
        return line

    def log_to_dataframe(self, log_file, regex, headers, logformat):
        """ Function to transform log file to dataframe 
        """
        log_messages = []
        linecount = 0
        with open(log_file, 'r') as fin:
            for line in fin.readlines():
                try:
                    match = regex.search(line.strip())
                    message = [match.group(header) for header in headers]
                    log_messages.append(message)
                    linecount += 1
                except Exception as e:
                    pass
        logdf = pd.DataFrame(log_messages, columns=headers)
        logdf.insert(0, 'LineId', None)
        logdf['LineId'] = [i + 1 for i in range(linecount)]
        return logdf

    def generate_logformat_regex(self, logformat):
        """ Function to generate regular expression to split log messages
        """
        headers = []
        splitters = re.split(r'(<[^<>]+>)', logformat)
        regex = ''
        for k in range(len(splitters)):
            if k % 2 == 0:
                splitter = re.sub(' +', '\\\s+', splitters[k])
                regex += splitter
            else:
                header = splitters[k].strip('<').strip('>')
                regex += '(?P<%s>.*?)' % header
                headers.append(header)
        regex = re.compile('^' + regex + '$')
        return headers, regex

    def get_parameter_list(self, row):
        template_regex = re.sub(r"<.{1,5}>", "<*>", row["EventTemplate"])
        if "<*>" not in template_regex: return []
        template_regex = re.sub(r'([^A-Za-z0-9])', r'\\\1', template_regex)
        template_regex = re.sub(r'\\ +', r'\s+', template_regex)
        template_regex = "^" + template_regex.replace("\<\*\>", "(.*?)") + "$"
        parameter_list = re.findall(template_regex, row["Content"])
        parameter_list = parameter_list[0] if parameter_list else ()
        parameter_list = list(parameter_list) if isinstance(parameter_list, tuple) else [parameter_list]
        return parameter_list