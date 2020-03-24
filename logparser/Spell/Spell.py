"""
Description : This file implements the Spell algorithm for log parsing
Author      : LogPAI team
License     : MIT
"""

import sys
import re
import os
import numpy as np
import pandas as pd
import hashlib
from sys import version_info
from datetime import datetime
import string
import pickle


class LCSObject:
    """ Class object to store a log group with the same template
    """
    def __init__(self, logTemplate='', logIDL=[], logParams = {}):
        self.logTemplate = logTemplate
        self.logIDL = logIDL
        self.logParams = logParams


class Node:
    """ A node in prefix tree data structure
    """
    def __init__(self, token='', templateNo=0):
        self.logClust = None
        self.token = token
        self.templateNo = templateNo
        self.childD = dict()


class LogParser:
    """ LogParser class

    Attributes
    ----------
        path : the path of the input file
        logName : the file name of the input file
        savePath : the path of the output file
        tau : how much percentage of tokens matched to merge a log message
    """
    def __init__(self, indir='./', outdir='./result/', log_format=None, tau=0.5, rex=[], keep_para=True):
        self.path = indir
        self.logname = None
        self.savePath = outdir
        self.tau = tau
        self.logformat = log_format
        self.df_log = None
        self.rex = rex
        self.keep_para = keep_para

    def JaccardSimilarity(self, seq1, seq2):
        a = set(seq1)
        b = set(seq2)
        c = a.intersection(b)
        return float(len(c))/ (len(a) + len(b) - len(c))

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
        while lenOfSeq1!=0 and lenOfSeq2 != 0:
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
        for logClust in logClustL:
            if float(len(logClust.logTemplate)) < 0.5 * len(seq):
                continue
            # Check the template is a subsequence of seq 
            #(we use set checking as a proxy here for speedup since incorrect-ordering bad cases rarely occur in logs)
            token_set = set(seq)
            if all(token in token_set or token == '<*>' for token in logClust.logTemplate):
                return logClust
        return None

    def PrefixTreeMatch(self, parentn, seq, idx):
        retLogClust = None
        length = len(seq)
        for i in range(idx, length):
            if seq[i] in parentn.childD:
                childn = parentn.childD[seq[i]]
                if (childn.logClust is not None):
                    constLM = [w for w in childn.logClust.logTemplate if w != '<*>']
                    if float(len(constLM)) >= self.tau * length:
                        return childn.logClust
                else:
                    return self.PrefixTreeMatch(childn, seq, i + 1)

        return retLogClust

    def LCSMatch(self, logClustL, seq):
        retLogClust = None

        maxLen = -1
        #maxlcs = []
        
        maxClust = None
        set_seq = set(seq)
        size_seq = len(seq)

        for logClust in logClustL:
            set_template = set(logClust.logTemplate)
            if len(set_seq & set_template) < 0.5 * size_seq:
                continue
            if self.JaccardSimilarity(seq, logClust.logTemplate) < self.tau: 
                continue
            lcs = self.LCS(seq, logClust.logTemplate)
            if len(lcs) > maxLen or (len(lcs) == maxLen and len(logClust.logTemplate) < len(maxClust.logTemplate)):
                maxLen = len(lcs)
                #maxlcs = lcs
                maxClust = logClust

        # LCS should be large then tau * len(itself)
        if float(maxLen) >= self.tau * size_seq:
            retLogClust = maxClust

        return retLogClust

    def getTemplate(self, lcs, seq, params):
        retVal = []
        
#         print("seq", seq)
#         print("lcs", lcs)
        if not lcs: return retVal
        lcs = lcs[::-1]
        i = 0
        for token in seq:
