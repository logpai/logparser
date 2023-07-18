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

from datetime import datetime
import random
import math
import operator
import regex as re
import os
import pandas as pd
import hashlib


class Para:
    def __init__(self, path, rex, savePath, groupNum, logformat):
        self.path = path
        self.rex = rex
        self.savePath = savePath
        self.groupNum = groupNum  # partition into k groups
        self.logformat = logformat


class LogParser:
    def __init__(self, indir, outdir, groupNum, log_format, rex=[], seed=0):
        self.para = Para(
            path=indir,
            rex=rex,
            savePath=outdir,
            groupNum=groupNum,
            logformat=log_format,
        )
        self.wordLL = []
        self.loglineNum = 0
        self.termpairLLT = []
        self.logNumPerGroup = []
        self.groupIndex = dict()  # each line corresponding to which group
        self.termPairLogNumLD = []
        self.logIndexPerGroup = []
        self.seed = seed

    def loadLog(self):
        """Load datasets and use regular expression to split it and remove some columns"""
        print("Loading logs...")
        headers, regex = self.generate_logformat_regex(self.para.logformat)
        self.df_log = self.log_to_dataframe(
            os.path.join(self.para.path, self.logname),
            regex,
            headers,
            self.para.logformat,
        )
        for idx, line in self.df_log.iterrows():
            line = line["Content"]
            if self.para.rex:
                for currentRex in self.para.rex:
                    line = re.sub(currentRex, "", line)

            wordSeq = line.strip().split()
            self.wordLL.append(tuple(wordSeq))

    def termpairGene(self):
        print("Generating term pairs...")
        i = 0
        for wordL in self.wordLL:
            wordLT = []
            for j in range(len(wordL)):
                for k in range(j + 1, len(wordL), 1):
                    if wordL[j] != "[$]" and wordL[k] != "[$]":
                        termpair = (wordL[j], wordL[k])
                        wordLT.append(termpair)
            self.termpairLLT.append(wordLT)
            i += 1

        # termPairLogNumLD, used to account the occurrence of each termpair of each group
        for i in range(self.para.groupNum):
            newDict = dict()
            self.termPairLogNumLD.append(newDict)
            # initialize the item value to zero
            self.logNumPerGroup.append(0)

        # divide logs into initial groupNum groups randomly, the group number of each log is stored in the groupIndex
        self.loglineNum = len(self.wordLL)
        random.seed(self.seed)
        for i in range(self.loglineNum):
            ran = random.randint(
                0, self.para.groupNum - 1
            )  # group number from 0 to k-1
            self.groupIndex[i] = ran
            self.logNumPerGroup[ran] += 1  # count the number of loglines per group

        # count the frequency of each termpairs per group
        i = 0
        for termpairLT in self.termpairLLT:
            j = 0
            for key in termpairLT:
                currGroupIndex = self.groupIndex[i]
                if key not in self.termPairLogNumLD[currGroupIndex]:
                    self.termPairLogNumLD[currGroupIndex][key] = 1
                else:
                    self.termPairLogNumLD[currGroupIndex][key] += 1
                j += 1
            i += 1

    def LogMessParti(self):
        """
        Use local search, for each log, find the group that it should be moved to.
        in this process, termpairs occurange should also make some changes and logNumber
        of corresponding should be changed
        """
        print("Log message partitioning...")
        changed = True
        while changed:
            changed = False
            i = 0
            for termpairLT in self.termpairLLT:
                curGroup = self.groupIndex[i]
                alterGroup = potenFunc(
                    curGroup,
                    self.termPairLogNumLD,
                    self.logNumPerGroup,
                    i,
                    termpairLT,
                    self.para.groupNum,
                )
                if curGroup != alterGroup:
                    changed = True
                    self.groupIndex[i] = alterGroup
                    # update the dictionary of each group
                    for key in termpairLT:
                        # minus 1 from the current group count on this key
                        self.termPairLogNumLD[curGroup][key] -= 1
                        if self.termPairLogNumLD[curGroup][key] == 0:
                            del self.termPairLogNumLD[curGroup][key]
                        # add 1 to the alter group
                        if key not in self.termPairLogNumLD[alterGroup]:
                            self.termPairLogNumLD[alterGroup][key] = 1
                        else:
                            self.termPairLogNumLD[alterGroup][key] += 1
                    self.logNumPerGroup[curGroup] -= 1
                    self.logNumPerGroup[alterGroup] += 1
                i += 1

    def signatConstr(self):
        """
        Calculate the occurancy of each word of each group, and for each group, save the words that
        happen more than half all log number to be candidateTerms(list of dict, words:frequency),
        """
        print("Log message signature construction...")
        # create the folder to save the resulted templates
        if not os.path.exists(self.para.savePath):
            os.makedirs(self.para.savePath)

        wordFreqPerGroup = []
        candidateTerm = []
        candidateSeq = []
        self.signature = []

        # save the all the log indexs of each group: logIndexPerGroup
        for t in range(self.para.groupNum):
            dic = dict()
            newlogIndex = []
            newCandidate = dict()
            wordFreqPerGroup.append(dic)
            self.logIndexPerGroup.append(newlogIndex)
            candidateSeq.append(newCandidate)

        # count the occurence of each word of each log per group
        # and save into the wordFreqPerGroup, which is a list of dictionary,
        # where each dictionary represents a group, key is the word, value is the occurence
        lineNo = 0
        for wordL in self.wordLL:
            groupIndex = self.groupIndex[lineNo]
            self.logIndexPerGroup[groupIndex].append(lineNo)
            for key in wordL:
                if key not in wordFreqPerGroup[groupIndex]:
                    wordFreqPerGroup[groupIndex][key] = 1
                else:
                    wordFreqPerGroup[groupIndex][key] += 1
            lineNo += 1

        # calculate the halfLogNum and select those words whose occurence is larger than halfLogNum
        # as constant part and save into candidateTerm
        for i in range(self.para.groupNum):
            halfLogNum = math.ceil(self.logNumPerGroup[i] / 2.0)
            dic = dict(
                (k, v) for k, v in wordFreqPerGroup[i].items() if v >= halfLogNum
            )
            candidateTerm.append(dic)

        # scan each logline's each word that also is a part of candidateTerm, put these words together
        # as a new candidate sequence, thus, each raw log will have a corresponding candidate sequence
        # and count the occurence of these candidate sequence of each group and select the most frequent
        # candidate sequence as the signature, i.e. the templates
        lineNo = 0
        for wordL in self.wordLL:
            curGroup = self.groupIndex[lineNo]
            newCandiSeq = []

            for key in wordL:
                if key in candidateTerm[curGroup]:
                    newCandiSeq.append(key)

            keySeq = tuple(newCandiSeq)
            if keySeq not in candidateSeq[curGroup]:
                candidateSeq[curGroup][keySeq] = 1
            else:
                candidateSeq[curGroup][keySeq] += 1
            lineNo += 1

        for i in range(self.para.groupNum):
            if len(candidateSeq[i]) > 0:
                sig = max(candidateSeq[i].items(), key=operator.itemgetter(1))[0]
            else:
                sig = ""
            self.signature.append(sig)

    def writeResultToFile(self):
        idx_eventID = {}
        for idx, item in enumerate(self.signature):
            eventStr = " ".join(item)
            idx_eventID[idx] = hashlib.md5(eventStr.encode("utf-8")).hexdigest()[0:8]

        EventId = []
        EventTemplate = []
        LineId_groupId = []
        for idx, item in enumerate(self.logIndexPerGroup):
            for LineId in item:
                LineId_groupId.append([LineId, idx])
        LineId_groupId.sort(key=lambda x: x[0])
        for item in LineId_groupId:
            GroupID = item[1]
            EventId.append(idx_eventID[GroupID])
            EventTemplate.append(" ".join(self.signature[GroupID]))

        self.df_log["EventId"] = EventId
        self.df_log["EventTemplate"] = EventTemplate
        self.df_log.to_csv(
            os.path.join(self.para.savePath, self.logname + "_structured.csv"),
            index=False,
        )

        occ_dict = dict(self.df_log["EventTemplate"].value_counts())
        df_event = pd.DataFrame()
        df_event["EventTemplate"] = self.df_log["EventTemplate"].unique()
        df_event["EventId"] = df_event["EventTemplate"].map(
            lambda x: hashlib.md5(x.encode("utf-8")).hexdigest()[0:8]
        )
        df_event["Occurrences"] = df_event["EventTemplate"].map(occ_dict)

        df_event.to_csv(
            os.path.join(self.para.savePath, self.logname + "_templates.csv"),
            index=False,
            columns=["EventId", "EventTemplate", "Occurrences"],
        )

    def log_to_dataframe(self, log_file, regex, headers, logformat):
        """Function to transform log file to dataframe"""
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

    def parse(self, logname):
        print("Parsing file: " + os.path.join(self.para.path, logname))
        start_time = datetime.now()
        self.logname = logname
        self.loadLog()
        self.termpairGene()
        self.LogMessParti()
        self.signatConstr()
        print("signature constructed.")
        self.writeResultToFile()
        print("Parsing done. [Time taken: {!s}]".format(datetime.now() - start_time))


