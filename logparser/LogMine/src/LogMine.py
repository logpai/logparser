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
from . import alignment
import copy
import hashlib
import pandas as pd
from datetime import datetime
from collections import defaultdict
from tqdm import tqdm


class partition:
    def __init__(self, idx, log="", lev=-1):
        self.logs_idx = [idx]
        self.patterns = [log]
        self.level = lev


class LogParser:
    def __init__(
        self,
        indir,
        outdir,
        log_format,
        max_dist=0.001,
        levels=2,
        k=1,
        k1=1,
        k2=1,
        alpha=100,
        rex=[],
    ):
        self.logformat = log_format
        self.path = indir
        self.savePath = outdir
        self.rex = rex
        self.levels = levels
        self.max_dist = max_dist
        self.k = k
        self.k1 = k1
        self.k2 = k2
        self.alpha = alpha
        self.df_log = None
        self.logname = None
        self.level_clusters = {}

    def parse(self, logname):
        print("Parsing file: " + os.path.join(self.path, logname))
        self.logname = logname
        starttime = datetime.now()
        self.load_data()
        for lev in range(self.levels):
            if lev == 0:
                # Clustering
                self.level_clusters[0] = self.get_clusters(self.df_log["Content_"], lev)
            else:
                # Clustering
                patterns = [c.patterns[0] for c in self.level_clusters[lev - 1]]
                self.max_dist *= self.alpha
                clusters = self.get_clusters(
                    patterns, lev, self.level_clusters[lev - 1]
                )

                # Generate patterns
                for cluster in tqdm(clusters, total=len(clusters)):
                    cluster.patterns = [self.sequential_merge(cluster.patterns)]
                self.level_clusters[lev] = clusters
        self.dump()
        print("Parsing done. [Time taken: {!s}]".format(datetime.now() - starttime))

    def dump(self):
        if not os.path.isdir(self.savePath):
            os.makedirs(self.savePath)

        templates = [0] * self.df_log.shape[0]
        ids = [0] * self.df_log.shape[0]
        templates_occ = defaultdict(int)
        for cluster in self.level_clusters[self.levels - 1]:
            EventTemplate = cluster.patterns[0]
            EventId = hashlib.md5(" ".join(EventTemplate).encode("utf-8")).hexdigest()[
                0:8
            ]
            Occurences = len(cluster.logs_idx)
            templates_occ[EventTemplate] += Occurences

            for idx in cluster.logs_idx:
                ids[idx] = EventId
                templates[idx] = EventTemplate
        self.df_log["EventId"] = ids
        self.df_log["EventTemplate"] = templates

        occ_dict = dict(self.df_log["EventTemplate"].value_counts())
        df_event = pd.DataFrame()
        df_event["EventTemplate"] = self.df_log["EventTemplate"].unique()
        df_event["Occurrences"] = self.df_log["EventTemplate"].map(occ_dict)
        df_event["EventId"] = self.df_log["EventTemplate"].map(
            lambda x: hashlib.md5(x.encode("utf-8")).hexdigest()[0:8]
        )

        self.df_log.drop("Content_", inplace=True, axis=1)
        self.df_log.to_csv(
            os.path.join(self.savePath, self.logname + "_structured.csv"), index=False
        )
        df_event.to_csv(
            os.path.join(self.savePath, self.logname + "_templates.csv"),
            index=False,
            columns=["EventId", "EventTemplate", "Occurrences"],
        )

    def get_clusters(self, logs, lev, old_clusters=None):
        clusters = []
        old_clusters = copy.deepcopy(old_clusters)
        for logidx, log in tqdm(enumerate(logs), total=len(logs)):
            match = False
            for cluster in clusters:
                dis = (
                    self.msgDist(log, cluster.patterns[0])
                    if lev == 0
                    else self.patternDist(log, cluster.patterns[0])
                )
                if dis and dis < self.max_dist:
                    if lev == 0:
                        cluster.logs_idx.append(logidx)
                    else:
                        cluster.logs_idx.extend(old_clusters[logidx].logs_idx)
                        cluster.patterns.append(old_clusters[logidx].patterns[0])
                    match = True

            if not match:
                if lev == 0:
                    clusters.append(partition(logidx, log, lev))  # generate new cluster
                else:
                    old_clusters[logidx].level = lev
                    clusters.append(old_clusters[logidx])  # keep old cluster

        return clusters

    def sequential_merge(self, logs):
        log_merged = logs[0]
        for log in logs[1:]:
            log_merged = self.pair_merge(log_merged, log)
        return log_merged

    def pair_merge(self, loga, logb):
        loga, logb = alignment.water(loga.split(), logb.split())
        logn = []
        for idx, value in enumerate(loga):
            logn.append("<*>" if value != logb[idx] else value)
        return " ".join(logn)

    def print_cluster(self, cluster):
        print("------start------")
        print("level: {}".format(cluster.level))
        print("idxs: {}".format(cluster.logs_idx))
        print("patterns: {}".format(cluster.patterns))
        print("count: {}".format(len(cluster.patterns)))
        for idx in cluster.logs_idx:
            print(self.df_log.iloc[idx]["Content_"])
        print("------end------")

    def msgDist(self, seqP, seqQ):
        dis = 1
        seqP = seqP.split()
        seqQ = seqQ.split()
        maxlen = max(len(seqP), len(seqQ))
        minlen = min(len(seqP), len(seqQ))
        for i in range(minlen):
            dis -= (self.k if seqP[i] == seqQ[i] else 0 * 1.0) / maxlen
        return dis

    def patternDist(self, seqP, seqQ):
        dis = 1
        seqP = seqP.split()
        seqQ = seqQ.split()
        maxlen = max(len(seqP), len(seqQ))
        minlen = min(len(seqP), len(seqQ))
        for i in range(minlen):
            if seqP[i] == seqQ[i]:
                if seqP[i] == "<*>":
                    dis -= self.k2 * 1.0 / maxlen
                else:
                    dis -= self.k1 * 1.0 / maxlen
        return dis

    def load_data(self):
        def preprocess(line):
            for currentRex in self.rex:
                line = re.sub(currentRex, "", line)
            return line

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
