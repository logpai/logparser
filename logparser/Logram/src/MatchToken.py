"""
This file is modified from:
https://github.com/BlueLionLogram/Logram/tree/master/Evaluation
"""

import hashlib
import regex as re
import pandas as pd
import os
from .Common import regexGenerator


def tripleMatch(tokens, triDictionaryList, triThreshold):
    indexList = {}

    for index in range(len(tokens)):
        if index >= len(tokens) - 2:
            break
        tripleTmp = tokens[index] + "^" + tokens[index + 1] + "^" + tokens[index + 2]
        if (
            tripleTmp in triDictionaryList
            and triDictionaryList[tripleTmp] >= triThreshold
        ):
            pass
        else:
            indexList[index] = 1
            indexList[index + 1] = 1
            indexList[index + 2] = 1
    return list(indexList.keys())


def doubleMatch(tokens, indexList, doubleDictionaryList, doubleThreshold, length):
    dynamicIndex = []
    for i in range(len(indexList)):
        index = indexList[i]
        if index == 0:
            doubleTmp = tokens[index] + "^" + tokens[index + 1]
            if (
                doubleTmp in doubleDictionaryList
                and doubleDictionaryList[doubleTmp] > doubleThreshold
            ):
                pass
            else:
                dynamicIndex.append(index)
        elif index == length - 1:
            doubleTmp1 = tokens[index - 1] + "^" + tokens[index]
            doubleTmp2 = tokens[index] + "^" + tokens[0]
            if (
                doubleTmp1 in doubleDictionaryList
                and doubleDictionaryList[doubleTmp1] >= doubleThreshold
            ) or (
                doubleTmp2 in doubleDictionaryList
                and doubleDictionaryList[doubleTmp2] >= doubleThreshold
            ):
                pass
            else:
                dynamicIndex.append(index)
        else:
            doubleTmp1 = tokens[index] + "^" + tokens[index + 1]
            doubleTmp2 = tokens[index - 1] + "^" + tokens[index]
            if (
                doubleTmp1 in doubleDictionaryList
                and doubleDictionaryList[doubleTmp1] >= doubleThreshold
            ) or (
                doubleTmp2 in doubleDictionaryList
                and doubleDictionaryList[doubleTmp2] >= doubleThreshold
            ):
                pass
            else:
                dynamicIndex.append(index)
    return dynamicIndex


def tokenMatch(
    allTokensList,
    doubleDictionaryList,
    triDictionaryList,
    doubleThreshold,
    triThreshold,
    outdir,
    log_file_basename,
    allMessageList,
):
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    template_file = os.path.join(outdir, log_file_basename + "_templates.csv")
    structured_log_file = os.path.join(outdir, log_file_basename + "_structured.csv")

    structured_log_lines = []
    template_lines = []
    assert len(allTokensList) == len(allMessageList)
    for tokens in allTokensList:
        index = allTokensList.index(tokens)
        indexList = tripleMatch(tokens, triDictionaryList, triThreshold)
        dynamicIndex = doubleMatch(
            tokens, indexList, doubleDictionaryList, doubleThreshold, len(tokens)
        )

        logEvent = ""
        for i in range(len(tokens)):
            if i in dynamicIndex:
                tokens[i] = "<*>"
            logEvent = logEvent + tokens[i] + " "

        logEvent = re.sub(",", "", logEvent).strip()
        template_id = hashlib.md5(logEvent.encode("utf-8")).hexdigest()[0:8]

        if not (template_id, logEvent) in template_lines:
            template_lines.append((template_id, logEvent))

        structured_log_lines.append(
            (index + 1, allMessageList[index], template_id, logEvent)
        )

    template_df = pd.DataFrame(template_lines, columns=["EventId", "EventTemplate"])
    template_df.to_csv(template_file, index=False)
    structured_log_df = pd.DataFrame(
        structured_log_lines, columns=["LineId", "Content", "EventId", "EventTemplate"]
    )
    structured_log_df.to_csv(structured_log_file, index=False)
