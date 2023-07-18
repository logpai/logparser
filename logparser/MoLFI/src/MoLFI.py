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
import hashlib
from ...utils import logloader
from .main.org.core.utility.Chromosome_Generator import ChromosomeGenerator
from .main.org.core.utility.log_message_adaptation import adapt_log_message
from .main.org.core.utility.match_utility import match
from .main.org.core.metaheuristics.NSGA_II_2D import main
from datetime import datetime


class LogParser:
    def __init__(self, indir, outdir, log_format, rex=[], n_workers=1):
        self.input_dir = indir
        self.output_dir = outdir
        self.log_format = log_format
        self.rex = rex
        self.n_workers = n_workers
        self.templates = []

        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir)

    def match_df(self, content):
        msg = adapt_log_message(content, self.rex)
        for template in self.templates:
            if match(msg, template):
                return " ".join(template.token)

    def parse(self, log_file):
        starttime = datetime.now()
        loader = logloader.LogLoader(self.log_format, self.n_workers)
        log_dataframe = loader.load_to_dataframe(os.path.join(self.input_dir, log_file))
        chrom_gen = ChromosomeGenerator(log_dataframe, self.rex)
        pareto = main(chrom_gen)
        for _, solution in pareto.items():
            for _, templates in solution.templates.items():
                self.templates.extend(templates)
            break
        log_dataframe["EventTemplate"] = log_dataframe["Content"].map(self.match_df)
        log_dataframe["EventId"] = log_dataframe["EventTemplate"].map(
            lambda x: hashlib.md5(x.encode("utf-8")).hexdigest()[0:8]
        )

        occ_dict = dict(log_dataframe["EventTemplate"].value_counts())
        df_event = pd.DataFrame()
        df_event["EventTemplate"] = log_dataframe["EventTemplate"].unique()
        df_event["Occurrences"] = df_event["EventTemplate"].map(occ_dict)
        df_event["EventId"] = df_event["EventTemplate"].map(
            lambda x: hashlib.md5(x.encode("utf-8")).hexdigest()[0:8]
        )
        df_event.to_csv(
            os.path.join(self.output_dir, log_file + "_templates.csv"),
            index=False,
            columns=["EventId", "EventTemplate", "Occurrences"],
        )
        log_dataframe.to_csv(
            os.path.join(self.output_dir, log_file + "_structured.csv"), index=False
        )
        print("Parsing done. [Time taken: {!s}]".format(datetime.now() - starttime))
