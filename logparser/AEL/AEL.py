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


import regex as re
import os
import hashlib
import pandas as pd
from datetime import datetime
from collections import defaultdict
from functools import reduce
from tqdm import tqdm


class Event:
    def __init__(self, logidx, Eventstr=""):
        self.id = hashlib.md5(Eventstr.encode("utf-8")).hexdigest()[0:8]
        self.logs = [logidx]
        self.Eventstr = Eventstr
        self.EventToken = Eventstr.split()
        self.merged = False

    def refresh_id(self):
        self.id = hashlib.md5(self.Eventstr.encode("utf-8")).hexdigest()[0:8]


class LogParser:
    def __init__(
        self,
        indir,
        outdir,
        log_format,
        minEventCount=2,
        merge_percent=1,
        rex=[],
        keep_para=True,
    ):
        self.logformat = log_format
        self.path = indir
        self.savePath = outdir
        self.rex = rex
        self.minEventCount = minEventCount
        self.merge_percent = merge_percent
        self.df_log = None
        self.logname = None
        self.merged_events = []
        self.bins = defaultdict(dict)
        self.keep_para = keep_para

    def parse(self, logname):
        start_time = datetime.now()
        print("Parsing file: " + os.path.join(self.path, logname))
        self.logname = logname
        self.load_data()
        self.tokenize()
        self.categorize()
        self.reconcile()
        self.dump()
        print("Parsing done. [Time taken: {!s}]".format(datetime.now() - start_time))

    def tokenize(self):
        """
        Put logs into bins according to (# of '<*>', # of token)

        """
        for idx, log in self.df_log["Content_"].items():
            para_count = 0

            tokens = log.split()
            for token in tokens:
                if token == "<*>":
                    para_count += 1

            if "Logs" not in self.bins[(len(tokens), para_count)]:
                self.bins[(len(tokens), para_count)]["Logs"] = [idx]
            else:
                self.bins[(len(tokens), para_count)]["Logs"].append(idx)

    def categorize(self):
        """
        Abstract templates bin by bin

        """
        for key in tqdm(self.bins):
            abin = self.bins[key]
            abin["Events"] = []

            for logidx in abin["Logs"]:
                log = self.df_log["Content_"].loc[logidx]
                matched = False
                for event in abin["Events"]:
                    if log == event.Eventstr:
                        matched = True
                        event.logs.append(logidx)
                        break
                if not matched:
                    abin["Events"].append(Event(logidx, log))

    def reconcile(self):
        """
        Merge events if a bin has too many events

        """
        for key in self.bins:
            abin = self.bins[key]
            if len(abin["Events"]) > self.minEventCount:
                tobeMerged = []
                for e1 in abin["Events"]:
                    if e1.merged:
                        continue
                    e1.merged = True
                    tobeMerged.append([e1])

                    for e2 in abin["Events"]:
                        if e2.merged:
                            continue
                        if self.has_diff(e1.EventToken, e2.EventToken):
                            tobeMerged[-1].append(e2)
                            e2.merged = True
                for Es in tobeMerged:
                    merged_event = reduce(self.merge_event, Es)
                    merged_event.refresh_id()
                    self.merged_events.append(merged_event)
            else:
                for e in abin["Events"]:
                    self.merged_events.append(e)

    def dump(self):
        if not os.path.isdir(self.savePath):
            os.makedirs(self.savePath)

        templateL = [0] * self.df_log.shape[0]
        idL = [0] * self.df_log.shape[0]
        df_events = []

        for event in self.merged_events:
            for logidx in event.logs:
                templateL[logidx] = event.Eventstr
                idL[logidx] = event.id
            df_events.append([event.id, event.Eventstr, len(event.logs)])

        df_event = pd.DataFrame(
            df_events, columns=["EventId", "EventTemplate", "Occurrences"]
        )

        self.df_log["EventId"] = idL
        self.df_log["EventTemplate"] = templateL
        self.df_log.drop("Content_", axis=1, inplace=True)
        if self.keep_para:
            self.df_log["ParameterList"] = self.df_log.apply(
                self.get_parameter_list, axis=1
            )
        self.df_log.to_csv(
            os.path.join(self.savePath, self.logname + "_structured.csv"), index=False
        )

        occ_dict = dict(self.df_log["EventTemplate"].value_counts())
        df_event = pd.DataFrame()
        df_event["EventTemplate"] = self.df_log["EventTemplate"].unique()
        df_event["EventId"] = df_event["EventTemplate"].map(
            lambda x: hashlib.md5(x.encode("utf-8")).hexdigest()[0:8]
        )
        df_event["Occurrences"] = df_event["EventTemplate"].map(occ_dict)
        df_event.to_csv(
            os.path.join(self.savePath, self.logname + "_templates.csv"),
            index=False,
            columns=["EventId", "EventTemplate", "Occurrences"],
        )

    def merge_event(self, e1, e2):
        for pos in range(len(e1.EventToken)):
            if e1.EventToken[pos] != e2.EventToken[pos]:
                e1.EventToken[pos] = "<*>"

        e1.logs.extend(e2.logs)
        e1.Eventstr = " ".join(e1.EventToken)

        return e1

    def has_diff(self, tokens1, tokens2):
        diff = 0
        for idx in range(len(tokens1)):
            if tokens1[idx] != tokens2[idx]:
                diff += 1
        return True if 0 < diff * 1.0 / len(tokens1) <= self.merge_percent else False

    def load_data(self):
        def preprocess(log):
            for currentRex in self.rex:
                log = re.sub(currentRex, "<*>", log)
            return log

        headers, regex = self.generate_logformat_regex(self.logformat)
        self.df_log = self.log_to_dataframe(
            os.path.join(self.path, self.logname), regex, headers, self.logformat
        )
        self.df_log["Content_"] = self.df_log["Content"].map(preprocess)

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