def potenFunc(curGroupIndex, termPairLogNumLD, logNumPerGroup, lineNum, termpairLT, k):
    maxDeltaD = 0
    maxJ = curGroupIndex
    for i in range(k):
        returnedDeltaD = getDeltaD(
            logNumPerGroup, termPairLogNumLD, curGroupIndex, i, lineNum, termpairLT
        )
        if returnedDeltaD > maxDeltaD:
            maxDeltaD = returnedDeltaD
            maxJ = i
    return maxJ


def getDeltaD(logNumPerGroup, termPairLogNumLD, groupI, groupJ, lineNum, termpairLT):
    """part of the potential function"""
    deltaD = 0
    Ci = logNumPerGroup[groupI]
    Cj = logNumPerGroup[groupJ]
    for r in termpairLT:
        if r in termPairLogNumLD[groupJ]:
            deltaD += pow(((termPairLogNumLD[groupJ][r] + 1) / (Cj + 1.0)), 2) - pow(
                (termPairLogNumLD[groupI][r] / (Ci + 0.0)), 2
            )
        else:
            deltaD += pow((1 / (Cj + 1.0)), 2) - pow(
                (termPairLogNumLD[groupI][r] / (Ci + 0.0)), 2
            )
    deltaD = deltaD * 3
    return deltaD
