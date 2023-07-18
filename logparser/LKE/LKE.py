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

import math
from datetime import datetime
import regex as re
import os
import sys
import pandas as pd
import hashlib
import numpy as np

SAVEDISTANCE = True


class Para:
    def __init__(self, path, split_threshold, rex, savePath, logformat):
        self.path = path
        self.split_threshold = split_threshold
        self.rex = rex
        self.savePath = savePath
        self.logformat = logformat


class LogParser:
    def __init__(
        self,
        log_format,
        indir="../logs/",
        outdir="./results/",
        split_threshold=4,
        rex=[],
        seed=1,
    ):
        self.para = Para(
            path=indir,
            split_threshold=split_threshold,
            rex=rex,
            savePath=outdir,
            logformat=log_format,
        )
        self.wordLL = []
        self.wordLen = []
        self.groups = (
            []
        )  # the list of list of words list, each group->each log lines->each words
        self.loglineNumPerGroup = []  # how many lines in each groups
        self.wordLenPerGroup = []  # maximum word positions in one group
        self.wordOccuOfPosiLLD = (
            []
        )  # each word in each position in each group occurrence/frequency
        self.loglinesOfGroups = []
        self.flatLogLineGroups = []
        self.newGroups = []
        self.dedup_lines = []
        self.templates = []
        self.seed = seed  # Random seed for kmeans clustering

    def preprocess(self, x):
        for currentRex in self.para.rex:
            x = re.sub(currentRex, "", x)
        return x

    def paraErasing(self):
        print("=== Step 1: Erasing parameters ===")
        headers, regex = self.generate_logformat_regex(self.para.logformat)
        self.df_log = self.log_to_dataframe(
            os.path.join(self.para.path, self.logname),
            regex,
            headers,
            self.para.logformat,
        )

        self.dedup_lines = self.df_log["Content"].map(self.preprocess)
        for line in self.dedup_lines:
            wordSeq = line.strip().split()
            self.wordLen.append(len(wordSeq))
            self.wordLL.append(tuple(wordSeq))

        if not os.path.exists(self.para.savePath):
            os.makedirs(self.para.savePath)

    def clustering(self):
        sys.setrecursionlimit(100000000)  # set the recursion limits number
        v = math.floor(sum(self.wordLen) / len(self.wordLen))
        print("the parameter v is: %d" % (v))
        logNum = len(self.wordLen)
        print("there are %d loglines" % (logNum))
        # In order to save time, load distArraydata, if exist, do not calculate the edit distance again:
        if (
            os.path.exists(self.para.savePath + self.logname + "editDistance.csv")
            and SAVEDISTANCE
        ):
            print("Loading distance matrix from cache..")
            distMat = np.genfromtxt(
                self.para.savePath + self.logname + "editDistance.csv", delimiter=","
            )
            distList = np.genfromtxt(
                self.para.savePath + self.logname + "distArray.csv", delimiter=","
            )
        else:
            print("calculating distance....")
            path = self.para.savePath + self.logname
            distMat, distList = calDistance(self.wordLL, v, path)
        distArray = np.array(distList)
        threshold1 = self.GetkMeansThreshold(distArray)
        print("the threshold1 is: %s" % (threshold1))

        # connect two loglines with distance < threshold, logDict is a dictionary
        # where the key is line num while
        logDict = {}
        for i in range(logNum):
            logLineSet = set()
            for j in range(i + 1, logNum):
                if distMat[i, j] < threshold1:
                    logLineSet.add(j)
            logDict[i] = logLineSet

        # use DFS to get the initial group.
        flag = np.zeros(
            (logNum, 1)
        )  # used to label whether line has been visited, 0 represents not visited
        for key in logDict:
            if flag[key] == 1:
                continue
            groupLoglist = []
            groupLoglist.append(
                key
            )  # add the key of dict into the list firstly, and then add others
            flag[key] = 1  # line is visited
            dfsTraversal(key, logDict, flag, groupLoglist)
            self.loglinesOfGroups.append(groupLoglist)
            self.loglineNumPerGroup.append(len(groupLoglist))

        print("================get the initial groups splitting=============")
        wordLenArray = np.array(self.wordLen)
        for row in self.loglinesOfGroups:
            eachLineLogList = []
            self.wordLenPerGroup.append(max(wordLenArray[row]))
            for colu in row:
                eachLineLogList.append(self.wordLL[colu])
            self.groups.append(eachLineLogList)
        print("there are %s groups" % (len(self.wordLenPerGroup)))

    def GetkMeansThreshold(self, distArray):
        """k-means where k equals 2 to divide the edit distance into two groups"""
        print("kMeans calculation...")
        distArraySize = len(distArray)
        # random choose two centroids
        minValue = min(distArray)
        centroids = np.zeros((2, 1))
        rangeValue = float(max(distArray) - minValue)
        # np.random.seed(self.seed)
        centroids[:] = np.random.rand(2, 1) * rangeValue + minValue
        maxInnerDist = np.zeros((2, 1))
        clusterChanged = True
        clusterAssment = np.zeros((distArraySize, 1))
        while clusterChanged:
            clusterChanged = False
            for i in range(distArraySize):
                minIndex = -1
                if math.fabs(distArray[i] - centroids[0]) < math.fabs(
                    distArray[i] - centroids[1]
                ):
                    minIndex = 0
                else:
                    minIndex = 1
                if clusterAssment[i] != minIndex:
                    clusterChanged = True
                clusterAssment[i] = minIndex
            for cent in range(2):
                indexs = np.where(clusterAssment == cent)[0]
                disInClust = distArray[indexs]
                maxInnerDist[cent] = min(disInClust)
                centroids[cent] = np.mean(disInClust, axis=0)
        return max(maxInnerDist)

    def splitting(self):
        """split the current group recursively."""
        print("splitting into different groups...")
        print("the split_threshold is %d" % (self.para.split_threshold))
        groupNum = len(self.groups)  # how many groups initially
        for i in range(groupNum):
            splitEachGroup(
                self.groups[i], self.para.split_threshold, self.loglinesOfGroups[i]
            )

        # to flat the list of list of list to list of many lists, that is only one layer lists nested
        mergeLists(self.groups, self.newGroups)
        mergeLists(self.loglinesOfGroups, self.flatLogLineGroups)
        print("Merge the lists together...")
        print("there are %s different groups" % (len(self.flatLogLineGroups)))

    def extracting(self):
        """extract the templates according to the logs in each group"""
        for i in range(len(self.flatLogLineGroups)):
            groupLen = len(self.flatLogLineGroups[i])
            eachGroup = self.newGroups[i]
            if groupLen == 1:
                self.templates.append(eachGroup[0])
            else:
                commonPart = LCS(eachGroup[0], eachGroup[1])
                for k in range(2, groupLen):
                    if not comExit(commonPart, eachGroup[k]):
                        commonPart = LCS(commonPart, eachGroup[k])
                        if len(commonPart) == 0:
                            print("there is no common part in this group")
                            commonPart = ["<*>"]
                            break
                self.templates.append(commonPart)

    def writeResultToFile(self):
        """save to logs in groups into different template txt"""
        content_event = {}
        for idx, item in enumerate(self.flatLogLineGroups):
            for LineId in item:
                content = self.dedup_lines[LineId]
                template = " ".join(self.templates[idx])
                if template:
                    content_event[content] = template

        Templates = []
        for idx, line in self.df_log.iterrows():
            processed = self.preprocess(line["Content"])
            Templates.append(
                content_event[processed]
                if processed in content_event
                else line["Content"]
            )

        self.df_log["EventTemplate"] = Templates
        self.df_log["EventId"] = self.df_log["EventTemplate"].map(
            lambda x: hashlib.md5(x.encode("utf-8")).hexdigest()[0:8]
        )
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

        if not SAVEDISTANCE:
            os.remove(self.para.savePath + self.logname + "editDistance.csv")
            os.remove(self.para.savePath + self.logname + "distArray.csv")

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
        starttime = datetime.now()
        print("Parsing file: " + os.path.join(self.para.path, logname))
        self.logname = logname
        self.paraErasing()
        self.clustering()
        self.splitting()
        self.extracting()
        self.writeResultToFile()
        print("Parsing done. [Time taken: {!s}]".format(datetime.now() - starttime))


