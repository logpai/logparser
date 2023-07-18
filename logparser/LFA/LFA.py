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

import os
import regex as re
import hashlib
import pandas as pd
from collections import defaultdict
from datetime import datetime


class LogParser(object):
    def __init__(self, indir, outdir, log_format, rex=[]):
        self.path = indir
        self.savePath = outdir
        self.logformat = log_format
        self.rex = rex
        self.wordseqs = []
        self.df_log = pd.DataFrame()
        self.wordpos_count = defaultdict(int)

    def parse(self, logname):
        print("Parsing file: " + os.path.join(self.path, logname))
        self.logname = logname
        start_time = datetime.now()
        self.firstpass()
        self.secondpass()
        print("Parsing done. [Time taken: {!s}]".format(datetime.now() - start_time))

    def firstpass(self):
        headers, regex = self.generate_logformat_regex(self.logformat)
        self.df_log = self.log_to_dataframe(
            os.path.join(self.path, self.logname), regex, headers, self.logformat
        )

        self.wordseqs = []
        for idx, line in self.df_log.iterrows():
            line = line["Content"]

            if self.rex:
                for currentRex in self.rex:
                    line = re.sub(currentRex, "<*>", line)

            wordseq = line.split()
            self.wordseqs.append(wordseq)

            for pos, word in enumerate(wordseq):
                # if word.strip() != "<*>":
                self.wordpos_count[(pos, word)] += 1
        print("First pass done.")

    def secondpass(self):
        self.templates = {}
        templatel = []
        for wordseq in self.wordseqs:
            countsl = [
                self.wordpos_count[(pos, word)]
                for pos, word in enumerate(wordseq)
                if word != "<*>"
            ]
            if len(countsl) > 1:
                # find max gap
                countsl_sorted = sorted(countsl)
                gaps = [
                    (countsl_sorted[idx + 1] - countsl_sorted[idx], idx)
                    for idx in range(len(countsl_sorted) - 1)
                ]
                split_value = countsl_sorted[max(gaps, key=lambda x: x[0])[1]]
                if max(countsl) != min(countsl):
                    countsl = [
                        self.wordpos_count[(pos, word)]
                        for pos, word in enumerate(wordseq)
                    ]
                    wordseq = [
                        wordseq[pos] if count > split_value else "<*>"
                        for pos, count in enumerate(countsl)
                    ]

            template = " ".join(wordseq)
            templatel.append(template)
            if template not in self.templates:
                self.templates[template] = {
                    "id": hashlib.md5(" ".join(template).encode("utf-8")).hexdigest()[
                        0:8
                    ],
                    "count": 1,
                }
            else:
                self.templates[template]["count"] += 1
        print("Second pass done.")
        self.df_log["EventId"] = [self.templates[x]["id"] for x in templatel]
        self.df_log["EventTemplate"] = templatel
        self.dump_results()

    def dump_results(self):
        if not os.path.isdir(self.savePath):
            os.makedirs(self.savePath)

        df_templates = pd.DataFrame(
            [
                [self.templates[key]["id"], key, self.templates[key]["count"]]
                for key in self.templates
            ],
            columns=["EventId", "EventTemplate", "Occurrences"],
        )

        df_templates.to_csv(
            os.path.join(self.savePath, self.logname + "_templates.csv"), index=False
        )
        self.df_log.to_csv(
            os.path.join(self.savePath, self.logname + "_structured.csv"), index=False
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
