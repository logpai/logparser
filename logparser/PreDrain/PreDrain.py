"""
Description : This file implements the Drain algorithm for log parsing
Author      : LogPAI team
License     : MIT
"""

import os
from datetime import datetime
from logparser.Drain import Logcluster, Node
import logparser.Drain
from logparser.utils.preprocessing import preprocess

class LogParser(logparser.Drain.LogParser):
    def __init__(self, log_format, estimate=2000, **kwargs):
        """
            estimate: The number of logs used for regex usage estimation
        """
        super().__init__(log_format, **kwargs)
        self.estimate = estimate

    #seq1 is template
    def seqDist(self, seq1, seq2):
        assert len(seq1) == len(seq2)
        simTokens = 0
        numOfPar = 0
        # Add fast return if they are the same
        if seq1 == seq2:
            for t in seq1:
                if t == "<*>": numOfPar += 1
            return 1, numOfPar

        for token1, token2 in zip(seq1, seq2):
            if token1 == '<*>':
                numOfPar += 1
                continue
            if token1 == token2:
                simTokens += 1 

        retVal = float(simTokens) / len(seq1)

        return retVal, numOfPar

    def parse(self, logName):
        print('Parsing file: ' + os.path.join(self.path, logName))
        start_time = datetime.now()
        self.logName = logName
        rootNode = Node()
        logCluL = []

        self.load_data()

        count = 0
        matched_types = []
        use_sequence = []
        for idx, line in self.df_log.iterrows():
            logID = line['LineId']

            # Add preprocess
            if idx < self.estimate:
                logmessageL, sequence, matched = preprocess(line['Content'], estimation_stage=True)
                logmessageL = logmessageL.strip().split()
                matched_types.extend(matched)
                use_sequence = sequence
            else:
                if idx == self.estimate:
                    matched_types = set(matched_types)
                    use_sequence = [i for i in use_sequence if i in matched_types]
                logmessageL = preprocess(line['Content'], estimation_stage=False, use_sequence=use_sequence).strip().split()
            
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
                print('Processed {0:.1f}% of log lines.'.format(count * 100.0 / len(self.df_log)))


        if not os.path.exists(self.savePath):
            os.makedirs(self.savePath)

        self.outputResult(logCluL)

        print('Parsing done. [Time taken: {!s}]'.format(datetime.now() - start_time))