# merge the list of lists(many layer) into one list of list
def mergeLists(initGroup, flatLogLineGroups):
    for i in range(len(initGroup)):
        if not listContained(initGroup[i]):
            flatLogLineGroups.append(initGroup[i])
        else:
            mergeLists(initGroup[i], flatLogLineGroups)


def listContained(group):
    """find out whether a list contained a list"""
    for i in range(len(group)):
        if type(group[i]) == list:
            return True
    return False


def splitEachGroup(eachGroup, split_threshold, loglinesEachGroup):
    """
    for each group, According to the splittable and groupLen, decide whether to split
    it iteratively until it cannot be splitted any more
    """
    groupLen = len(eachGroup)
    if groupLen <= 1:
        return
    returnValues = posiToSplit(eachGroup, split_threshold)
    splittable = returnValues["splittable"]
    if splittable == "yes":
        diffwords = returnValues["diffWordList"]
        posi = returnValues["minIndex"]
        conOrParaDivi = returnValues["conOrParaDivi"]
        # print('the different words are:',diffwords)
        # each item in the diffwords corresponds to a group
        for k in range(len(diffwords)):
            newgroups = []
            newloglineGroup = []
            for t in range(groupLen):  # each line in a group
                if len(conOrParaDivi[t]) < posi + 1:
                    newgroups.append(eachGroup[t])
                    newloglineGroup.append(loglinesEachGroup[t])
                    break
                if conOrParaDivi[t][posi] == diffwords[k]:
                    newgroups.append(eachGroup[t])
                    newloglineGroup.append(loglinesEachGroup[t])

            eachGroup.append(newgroups)
            loglinesEachGroup.append(newloglineGroup)
        for t in range(groupLen):
            eachGroup.pop(0)
            loglinesEachGroup.pop(0)
        for i in range(len(diffwords)):
            splitEachGroup(eachGroup[i], split_threshold, loglinesEachGroup[i])


