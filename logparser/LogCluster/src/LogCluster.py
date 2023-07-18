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
import pandas as pd
import regex as re
import hashlib
from datetime import datetime
import subprocess


class LogParser:
    def __init__(
        self,
        indir,
        log_format,
        outdir,
        rex=[],
        support=None,
        rsupport=None,
        separator=None,
        lfilter=None,
        template=None,
        lcfunc=None,
        syslog=None,
        wsize=None,
        csize=None,
        wweight=None,
        weightf=None,
        wfreq=None,
        wfilter=None,
        wsearch=None,
        wrplace=None,
        wcfunc=None,
        outliers=None,
        readdump=None,
        writedump=None,
        readwords=None,
        writewords=None,
    ):
        """
        Arguments:
            rsupport = < relative_support >
            separator = < word_separator_regexp >
            lfilter = < line_filter_regexp >
            template = < line_conversion_template >
            lcfunc = < perl_code >
            syslog = < syslog_facility >
            wsize = < word_sketch_size >
            csize = < candidate_sketch_size >
            wweight = < word_weight_threshold >
            weightf = < word_weight_function >
            wfreq = < word_frequency_threshold >
            wfilter = < word_filter_regexp >
            wsearch = < word_search_regexp >
            wreplace = < word_replace_string >
            wcfunc = < perl_code >
            outliers = < outlier_file >
            readdump = < dump_file >
            writedump = < dump_file >
            readwords = < word_file >
            writewords = < word_file >
        """
        self.path = indir
        self.log_format = log_format
        self.savepath = outdir
        self.paras = [
            support,
            rsupport,
            separator,
            lfilter,
            template,
            lcfunc,
            syslog,
            wsize,
            csize,
            wweight,
            weightf,
            wfreq,
            wfilter,
            wsearch,
            wrplace,
            wcfunc,
            outliers,
            readdump,
            writedump,
            readwords,
            writewords
        ]
        self.paranames = [
            "support",
            "rsupport",
            "separator",
            "lfilter",
            "template",
            "lcfunc",
            "syslog",
            "wsize",
            "csize",
            "wweight",
            "weightf",
            "wfreq",
            "wfilter",
            "wsearch",
            "wrplace",
            "wcfunc",
            "outliers",
            "readdump",
            "writedump",
            "readwords",
            "writewords"
        ]
        self.perl_command = "perl {} --input {}".format(
            os.path.join(os.path.dirname(__file__), "logcluster.pl"),
            "logcluster_input.log",
        )
        for idx, para in enumerate(self.paras):
            if para:
                self.perl_command += " -{} {}".format(self.paranames[idx], para)
        self.perl_command += " > logcluster_output.txt"
        self.rex = rex

    def parse(self, filename):
        start_time = datetime.now()
        filepath = os.path.join(self.path, filename)
        print("Parsing file: " + filepath)
        self.filename = filename
        headers, regex = self.generate_logformat_regex(self.log_format)
        self.df_log = self.log_to_dataframe(filepath, regex, headers, self.log_format)
        with open("logcluster_input.log", "w") as fw:
            for line in self.df_log["Content"]:
                if self.rex:
                    for currentRex in self.rex:
                        line = re.sub(currentRex, "", line)
                fw.write(line + "\n")
        try:
            print("Run LogCluster command...\n>> {}".format(self.perl_command))
            subprocess.check_call(self.perl_command, shell=True)
        except:
            print("LogCluster run failed! Please check perl installed.\n")
            raise
        self.wirteResultToFile()
        os.remove("logcluster_input.log")
        os.remove("logcluster_output.txt")
        print("Parsing done. [Time taken: {!s}]".format(datetime.now() - start_time))

    def wirteResultToFile(self):
        if not os.path.isdir(self.savepath):
            os.makedirs(self.savepath)

        EventIdx_hash = []
        LineID_EventIdx = {}
        Events = []
        Occurrences = []
        EventIdx = 0
        with open("logcluster_output.txt", "r") as fr:
            for line in fr:
                line = line.split("\t")
                lineNums = line[1].split(",")
                Events.append(line[0].strip())
                EventIdx_hash.append(
                    hashlib.md5(line[0].encode("utf-8")).hexdigest()[0:8]
                )
                Occurrences.append(line[2].strip())
                for num in lineNums:
                    LineID_EventIdx[int(num)] = EventIdx
                EventIdx += 1

        EventTemplate = []
        EventId = []
        for i in range(self.df_log.shape[0]):
            i += 1
            e_idx = LineID_EventIdx.get(i, -1)
            if e_idx != -1:
                EventTemplate.append(Events[e_idx])
                EventId.append(EventIdx_hash[e_idx])
            else:
                content = self.df_log.iloc[i - 1]["Content"]
                EventTemplate.append(content)
                EventId.append(hashlib.md5(content.encode("utf-8")).hexdigest()[0:8])

        self.df_log["EventId"] = EventId
        self.df_log["EventTemplate"] = EventTemplate

        occ_dict = dict(self.df_log["EventTemplate"].value_counts())
        df_event = pd.DataFrame()
        df_event["EventTemplate"] = self.df_log["EventTemplate"].unique()
        df_event["Occurrences"] = df_event["EventTemplate"].map(occ_dict)
        df_event["EventId"] = df_event["EventTemplate"].map(
            lambda x: hashlib.md5(x.encode("utf-8")).hexdigest()[0:8]
        )
        self.df_log.to_csv(
            os.path.join(self.savepath, self.filename + "_structured.csv"), index=False
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
