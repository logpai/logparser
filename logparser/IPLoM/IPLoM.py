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

import copy
import sys
from datetime import datetime
import os
import regex as re
import pandas as pd
import hashlib


class Partition:
    """Wrap around the logs and the step number"""

    def __init__(self, stepNo, numOfLogs=0, lenOfLogs=0):
        self.logLL = []
        self.stepNo = stepNo
        self.valid = True
        self.numOfLogs = numOfLogs
        self.lenOfLogs = lenOfLogs


class Event:
    def __init__(self, eventStr):
        self.eventStr = eventStr
        self.eventId = hashlib.md5(" ".join(eventStr).encode("utf-8")).hexdigest()[0:8]
        self.eventCount = 0


class Para:
    """Para class

    Attributes
    ----------
        maxEventLen : the length of the longest log/event, which is used in step 1 to split logs into partitions
            according to their length
        path : the path of the input file
        step2Support : the support threshold to create a new partition, partitions which contains less than
            step2Support logs will not go through step 2
        PST : Partition support ratio threshold
        CT : Cluster goodness threshold used in DetermineP1P2 in step3. If the columns with unique term more
            than CT, we skip step 3
    """

    def __init__(
        self,
        log_format,
        indir,
        outdir,
        maxEventLen,
        step2Support,
        PST,
        CT,
        lowerBound,
        upperBound,
        rex,
    ):
        self.maxEventLen = maxEventLen
        self.path = indir
        self.savePath = outdir
        self.step2Support = step2Support
        self.PST = PST
        self.CT = CT
        self.lowerBound = lowerBound
        self.upperBound = upperBound
        self.rex = rex
        self.logformat = log_format