def deleteAllFiles(dirPath):
    fileList = os.listdir(dirPath)
    for fileName in fileList:
        os.remove(dirPath + "/" + fileName)


def posiToSplit(eachGroup, split_threshold):
    """
    find the position that should be splitted, that is to find minimum num of different
    variable parts of each position or find the entropy
    """
    groupLen = len(eachGroup)
    wordLabel = []
    noCommon = False
    commonPart = LCS(eachGroup[0], eachGroup[1])
    Splittable = "yes"
    returnValues = {}
    for i in range(2, groupLen):
        if not comExit(commonPart, eachGroup[i]):
            commonPart = LCS(commonPart, eachGroup[i])
            if len(commonPart) == 0:
                noCommon = True
                print("there is no common part in this group")
                break

    for k in range(groupLen):
        newWordLabel = []
        for t in range(len(eachGroup[k])):
            if eachGroup[k][t] in commonPart:
                newWordLabel.append(1)  # 1 represent constant
            else:
                newWordLabel.append(0)  # 0 represents variable
        wordLabel.append(newWordLabel)

    conOrParaDivi = []
    partLabel = []
    seqLen = []
    # connect the continuous constant words or variable words as a big part(be a sequence)
    for i in range(groupLen):
        start = 0
        newconOrParaLL = []
        newPartLabel = []
        j = 1
        end = -1
        while j < len(eachGroup[i]):
            if wordLabel[i][j - 1] != wordLabel[i][j]:
                end = j - 1
                newconOrPara = []
                newconOrPara = newappend(start, end, eachGroup[i], newconOrPara)
                newconOrParaLL.append(newconOrPara)
                newPartLabel.append(wordLabel[i][end])
                start = j
            j += 1

        lastnewconOrPara = []
        for j in range(end + 1, len(eachGroup[i]), 1):
            lastnewconOrPara.append(eachGroup[i][j])
        newconOrParaLL.append(lastnewconOrPara)
        newPartLabel.append(wordLabel[i][end + 1])
        conOrParaDivi.append(newconOrParaLL)
        partLabel.append(newPartLabel)
        seqLen.append(len(newPartLabel))

    maxLen = max(seqLen)

    # convert list into tuple as list could not be the key of dict
    for i in range(groupLen):
        for j in range(len(conOrParaDivi[i])):
            conOrParaDivi[i][j] = tuple(conOrParaDivi[i][j])

    # initialize the list of dict of (part: occurance)
    partOccuLD = list()
    for t in range(
        maxLen
    ):  # wordLenPerGroup is the maximum number of positions in one group
        wordOccuD = {}
        partOccuLD.append(wordOccuD)

    for j in range(groupLen):  # the j-th word sequence
        for k in range(len(conOrParaDivi[j])):  # the k-th word in word sequence
            key = conOrParaDivi[j][k]
            if key not in partOccuLD[k]:
                partOccuLD[k][key] = 1
                continue
            partOccuLD[k][key] += 1
    numOfDiffParts = list()
    numOfPosi = len(partOccuLD)
    for i in range(numOfPosi):
        numOfDiffParts.append(len(partOccuLD[i]))

    minNum = np.inf
    minIndex = -1
    for i in range(numOfPosi):
        if numOfDiffParts[i] == 1:
            continue
        # print(numOfDiffParts[i])
        if numOfDiffParts[i] < split_threshold:
            if numOfDiffParts[i] < minNum:
                minNum = numOfDiffParts[i]
    if minNum == np.inf:
        Splittable = "no"
        # no minmum that smaller than split_threshold, which means all
        # position except are parameters, no need to split
        returnValues["splittable"] = "no"
        return returnValues

    indexOfMinItem = []
    for i in range(numOfPosi):
        if numOfDiffParts[i] == minNum:
            indexOfMinItem.append(i)

    if len(indexOfMinItem) == 1:
        minIndex = indexOfMinItem[0]  # minmum position

    # multiple position that has same minmum num of words
    minEntropy = np.inf
    if len(indexOfMinItem) > 1:
        for j in range((len(indexOfMinItem) - 1), -1, -1):
            entropy_J = entropy(
                partOccuLD[indexOfMinItem[j]], numOfDiffParts[indexOfMinItem[j]]
            )
            if entropy_J < minEntropy:
                minEntropy = entropy_J
                minIndex = j

    diffWordList = list(partOccuLD[minIndex].keys())
    returnValues["splittable"] = "yes"
    if len(diffWordList) == 1:
        returnValues["splittable"] = "no"
    returnValues["minIndex"] = minIndex
    returnValues["diffWordList"] = diffWordList
    returnValues["conOrParaDivi"] = conOrParaDivi
    return returnValues


