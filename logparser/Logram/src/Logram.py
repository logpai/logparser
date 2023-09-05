"""
This file is modified from:
https://github.com/logpai/LogPub/tree/main/benchmark/logparser/Logram

Copyright (c) 2023 LOGPAI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
"""

import os
from .DictionarySetUp import dictionaryBuilder
from .MatchToken import tokenMatch


class LogParser:
    def __init__(
        self,
        log_format,
        indir="./",
        outdir="./result/",
        doubleThreshold=15,
        triThreshold=10,
        rex=[],
    ):
        self.indir = indir
        self.outdir = outdir
        self.doubleThreshold = doubleThreshold
        self.triThreshold = triThreshold
        self.log_format = log_format
        self.rex = rex

    def parse(self, log_file_basename):
        log_file = os.path.join(self.indir, log_file_basename)
        print("Parsing file: " + log_file)
        (
            doubleDictionaryList,
            triDictionaryList,
            allTokenList,
            allMessageList,
        ) = dictionaryBuilder(self.log_format, log_file, self.rex)
        tokenMatch(
            allTokenList,
            doubleDictionaryList,
            triDictionaryList,
            self.doubleThreshold,
            self.triThreshold,
            self.outdir,
            log_file_basename,
            allMessageList,
        )
        print("Parsing done.")
