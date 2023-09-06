# =========================================================================
# This file is modified from https://github.com/SRT-Lab/ULP
#
# MIT License
# Copyright (c) 2022 Universal Log Parser
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# =========================================================================

import os
import pandas as pd
import regex as re
import time
import warnings
from collections import Counter
from string import punctuation

warnings.filterwarnings("ignore")


class LogParser:
    def __init__(self, log_format, indir="./", outdir="./result/", rex=[]):
        """
        Attributes
        ----------
            rex : regular expressions used in preprocessing (step1)
            path : the input path stores the input log file name
            logName : the name of the input file containing raw log messages
            savePath : the output path stores the file containing structured logs
        """
        self.path = indir
        self.indir = indir
        self.outdir = outdir
        self.logName = None
        self.savePath = outdir
        self.df_log = None
        self.log_format = log_format
        self.rex = rex

    def tokenize(self):
        event_label = []
        # print("\n============================Removing obvious dynamic variables======================\n\n")
        for idx, log in self.df_log["Content"].iteritems():
            tokens = log.split()
            tokens = re.sub(r"\\", "", str(tokens))
            tokens = re.sub(r"\'", "", str(tokens))
            tokens = tokens.translate({ord(c): "" for c in "!@#$%^&*{}<>?\|`~"})

            re_list = [
                "([\da-fA-F]{2}:){5}[\da-fA-F]{2}",
                "\d{4}-\d{2}-\d{2}",
                "\d{4}\/\d{2}\/\d{2}",
                "[0-9]{2}:[0-9]{2}:[0-9]{2}(?:[.,][0-9]{3})?",
                "[0-9]{2}:[0-9]{2}:[0-9]{2}",
                "[0-9]{2}:[0-9]{2}",
                "0[xX][0-9a-fA-F]+",
                "([\(]?[0-9a-fA-F]*:){8,}[\)]?",
                "^(?:[0-9]{4}-[0-9]{2}-[0-9]{2})(?:[ ][0-9]{2}:[0-9]{2}:[0-9]{2})?(?:[.,][0-9]{3})?",
                "(\/|)([a-zA-Z0-9-]+\.){2,}([a-zA-Z0-9-]+)?(:[a-zA-Z0-9-]+|)(:|)",
            ]

            pat = r"\b(?:{})\b".format("|".join(str(v) for v in re_list))
            tokens = re.sub(pat, "<*>", str(tokens))
            tokens = tokens.replace("=", " = ")
            tokens = tokens.replace(")", " ) ")
            tokens = tokens.replace("(", " ( ")
            tokens = tokens.replace("]", " ] ")
            tokens = tokens.replace("[", " [ ")
            event_label.append(str(tokens).lstrip().replace(",", " "))

        self.df_log["event_label"] = event_label

        return 0

    def getDynamicVars2(self, petit_group):
        petit_group["event_label"] = petit_group["event_label"].map(
            lambda x: " ".join(dict.fromkeys(x.split()))
        )
        petit_group["event_label"] = petit_group["event_label"].map(
            lambda x: " ".join(
                filter(None, (word.strip(punctuation) for word in x.split()))
            )
        )

        lst = petit_group["event_label"].values.tolist()

        vec = []
        big_lst = " ".join(v for v in lst)
        this_count = Counter(big_lst.split())

        if this_count:
            max_val = max(this_count, key=this_count.get)
            for word in this_count:
                if this_count[word] < this_count[max_val]:
                    vec.append(word)

        return vec

    def remove_word_with_special(self, sentence):
        sentence = sentence.translate(
            {ord(c): "" for c in "!@#$%^&*()[]{};:,/<>?\|`~-=+"}
        )
        length = len(sentence.split())

        finale = ""
        for word in sentence.split():
            if (
                not any(ch.isdigit() for ch in word)
                and not any(not c.isalnum() for c in word)
                and len(word) > 1
            ):
                finale += word

        finale = finale + str(length)
        return finale

    def outputResult(self):
        self.df_log.to_csv(
            os.path.join(self.savePath, self.logName + "_structured.csv"), index=False
        )

    def load_data(self):
        headers, regex = self.generate_logformat_regex(self.log_format)

        self.df_log = self.log_to_dataframe(
            os.path.join(self.path, self.logname), regex, headers, self.log_format
        )

    def generate_logformat_regex(self, logformat):
        """Function to generate regular expression to split log messages"""
        headers = []
        splitters = re.split(r"(<[^<>]+>)", logformat)
        regex = ""
        for k in range(len(splitters)):
            if k % 2 == 0:
                splitter = re.sub(" +", "\\\s+", splitters[k])
                regex += splitter
            else:
                header = splitters[k].strip("<").strip(">")
                regex += "(?P<%s>.*?)" % header
                headers.append(header)
        regex = re.compile("^" + regex + "$")
        return headers, regex

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
                    print("[Warning] Skip line: " + line)
        logdf = pd.DataFrame(log_messages, columns=headers)
        logdf.insert(0, "LineId", None)
        logdf["LineId"] = [i + 1 for i in range(linecount)]
        return logdf

    def parse(self, logname):
        start_timeBig = time.time()
        print("Parsing file: " + os.path.join(self.path, logname))

        self.logname = logname

        regex = [r"blk_-?\d+", r"(\d+\.){3}\d+(:\d+)?"]

        self.load_data()
        self.df_log = self.df_log.sample(n=2000)
        self.tokenize()
        self.df_log["EventId"] = self.df_log["event_label"].map(
            lambda x: self.remove_word_with_special(str(x))
        )
        groups = self.df_log.groupby("EventId")
        keys = groups.groups.keys()
        stock = pd.DataFrame()
        count = 0

        re_list2 = ["[ ]{1,}[-]*[0-9]+[ ]{1,}", ' "\d+" ']

        generic_re = re.compile("|".join(re_list2))

        for i in keys:
            l = []
            slc = groups.get_group(i)

            template = slc["event_label"][0:1].to_list()[0]
            count += 1
            if slc.size > 1:
                l = self.getDynamicVars2(slc.head(10))
                pat = r"\b(?:{})\b".format("|".join(str(v) for v in l))
                if len(l) > 0:
                    template = template.lower()
                    template = re.sub(pat, "<*>", template)

            template = re.sub(generic_re, " <*> ", template)
            slc["event_label"] = [template] * len(slc["event_label"].to_list())

            stock = stock.append(slc)
            stock = stock.sort_index()

        self.df_log = stock

        self.df_log["EventTemplate"] = self.df_log["event_label"]
        if not os.path.exists(self.savePath):
            os.makedirs(self.savePath)
        self.df_log.to_csv(
            os.path.join(self.savePath, logname + "_structured.csv"), index=False
        )
        elapsed_timeBig = time.time() - start_timeBig
        print(f"Parsing done in {elapsed_timeBig} sec")
        return 0
