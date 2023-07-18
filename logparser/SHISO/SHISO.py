# =========================================================================
# Copyright (C) 2016-2023 LOGPAI (https://github.com/logpai).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =========================================================================

from queue import *
import regex as re
import os
from nltk import ngrams
import numpy as np
import pandas as pd
import hashlib
from datetime import datetime
from tqdm import tqdm


class Node:
    def __init__(self, format="", logIDL=None, childL=None):
        self.format = format
        if logIDL is None:
            logIDL = []
        if childL is None:
            childL = []
        self.logIDL = logIDL
        self.childL = childL


class LogParser:
    def __init__(
        self,
        log_format,
        formatTable=None,
        indir="./",
        outdir="./results/",
        maxChildNum=4,
        mergeThreshold=0.1,
        formatLookupThreshold=0.3,
        superFormatThreshold=0.85,
        rex=[],
    ):
        """
        Attributes
        ----------
        path : the path of the input file
        logname : the file name of the input file
        savePath :the path of the output file
        maxChildNum : maximum number allowed for the tree
        mergeThreshold : used to search the most similar template in the children
        formatLookupThreshold : lowerbound to find the most similar node to Adjust
        superFormatThreshold : threshold compared with float(lcsLen)/averageLen, whether merge or not
        """
        self.path = indir
        self.logname = None
        self.logformat = log_format
        self.savePath = outdir
        self.maxChildNum = maxChildNum
        self.mergeThreshold = mergeThreshold
        self.formatLookupThreshold = formatLookupThreshold
        self.superFormatThreshold = superFormatThreshold
        self.rex = rex

        if formatTable is None:
            formatTable = dict()
        self.formatTable = formatTable

    def Format(self, seq1, seq2):
        assert len(seq1) == len(seq2)
        retVal = []

        i = 0
        for word in seq1:
            if word == seq2[i]:
                retVal.append(word)
            else:
                retVal.append("*")

            i += 1

        return retVal

    # [lower, upper, digit, other]
    def wordToVect(self, word):
        retVal = [0, 0, 0, 0]
        for c in word:
            if c.islower():
                retVal[0] += 1
            elif c.isupper():
                retVal[1] += 1
            elif c.isdigit():
                retVal[2] += 1
            else:
                retVal[3] += 1

        if all(i == 0 for i in retVal):
            return retVal

        retVal = np.array(retVal)

        # Euclidean distance
        retVal = retVal / np.linalg.norm(retVal)

        return retVal

    def wordDist(self, word1, word2):
        if word1 == "*" or word2 == "*":
            return 0.0
        return np.linalg.norm(self.wordToVect(word1) - self.wordToVect(word2))

    # If their length is not equal, make their distance 1.00, instead of 0.0 in the paper.
    def SeqRatio(self, seq1, seq2):
        retVal = 0

        if len(seq1) != len(seq2):
            return 1.0

        i = 0
        numerator = 0
        for word1 in seq1:
            word2 = seq2[i]
            numerator += self.wordDist(word1, word2)
            i += 1

        return float(numerator) / (2 * len(seq1))

    def Sim(self, seq1, seq2):
        if len(seq1) == len(seq2):
            return self.SeqRatio(seq1, seq2)

        if len(seq1) > len(seq2):
            largeSeq = seq1
            smallSeq = seq2
        else:
            largeSeq = seq2
            smallSeq = seq1

        i = 0
        numerator = 0
        for word1 in smallSeq:
            word2 = largeSeq[i]
            numerator += self.wordDist(word1, word2)
            i += 1

        for idx in range(i, len(largeSeq)):
            word2 = largeSeq[i]
            numerator += self.wordDist("", word2)

        return float(numerator) / (2 * len(largeSeq))

    def LCS(self, seq1, seq2):
        lengths = [[0 for j in range(len(seq2) + 1)] for i in range(len(seq1) + 1)]
        # row 0 and column 0 are initialized to 0 already
        for i in range(len(seq1)):
            for j in range(len(seq2)):
                if seq1[i] == seq2[j]:
                    lengths[i + 1][j + 1] = lengths[i][j] + 1
                else:
                    lengths[i + 1][j + 1] = max(lengths[i + 1][j], lengths[i][j + 1])

        # read the substring out from the matrix
        result = []
        lenOfSeq1, lenOfSeq2 = len(seq1), len(seq2)
        while lenOfSeq1 != 0 and lenOfSeq2 != 0:
            if lengths[lenOfSeq1][lenOfSeq2] == lengths[lenOfSeq1 - 1][lenOfSeq2]:
                lenOfSeq1 -= 1
            elif lengths[lenOfSeq1][lenOfSeq2] == lengths[lenOfSeq1][lenOfSeq2 - 1]:
                lenOfSeq2 -= 1
            else:
                assert seq1[lenOfSeq1 - 1] == seq2[lenOfSeq2 - 1]
                result.insert(0, seq1[lenOfSeq1 - 1])
                lenOfSeq1 -= 1
                lenOfSeq2 -= 1
        return result

    def SuperFormat(self, seq1, seq2):
        lcs = self.LCS(seq1, seq2)
        lcsLen = len(lcs)
        averageLen = (len(seq1) + len(seq2)) / 2.0
        if float(lcsLen) / averageLen > self.superFormatThreshold:
            return lcs
        else:
            return []

    def Search(self, n, nroot):
        f = []
        newFormat = False
        nparent = nroot

        # Loop until either find a format node, or create a new format node by itself
        while len(f) == 0:
            dmin = 1.1
            selectNode = None
            selectIdx = -1

            # match with the most similar hit
            currentIdx = 0
            for child in nparent.childL:
                d = self.SeqRatio(n.format, child.format)
                if d <= self.mergeThreshold and d < dmin:
                    dmin = d
                    f = self.Format(n.format, child.format)
                    selectNode = child
                    selectIdx = currentIdx
                currentIdx += 1

            if selectNode is None:
                if len(nparent.childL) < self.maxChildNum:
                    nparent.childL.append(n)
                    f = n.format
                else:
                    nptemp = None
                    r = 1.1
                    for child in nparent.childL:
                        currentSim = self.Sim(n.format, child.format)
                        if r > currentSim:
                            nptemp = child
                            r = currentSim
                    nparent = nptemp
                    assert nparent is not None

            else:
                selectNode.logIDL.append(n.logIDL[0])
                if " ".join(f) != " ".join(selectNode.format):
                    selectNode.format = f
                    newFormat = True

        return (nparent, selectIdx, selectNode, newFormat)

    # Called when the Search funtion generates a new format
    def Adjust(self, pn, nidx, n):
        rmax = 0
        fmax = []
        nodemax = None
        superF = []
        f = n.format
        G = set(ngrams(f, 3))  # trigram: [(w1, w2, w3), (,,), ...]

        # self.formatTable: (ngram, node)
        for currentFormat in self.formatTable:
            simTuple = 0
            (currentG, currentNode) = self.formatTable[currentFormat]
            for g in G:
                if g in currentG:
                    simTuple += 1
            r = 2.0 * simTuple / (len(currentG) + len(G))
            if r > self.formatLookupThreshold and r > rmax:
                rmax = r
                fmax = currentFormat.split()
                nodemax = currentNode

        if len(fmax) != 0:
            superF = self.SuperFormat(f, fmax)
            assert type(superF) == type([])

            # If we need to generate new format
            if len(superF) != 0:
                nodemax.logIDL.extend(n.logIDL)
                nodemax.format = superF
                n.format = ""
                n.logIDL = []

                # Move the children of the deleted Node into the right place
                if len(n.childL) != 0:
                    childNum = len(n.childL)
                    nextP = None
                    for child in n.childL:
                        if self.maxChildNum - len(child.childL) >= childNum - 1:
                            nextP = child
                            break
                    if nextP is not None:
                        for child in n.childL:
                            if child is not nextP:
                                nextP.childL.append(child)
                        pn.childL[nidx] = nextP

                # If the deleted Node does not have children
                else:
                    assert pn.childL[nidx] == n
                    del pn.childL[nidx]

                # New superformat, not in the table
                if " ".join(superF) not in self.formatTable:
                    self.formatTable[" ".join(superF)] = (
                        set(ngrams(superF, 3)),
                        nodemax,
                    )

                # Already exist this superformat in the table. currently brute force make one of the node empty.
                else:
                    self.formatTable[" ".join(superF)][1].logIDL.extend(nodemax.logIDL)
                    nodemax.logIDL = []
                    nodemax.format = ""

    def outputResult(self, node):
        templateNo = 1
        nodeQ = Queue()
        nodeQ.put(node)

        templates = [0] * self.df_log.shape[0]
        ids = [0] * self.df_log.shape[0]
        df_event = []

        while not nodeQ.empty():
            currentNode = nodeQ.get()
            for child in currentNode.childL:
                nodeQ.put(child)
            if len(currentNode.format) == 0:
                continue

            template = " ".join(currentNode.format)
            eid = hashlib.md5(template.encode("utf-8")).hexdigest()[0:8]
            occurence = len(currentNode.logIDL)
            df_event.append([eid, template, occurence])

            for logid in currentNode.logIDL:
                templates[logid - 1] = template
                ids[logid - 1] = eid

        df_event = pd.DataFrame(
            df_event, columns=["EventId", "EventTemplate", "Occurrences"]
        )

        self.df_log["EventId"] = ids
        self.df_log["EventTemplate"] = templates
        self.df_log.to_csv(
            os.path.join(self.savePath, self.logname + "_structured.csv"), index=False
        )
        df_event.to_csv(
            os.path.join(self.savePath, self.logname + "_templates.csv"), index=False
        )

    def printTree(self, node, dep):
        pStr = ""
        for i in range(dep):
            pStr += "\t"

        if len(node.format) == 0:
            pStr += "No format node"
        else:
            pStr += " ".join(node.format)
        # print pStr
        if len(node.childL) == 0:
            return 1
        for child in node.childL:
            self.printTree(child, dep + 1)

    def parse(self, logname):
        print("Parsing file: " + os.path.join(self.path, logname))
        self.logname = logname
        starttime = datetime.now()
        rootNode = Node()
        self.load_data()

        count = 0
        for idx, line in tqdm(self.df_log.iterrows(), total=len(self.df_log)):
            ID = line["LineId"]
            logmessageL = line["Content"]
            if self.rex:
                for currentRex in self.rex:
                    logmessageL = re.sub(currentRex, "<*>", logmessageL)
            logmessageL = logmessageL.strip().split()
            currentNode = Node(format=logmessageL, logIDL=[ID])

            (parentNode, newIdx, newFormNode, hasNewForm) = self.Search(
                n=currentNode, nroot=rootNode
            )

            if hasNewForm:
                self.Adjust(pn=parentNode, nidx=newIdx, n=newFormNode)
            count += 1

        if not os.path.exists(self.savePath):
            os.makedirs(self.savePath)

        self.outputResult(rootNode)
        print("Parsing done. [Time taken: {!s}]".format(datetime.now() - starttime))

    def load_data(self):
        headers, regex = self.generate_logformat_regex(self.logformat)
        self.df_log = self.log_to_dataframe(
            os.path.join(self.path, self.logname), regex, headers, self.logformat
        )

    def log_to_dataframe(self, log_file, regex, headers, logformat):
        """
        Function to transform log file to dataframe
        """
        log_messages = []
        linecount = 0
        with open(log_file, "r") as fin:
            for line in fin.readlines():
                try:
                    match = regex.search(line.strip())
                    message = [match.group(header) for header in headers]
                    log_messages.append(message)
                    linecount += 1
                except Exception as e:
                    print("Skip line: " + line)
        logdf = pd.DataFrame(log_messages, columns=headers)
        logdf.insert(0, "LineId", None)
        logdf["LineId"] = [i + 1 for i in range(linecount)]
        print("log_to_dataframe done!")
        return logdf

    def generate_logformat_regex(self, logformat):
        """
        Function to generate regular expression to split log messages
        """
        headers = []
        splitters = re.split(r"(<[^<>]+>)", logformat)
        regex = ""
        for k in range(len(splitters)):
            if k % 2 == 0:
                splitter = re.sub(" +", "\s+", splitters[k])
                regex += splitter
            else:
                header = splitters[k].strip("<").strip(">")
                regex += "(?P<%s>.*?)" % header
                headers.append(header)
        regex = re.compile("^" + regex + "$")
        return headers, regex