def comExit(commonPart, seq):
    for i, itemI in enumerate(seq):
        if itemI not in commonPart:
            return False
    return True


def LCS(seq1, seq2):
    """find the common part of two sequences"""
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


def newappend(start, end, wordList, newconOrPara):
    for i in range(start, end + 1, 1):
        newconOrPara.append(wordList[i])
    return newconOrPara


def entropy(wordsOnPosit, totalNum):
    entropy = 0
    for key in wordsOnPosit:
        temp = float(wordsOnPosit[key]) / totalNum
        entropy -= math.log(temp) * temp
    return entropy


def dfsTraversal(key, logDict, flag, groupLoglist):
    for nodes in logDict[key]:
        if flag[nodes] == 0:
            groupLoglist.append(nodes)
            flag[nodes] = 1
            dfsTraversal(nodes, logDict, flag, groupLoglist)


def calDistance(wordLL, v, path):
    """calculate the distance betweent each two logs and save into a matrix"""
    print("calculate distance between every two logs...")
    logNum = len(wordLL)
    distList = []
    distMat = np.zeros((logNum, logNum))
    for i in range(logNum):
        for j in range(i, logNum):
            dist = editDistOfSeq(wordLL[i], wordLL[j], v)
            distMat[i][j] = distMat[j][i] = dist
            distList.append(dist)
    distArray = np.array(distList)
    np.savetxt(path + "editDistance.csv", distMat, delimiter=",")
    np.savetxt(path + "distArray.csv", distArray, delimiter=",")
    return distMat, distArray


def editDistOfSeq(wordList1, wordList2, v):
    """the edit distance of two logs"""
    m = len(wordList1) + 1
    n = len(wordList2) + 1
    d = []
    t = s = 0
    for i in range(m):
        d.append([t])
        t += 1 / (math.exp(i - v) + 1)
    del d[0][0]
    for j in range(n):
        d[0].append(s)
        s += 1 / (math.exp(j - v) + 1)
    for i in range(1, m):
        for j in range(1, n):
            if wordList1[i - 1] == wordList2[j - 1]:
                d[i].insert(j, d[i - 1][j - 1])
            else:
                weight = 1.0 / (math.exp(i - 1 - v) + 1)
                minimum = min(
                    d[i - 1][j] + weight,
                    d[i][j - 1] + weight,
                    d[i - 1][j - 1] + 2 * weight,
                )
                d[i].insert(j, minimum)
    return d[-1][-1]