#             print("ret", retVal)
            i += 1
            if token == lcs[-1]:
                retVal.append(token)
                lcs.pop()
            else:
                retVal.append('<*>')
            if not lcs:
                break
        if i < len(seq):
            retVal.append('<*>')
        return retVal

    def addSeqToPrefixTree(self, rootn, newCluster):
        parentn = rootn
        seq = newCluster.logTemplate
        seq = [w for w in seq if w != '<*>']

        for i in range(len(seq)):
            tokenInSeq = seq[i]
            # Match
            if tokenInSeq in parentn.childD:
                parentn.childD[tokenInSeq].templateNo += 1                  
            # Do not Match
            else:
                parentn.childD[tokenInSeq] = Node(token=tokenInSeq, templateNo=1)
            parentn = parentn.childD[tokenInSeq]

        if parentn.logClust is None:
            parentn.logClust = newCluster

    def removeSeqFromPrefixTree(self, rootn, newCluster):
        parentn = rootn
        seq = newCluster.logTemplate
        seq = [w for w in seq if w != '<*>']

        for tokenInSeq in seq:
            if tokenInSeq in parentn.childD:
                matchedNode = parentn.childD[tokenInSeq]
                if matchedNode.templateNo == 1:
                    del parentn.childD[tokenInSeq]
                    break
                else:
                    matchedNode.templateNo -= 1
                    parentn = matchedNode

    def outputResult(self, logClustL, rootNode):
        
        templates = [0] * self.df_log.shape[0]
        ids = [0] * self.df_log.shape[0]
        df_event = []
        eid = 0
        for logclust in logClustL:
            template_str = ' '.join(logclust.logTemplate)
            #eid = hashlib.md5(template_str.encode('utf-8')).hexdigest()[0:8]
            eid += 1
            for logid in logclust.logIDL:
                templates[logid - 1] = template_str
                ids[logid - 1] = eid
            df_event.append([eid, template_str, len(logclust.logIDL)])

        df_event = pd.DataFrame(df_event, columns=['Log Key', 'Message', 'Occurrences'])
        df_event = df_event.sort_values(by=['Occurrences'], ascending = False)

        self.df_log['Log Key'] = ids
        self.df_log['Message'] = templates
        if self.keep_para:
            self.df_log["ParameterList"] = self.df_log.apply(self.get_parameter_list, axis=1) 

        np.savetxt(r'Spell_result/np.txt', self.df_log['Log Key'].values, fmt='%d', newline=' ')
        self.df_log.to_csv(os.path.join(self.savePath, 'logs_structured.csv'), index=False)
        df_event.to_csv(os.path.join(self.savePath, 'logs_templates.csv'), index=False)
        
        with open('Spell_result/LCSObject.plk', 'wb') as LCSObject_file:
            pickle.dump(logClustL, LCSObject_file)
        with open('Spell_result/Tree.plk', 'wb') as Tree_file:
            pickle.dump(rootNode, Tree_file)

    def printTree(self, node, dep):
        pStr = ''   
        for _ in range(dep):
            pStr += '\t'

        if node.token == '':
            pStr += 'Root'
        else:
            pStr += node.token
            if node.logClust is not None:
                pStr += '-->' + ' '.join(node.logClust.logTemplate)
        print(pStr + ' ('+ str(node.templateNo) + ')')

        for child in node.childD:
            self.printTree(node.childD[child], dep + 1)

    def LCSsearch(self, logCluL, constLogMessL, logmessageL, rootNode, idx):
        matchCluster = self.PrefixTreeMatch(rootNode, constLogMessL, idx)
        
        if matchCluster is None:
            matchCluster = self.SimpleLoopMatch(logCluL, constLogMessL)
            
            if matchCluster is None:
                matchCluster = self.LCSMatch(logCluL, logmessageL)
        
        return matchCluster
        
    def parse(self, logname):
        starttime = datetime.now()  
        self.logname = logname  
        self.load_data()
        rootNode = Node()
        logCluL = []
        
