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
"""This file implements the formating interface to load log file to dataframe"""

import multiprocessing as mp
from itertools import groupby, count, chain
import pandas as pd
import regex as re
import numpy as np


class LogLoader(object):
    def __init__(self, logformat, n_workers=1):
        if not logformat:
            raise RuntimeError("Logformat is required!")
        self.logformat = logformat.strip()
        self.headers, self.regex = self._generate_logformat_regex(self.logformat)
        self.n_workers = n_workers

    def load_to_dataframe(self, log_filepath):
        """Function to transform log file to dataframe"""
        print("Loading log messages to dataframe...")
        lines = []
        with open(log_filepath, "r") as fid:
            lines = fid.readlines()

        log_messages = []
        if self.n_workers == 1:
            log_messages = formalize_message(enumerate(lines), self.regex, self.headers)
        else:
            chunk_size = np.ceil(len(lines) / float(self.n_workers))
            chunks = groupby(
                enumerate(lines), key=lambda k, line=count(): next(line) // chunk_size
            )
            log_chunks = [list(chunk) for _, chunk in chunks]
            print("Read %d log chunks in parallel" % len(log_chunks))
            pool = mp.Pool(processes=self.n_workers)
            result_chunks = [
                pool.apply_async(
                    formalize_message, args=(chunk, self.regex, self.headers)
                )
                for chunk in log_chunks
            ]
            pool.close()
            pool.join()
            log_messages = list(chain(*[result.get() for result in result_chunks]))

        if not log_messages:
            raise RuntimeError("Logformat error or log file is empty!")
        log_dataframe = pd.DataFrame(log_messages, columns=["LineId"] + self.headers)
        success_rate = len(log_messages) / float(len(lines))
        print(
            "Loading {} messages done, loading rate: {:.1%}".format(
                len(log_messages), success_rate
            )
        )
        return log_dataframe

    def _generate_logformat_regex(self, logformat):
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


def formalize_message(enumerated_lines, regex, headers):
    log_messages = []
    for line_count, line in enumerated_lines:
        line = line.strip()
        if not line:
            continue
        line = re.sub(r"[^\x00-\x7F]+", "<N/ASCII>", line)
        try:
            match = regex.search(line)
            message = [match.group(header) for header in headers]
            message.insert(0, line_count + 1)
            log_messages.append(message)
        except Exception as e:
            print("Skip line: " + line)
    return log_messages