class LogParser:
    def __init__(
        self,
        log_format,
        indir="../logs/",
        outdir="./result/",
        maxEventLen=200,
        step2Support=0,
        PST=0,
        CT=0.35,
        lowerBound=0.25,
        upperBound=0.9,
        rex=[],
        keep_para=True,
    ):
        self.para = Para(
            log_format=log_format,
            indir=indir,
            outdir=outdir,
            maxEventLen=maxEventLen,
            step2Support=step2Support,
            PST=PST,
            CT=CT,
            lowerBound=lowerBound,
            upperBound=upperBound,
            rex=rex,
        )
        self.partitionsL = []
        self.eventsL = []
        self.output = []
        self.keep_para = keep_para

        if not os.path.exists(self.para.savePath):
            os.makedirs(self.para.savePath)

        # Initialize some partitions which contain logs with different length
        for logLen in range(self.para.maxEventLen + 1):
            self.partitionsL.append(Partition(stepNo=1, numOfLogs=0, lenOfLogs=logLen))

    def parse(self, logname):
        print("Parsing file: " + os.path.join(self.para.path, logname))
        self.logname = logname
        starttime = datetime.now()
        self.Step1()
        self.Step2()
        self.Step3()
        self.Step4()
        self.getOutput()
        self.WriteEventToFile()
        print("Parsing done. [Time taken: {!s}]".format(datetime.now() - starttime))

    def Step1(self):
        headers, regex = self.generate_logformat_regex(self.para.logformat)
        self.df_log = self.log_to_dataframe(
            os.path.join(self.para.path, self.logname),
            regex,
            headers,
            self.para.logformat,
        )
        lineCount = 1
        for idx, line in self.df_log.iterrows():
            line = line["Content"]
            # If line is empty, skip
            if line.strip() == "":
                continue

            if self.para.rex:
                for currentRex in self.para.rex:
                    line = re.sub(currentRex, "", line)

            wordSeq = list(filter(lambda x: x != "", re.split(r"[\s=:,]", line)))
            if not wordSeq:
                wordSeq = [" "]

            # Generate terms list, with ID in the end
            wordSeq.append(str(lineCount))
            lineCount += 1

            # Add current log to the corresponding partition
            self.partitionsL[len(wordSeq) - 1].logLL.append(wordSeq)
            self.partitionsL[len(wordSeq) - 1].numOfLogs += 1

        for partition in self.partitionsL:
            if partition.numOfLogs == 0:
                partition.valid = False

            elif (
                self.para.PST != 0
                and 1.0 * partition.numOfLogs / lineCount < self.para.PST
            ):
                for logL in partition.logLL:
                    self.partitionsL[0].logLL.append(logL)
                    self.partitionsL[0].numOfLogs += 1
                partition.valid = False

    def Step2(self):
        for partition in self.partitionsL:
            if not partition.valid:
                continue

            if partition.numOfLogs <= self.para.step2Support:
                continue

            # Avoid going through newly generated partitions
            if partition.stepNo == 2:
                break

            # For each column, create a set to hold the unique tokens in that column.
            # And finally, calculate the number of the unique tokens in each column
            uniqueTokensCountLS = []
            for columnIdx in range(partition.lenOfLogs):
                uniqueTokensCountLS.append(set())

            for logL in partition.logLL:
                for columnIdx in range(partition.lenOfLogs):
                    uniqueTokensCountLS[columnIdx].add(logL[columnIdx])

            # Find the column with minimum unique tokens
            minColumnIdx = 0
            minColumnCount = len(uniqueTokensCountLS[0])

            for columnIdx in range(partition.lenOfLogs):
                if minColumnCount > len(uniqueTokensCountLS[columnIdx]):
                    minColumnCount = len(uniqueTokensCountLS[columnIdx])
                    minColumnIdx = columnIdx

            # If there is one column with one unique term, do not split this partition
            if minColumnCount == 1:
                continue

            # From split-token to log list
            logDLL = {}
            for logL in partition.logLL:
                if logL[minColumnIdx] not in logDLL:
                    logDLL[logL[minColumnIdx]] = []
                logDLL[logL[minColumnIdx]].append(logL)

            for key in logDLL:
                if (
                    self.para.PST != 0
                    and 1.0 * len(logDLL[key]) / partition.numOfLogs < self.para.PST
                ):
                    self.partitionsL[0].logLL += logDLL[key]
                    self.partitionsL[0].numOfLogs += len(logDLL[key])
                else:
                    newPartition = Partition(
                        stepNo=2,
                        numOfLogs=len(logDLL[key]),
                        lenOfLogs=partition.lenOfLogs,
                    )
                    newPartition.logLL = logDLL[key]
                    self.partitionsL.append(newPartition)

            partition.valid = False

    def Step3(self):
        for partition in self.partitionsL:
            if not partition.valid:
                continue

            if partition.stepNo == 3:
                break

            # Find two columns that my cause split in this step
            p1, p2 = self.DetermineP1P2(partition)

            if p1 == -1 or p2 == -1:
                continue

            try:
                p1Set = set()
                p2Set = set()
                mapRelation1DS = {}
                mapRelation2DS = {}

                # Construct token sets for p1 and p2, dictionary to record the mapping relations between p1 and p2
                for logL in partition.logLL:
                    p1Set.add(logL[p1])
                    p2Set.add(logL[p2])

                    if logL[p1] == logL[p2]:
                        print("Warning: p1 may be equal to p2")

                    if logL[p1] not in mapRelation1DS:
                        mapRelation1DS[logL[p1]] = set()
                    mapRelation1DS[logL[p1]].add(logL[p2])

                    if logL[p2] not in mapRelation2DS:
                        mapRelation2DS[logL[p2]] = set()
                    mapRelation2DS[logL[p2]].add(logL[p1])

                # Construct sets to record the tokens in 1-1, 1-M, M-1 relationships, the left-tokens in p1Set & p2Set
                # are in M-M relationships
                oneToOneS = set()
                oneToMP1D = {}
                oneToMP2D = {}

                # select 1-1 and 1-M relationships
                for p1Token in p1Set:
                    if len(mapRelation1DS[p1Token]) == 1:
                        if len(mapRelation2DS[list(mapRelation1DS[p1Token])[0]]) == 1:
                            oneToOneS.add(p1Token)

                    else:
                        isOneToM = True

                        for p2Token in mapRelation1DS[p1Token]:
                            if len(mapRelation2DS[p2Token]) != 1:
                                isOneToM = False
                                break
                        if isOneToM:
                            oneToMP1D[p1Token] = 0

                # delete the tokens which are picked to 1-1 and 1-M relationships from p1Set, so that the left are M-M
                for deleteToken in oneToOneS:
                    p1Set.remove(deleteToken)
                    p2Set.remove(list(mapRelation1DS[deleteToken])[0])

                for deleteToken in oneToMP1D:
                    for deleteTokenP2 in mapRelation1DS[deleteToken]:
                        p2Set.remove(deleteTokenP2)
                    p1Set.remove(deleteToken)

                # select M-1 relationships
                for p2Token in p2Set:
                    if len(mapRelation2DS[p2Token]) != 1:
                        isOneToM = True
                        for p1Token in mapRelation2DS[p2Token]:
                            if len(mapRelation1DS[p1Token]) != 1:
                                isOneToM = False
                                break
                        if isOneToM:
                            oneToMP2D[p2Token] = 0

                # delete the tokens which are picked to M-1 relationships from p2Set, so that the left are M-M
                for deleteToken in oneToMP2D:
                    p2Set.remove(deleteToken)
                    for deleteTokenP1 in mapRelation2DS[deleteToken]:
                        p1Set.remove(deleteTokenP1)

                # calculate the #Lines_that_match_S
                for logL in partition.logLL:
                    if logL[p1] in oneToMP1D:
                        oneToMP1D[logL[p1]] += 1

                    if logL[p2] in oneToMP2D:
                        oneToMP2D[logL[p2]] += 1

            except KeyError as er:
                print(er)
                print("error: " + str(p1) + "\t" + str(p2))

            newPartitionsD = {}
            if partition.stepNo == 2:
                newPartitionsD["dumpKeyforMMrelationInStep2__"] = Partition(
                    stepNo=3, numOfLogs=0, lenOfLogs=partition.lenOfLogs
                )
            # Split partition
            for logL in partition.logLL:
                # If is 1-1
                if logL[p1] in oneToOneS:
                    if logL[p1] not in newPartitionsD:
                        newPartitionsD[logL[p1]] = Partition(
                            stepNo=3, numOfLogs=0, lenOfLogs=partition.lenOfLogs
                        )
                    newPartitionsD[logL[p1]].logLL.append(logL)
                    newPartitionsD[logL[p1]].numOfLogs += 1

                # This part can be improved. The split_rank can be calculated once.
                # If is 1-M
                elif logL[p1] in oneToMP1D:
                    split_rank = self.Get_Rank_Posistion(
                        len(mapRelation1DS[logL[p1]]), oneToMP1D[logL[p1]], True
                    )
                    if split_rank == 1:
                        if logL[p1] not in newPartitionsD:
                            newPartitionsD[logL[p1]] = Partition(
                                stepNo=3, numOfLogs=0, lenOfLogs=partition.lenOfLogs
                            )
                        newPartitionsD[logL[p1]].logLL.append(logL)
                        newPartitionsD[logL[p1]].numOfLogs += 1
                    else:
                        if logL[p2] not in newPartitionsD:
                            newPartitionsD[logL[p2]] = Partition(
                                stepNo=3, numOfLogs=0, lenOfLogs=partition.lenOfLogs
                            )
                        newPartitionsD[logL[p2]].logLL.append(logL)
                        newPartitionsD[logL[p2]].numOfLogs += 1

                # If is M-1
                elif logL[p2] in oneToMP2D:
                    split_rank = self.Get_Rank_Posistion(
                        len(mapRelation2DS[logL[p2]]), oneToMP2D[logL[p2]], False
                    )
                    if split_rank == 1:
                        if logL[p1] not in newPartitionsD:
                            newPartitionsD[logL[p1]] = Partition(
                                stepNo=3, numOfLogs=0, lenOfLogs=partition.lenOfLogs
                            )
                        newPartitionsD[logL[p1]].logLL.append(logL)
                        newPartitionsD[logL[p1]].numOfLogs += 1
                    else:
                        if logL[p2] not in newPartitionsD:
                            newPartitionsD[logL[p2]] = Partition(
                                stepNo=3, numOfLogs=0, lenOfLogs=partition.lenOfLogs
                            )
                        newPartitionsD[logL[p2]].logLL.append(logL)
                        newPartitionsD[logL[p2]].numOfLogs += 1

                # M-M
                else:
                    if partition.stepNo == 2:
                        newPartitionsD["dumpKeyforMMrelationInStep2__"].logLL.append(
                            logL
                        )
                        newPartitionsD["dumpKeyforMMrelationInStep2__"].numOfLogs += 1
                    else:
                        if len(p1Set) < len(p2Set):
                            if logL[p1] not in newPartitionsD:
                                newPartitionsD[logL[p1]] = Partition(
                                    stepNo=3, numOfLogs=0, lenOfLogs=partition.lenOfLogs
                                )
                            newPartitionsD[logL[p1]].logLL.append(logL)
                            newPartitionsD[logL[p1]].numOfLogs += 1
                        else:
                            if logL[p2] not in newPartitionsD:
                                newPartitionsD[logL[p2]] = Partition(
                                    stepNo=3, numOfLogs=0, lenOfLogs=partition.lenOfLogs
                                )
                            newPartitionsD[logL[p2]].logLL.append(logL)
                            newPartitionsD[logL[p2]].numOfLogs += 1

            if (
                "dumpKeyforMMrelationInStep2__" in newPartitionsD
                and newPartitionsD["dumpKeyforMMrelationInStep2__"].numOfLogs == 0
            ):
                newPartitionsD["dumpKeyforMMrelationInStep2__"].valid = False
            # Add all the new partitions to collection
            for key in newPartitionsD:
                if (
                    self.para.PST != 0
                    and 1.0 * newPartitionsD[key].numOfLogs / partition.numOfLogs
                    < self.para.PST
                ):
                    self.partitionsL[0].logLL += newPartitionsD[key].logLL
                    self.partitionsL[0].numOfLogs += newPartitionsD[key].numOfLogs
                else:
                    self.partitionsL.append(newPartitionsD[key])

            partition.valid = False

    def Step4(self):
        self.partitionsL[0].valid = False
        if self.para.PST == 0 and self.partitionsL[0].numOfLogs != 0:
            event = Event(["Outlier"])
            event.eventCount = self.partitionsL[0].numOfLogs
            self.eventsL.append(event)

            for logL in self.partitionsL[0].logLL:
                logL.append(str(event.eventId))

        for partition in self.partitionsL:
            if not partition.valid:
                continue

            if partition.numOfLogs == 0:
                print(str(partition.stepNo) + "\t")

            uniqueTokensCountLS = []
            for columnIdx in range(partition.lenOfLogs):
                uniqueTokensCountLS.append(set())

            for logL in partition.logLL:
                for columnIdx in range(partition.lenOfLogs):
                    uniqueTokensCountLS[columnIdx].add(logL[columnIdx])

            e = copy.deepcopy(partition.logLL[0])[: partition.lenOfLogs]

            for columnIdx in range(partition.lenOfLogs):
                if len(uniqueTokensCountLS[columnIdx]) == 1:
                    continue
                else:
                    e[columnIdx] = "<*>"

            event = Event(e)
            event.eventCount = partition.numOfLogs

            self.eventsL.append(event)

            for logL in partition.logLL:
                logL.append(str(event.eventId))

    def getOutput(self):
        if self.para.PST == 0 and self.partitionsL[0].numOfLogs != 0:
            for logL in self.partitionsL[0].logLL:
                self.output.append(logL[-2:] + logL[:-2])
        for partition in self.partitionsL:
            if not partition.valid:
                continue
            for logL in partition.logLL:
                self.output.append(logL[-2:] + logL[:-2])

    def WriteEventToFile(self):
        eventID_template = {
            event.eventId: " ".join(event.eventStr) for event in self.eventsL
        }
        eventList = [
            [event.eventId, " ".join(event.eventStr), event.eventCount]
            for event in self.eventsL
        ]
        eventDf = pd.DataFrame(
            eventList, columns=["EventId", "EventTemplate", "Occurrences"]
        )
        eventDf.to_csv(
            os.path.join(self.para.savePath, self.logname + "_templates.csv"),
            index=False,
        )

        self.output.sort(key=lambda x: int(x[0]))
        self.df_log["EventId"] = [str(logL[1]) for logL in self.output]
        self.df_log["EventTemplate"] = [
            eventID_template[logL[1]] for logL in self.output
        ]
        if self.keep_para:
            self.df_log["ParameterList"] = self.df_log.apply(
                self.get_parameter_list, axis=1
            )
        self.df_log.to_csv(
            os.path.join(self.para.savePath, self.logname + "_structured.csv"),
            index=False,
        )

    """
    For 1-M and M-1 mappings, you need to decide whether M side are constants or variables. This method is to decide which side to split

    cardOfS           : The number of unique values in this set
    Lines_that_match_S: The number of lines that have these values
    one_m             : If the mapping is 1-M, this value is True. Otherwise, False
    """

    def Get_Rank_Posistion(self, cardOfS, Lines_that_match_S, one_m):
        try:
            distance = 1.0 * cardOfS / Lines_that_match_S
        except ZeroDivisionError as er1:
            print(er1)
            print(
                "cardOfS: "
                + str(cardOfS)
                + "\t"
                + "Lines_that_match_S: "
                + str(Lines_that_match_S)
            )

        if distance <= self.para.lowerBound:
            if one_m:
                split_rank = 2
            else:
                split_rank = 1
        elif distance >= self.para.upperBound:
            if one_m:
                split_rank = 1
            else:
                split_rank = 2
        else:
            if one_m:
                split_rank = 1
            else:
                split_rank = 2

        return split_rank

    def DetermineP1P2(self, partition):
        if partition.lenOfLogs > 2:
            count_1 = 0

            uniqueTokensCountLS = []
            for columnIdx in range(partition.lenOfLogs):
                uniqueTokensCountLS.append(set())

            for logL in partition.logLL:
                for columnIdx in range(partition.lenOfLogs):
                    uniqueTokensCountLS[columnIdx].add(logL[columnIdx])

            # Count how many columns have only one unique term
            for columnIdx in range(partition.lenOfLogs):
                if len(uniqueTokensCountLS[columnIdx]) == 1:
                    count_1 += 1

            # If the columns with unique term more than a threshold, we return (-1, -1) to skip step 3
            GC = 1.0 * count_1 / partition.lenOfLogs

            if GC < self.para.CT:
                return self.Get_Mapping_Position(partition, uniqueTokensCountLS)
            else:
                return (-1, -1)

        elif partition.lenOfLogs == 2:
            return (0, 1)
        else:
            return (-1, -1)

    def Get_Mapping_Position(self, partition, uniqueTokensCountLS):
        p1 = p2 = -1

        # Caculate #unqiueterms in each column, and record how many column with each #uniqueterms
        numOfUniqueTokensD = {}
        for columnIdx in range(partition.lenOfLogs):
            if len(uniqueTokensCountLS[columnIdx]) not in numOfUniqueTokensD:
                numOfUniqueTokensD[len(uniqueTokensCountLS[columnIdx])] = 0
            numOfUniqueTokensD[len(uniqueTokensCountLS[columnIdx])] += 1

        if partition.stepNo == 2:
            # Find the largest card and second largest card
            maxIdx = secondMaxIdx = -1
            maxCount = secondMaxCount = 0
            for key in numOfUniqueTokensD:
                if key == 1:
                    continue
                if numOfUniqueTokensD[key] > maxCount:
                    secondMaxIdx = maxIdx
                    secondMaxCount = maxCount
                    maxIdx = key
                    maxCount = numOfUniqueTokensD[key]
                elif (
                    numOfUniqueTokensD[key] > secondMaxCount
                    and numOfUniqueTokensD[key] != maxCount
                ):
                    secondMaxIdx = key
                    secondMaxCount = numOfUniqueTokensD[key]

            # If the frequency of the freq_card>1 then
            if maxCount > 1:
                for columnIdx in range(partition.lenOfLogs):
                    if len(uniqueTokensCountLS[columnIdx]) == maxIdx:
                        if p1 == -1:
                            p1 = columnIdx
                        else:
                            p2 = columnIdx
                            break

            # If the frequency of the freq_card==1 then
            else:
                for columnIdx in range(partition.lenOfLogs):
                    if len(uniqueTokensCountLS[columnIdx]) == maxIdx:
                        p1 = columnIdx
                        break

                for columnIdx in range(partition.lenOfLogs):
                    if len(uniqueTokensCountLS[columnIdx]) == secondMaxIdx:
                        p2 = columnIdx
                        break

            if p1 == -1 or p2 == -1:
                return (-1, -1)
            else:
                return (p1, p2)

        # If it is from step 1
        else:
            minIdx = secondMinIdx = -1
            minCount = secondMinCount = sys.maxsize
            for key in numOfUniqueTokensD:
                if numOfUniqueTokensD[key] < minCount:
                    secondMinIdx = minIdx
                    secondMinCount = minCount
                    minIdx = key
                    minCount = numOfUniqueTokensD[key]
                elif (
                    numOfUniqueTokensD[key] < secondMinCount
                    and numOfUniqueTokensD[key] != minCount
                ):
                    secondMinIdx = key
                    secondMinCount = numOfUniqueTokensD[key]

            for columnIdx in range(len(uniqueTokensCountLS)):
                if numOfUniqueTokensD[len(uniqueTokensCountLS[columnIdx])] == minCount:
                    if p1 == -1:
                        p1 = columnIdx
                        break

            for columnIdx in range(len(uniqueTokensCountLS)):
                if (
                    numOfUniqueTokensD[len(uniqueTokensCountLS[columnIdx])]
                    == secondMinCount
                ):
                    p2 = columnIdx
                    break

            return (p1, p2)

    def PrintPartitions(self):
        for idx in range(len(self.partitionsL)):
            print(
                "Partition {}:(from step {})    Valid:{}".format(
                    idx, self.partitionsL[idx].stepNo, self.partitionsL[idx].valid
                )
            )

            for log in self.partitionsL[idx].logLL:
                print(log)

    def PrintEventStats(self):
        for event in self.eventsL:
            if event.eventCount > 1:
                print(str(event.eventId) + "\t" + str(event.eventCount))
                print(event.eventStr)

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
        """Function to generate regular expression to split log messages"""
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

    def get_parameter_list(self, row):
        template_regex = re.sub(r"<.{1,5}>", "<*>", row["EventTemplate"])
        if "<*>" not in template_regex:
            return []
        template_regex = re.sub(r"([^A-Za-z0-9])", r"\\\1", template_regex)
        template_regex = re.sub(r"\\ +", r"\\s+", template_regex)
        template_regex = "^" + template_regex.replace("\<\*\>", "(.*?)") + "$"
        parameter_list = re.findall(template_regex, row["Content"])
        parameter_list = parameter_list[0] if parameter_list else ()
        parameter_list = (
            list(parameter_list)
            if isinstance(parameter_list, tuple)
            else [parameter_list]
        )
        return parameter_list