#         with open('Spell_result/Tree.plk', 'rb') as Tree_file:
#             rootNode = pickle.load(Tree_file)
#         with open('Spell_result/LCSObject.plk', 'rb') as LCSObject_file:
#             logCluL = pickle.load(LCSObject_file)
        
        count = 0
        
        for _, line in self.df_log.iterrows():
            logID = line['LineId']
            logmessageL = list(filter(lambda x: x != '', re.split(r'[\s=:,()]', self.preprocess(line['Content']))))
            constLogMessL = [w for w in logmessageL if w != '<*>']
            matchCluster = self.LCSsearch(logCluL, constLogMessL, logmessageL, rootNode, 0)

            # Match no existing log cluster
            if matchCluster is None:
                newCluster = LCSObject(logTemplate=logmessageL, logIDL=[logID])
                logCluL.append(newCluster)
                self.addSeqToPrefixTree(rootNode, newCluster)
            #Add the new log message to the existing cluster
            else:
                newTemplate = self.getTemplate(self.LCS(logmessageL, matchCluster.logTemplate), matchCluster.logTemplate, matchCluster.logParams)
                if ' '.join(newTemplate) != ' '.join(matchCluster.logTemplate): 
                    self.removeSeqFromPrefixTree(rootNode, matchCluster)
                    matchCluster.logTemplate = newTemplate
                    self.addSeqToPrefixTree(rootNode, matchCluster)
            if matchCluster:
                matchCluster.logIDL.append(logID)
            count += 1
            if count % 50000 == 0 or count == len(self.df_log):
                print('Processed {0:.1f}% of log lines.'.format(count * 100.0 / len(self.df_log)))
        
        if not os.path.exists(self.savePath):
            os.makedirs(self.savePath)
        self.outputResult(logCluL, rootNode)
        print('Parsing done. [Time taken: {!s}]'.format(datetime.now() - starttime))

    def load_data(self):
        headers, regex = self.generate_logformat_regex(self.logformat)
        if isinstance(self.logname, list):
            self.df_log = self.log_to_dataframe(self.logname, regex, headers, self.logformat)
        else:
            self.df_log = self.log_to_dataframe(os.path.join(self.path, self.logname), regex, headers, self.logformat)
            
    def preprocess(self, line):
        for currentRex in self.rex:
            line = re.sub(currentRex, '<*>', line)
        return line

    def log_to_dataframe(self, log_file, regex, headers, logformat):
        """ Function to transform log file to dataframe 
        """
        log_messages = []
        linecount = 0

        if isinstance(log_file, list):
            log_file = self.sort_logs(log_file)
            for line in log_file:
                line = re.sub(r'[^\x00-\x7F]+', '<NASCII>', line)
                line = re.sub(' +', ' ', line)
                try:
                    match = regex.search(line.strip())
                    message = [match.group(header) for header in headers]
                    log_messages.append(message)
                    linecount += 1
                #except Exception as e:
                except:
                    pass
        else:
            with open(log_file, 'r') as fin:
                for line in fin.readlines():
                    if ".pcap" not in line:
                        line = re.sub(r'[^\x00-\x7F]+', '<NASCII>', line)
                        line = re.sub(' +', ' ', line)
                        try:
                            match = regex.search(line.strip())
                            message = [match.group(header) for header in headers]           

                            if len(message[-1].split()) > 18: continue

                            log_messages.append(message)
                            linecount += 1
                        #except Exception as e:
                        except:
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
                if version_info.major == 2:#for Python 2 
                    splitter = re.sub(' +', r'\s+', splitters[k])
                else:
                    splitter = re.sub(r'\s+', ' ', splitters[k])
                regex += splitter
            else:
                header = splitters[k].strip('<').strip('>')
                regex += '(?P<%s>.*?)' % header
                headers.append(header)
        regex = re.compile('^' + regex + '$')
        return headers, regex

    def get_parameter_list(self, row):
        template_regex = re.sub(r"\s<.{1,5}>\s", "<*>", row["Message"])
        if "<*>" not in template_regex: return []
        
        template_regex = re.sub(r'([^A-Za-z0-9])', r'\\\1', template_regex)
        template_regex = re.sub(r'\\ +', r'[^A-Za-z0-9]+', template_regex)
        template_regex = "^" + template_regex.replace("\<\*\>", "(.*?)") + "$"
        
        parameter_list = re.findall(template_regex, row["Content"])
        parameter_list = parameter_list[0] if parameter_list else ()
        parameter_list = list(parameter_list) if isinstance(parameter_list, tuple) else [parameter_list]
        parameter_list = [para.strip(string.punctuation).strip(' ') for para in parameter_list]
        
        return parameter_list

    def sort_logs(self, log_file):
        dates =[log.split()[0] + " " + log.split()[1] + " " + log.split()[2] for log in log_file]
        messages =[" ".join(log.split()[3:]) for log in log_file ]
        
        #Convert to data frame
        df = pd.DataFrame(zip(dates,messages), columns = ['Date', 'Message'])
        
        #Sort logs by date
        df = df.sort_values(by='Date')

        #Re-merge into single log
        df = df['Date'].astype(str)+' '+df['Message']
        log_list = df.values.tolist()
        return log_list