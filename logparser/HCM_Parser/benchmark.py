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


import sys
sys.path.append("../../")
from logparser.MLParser import LogParser
from logparser.utils import evaluator
import os
import pandas as pd


input_dir = "../../data/loghub_2k/"  # The input directory of log file
output_dir = "MLParser_result/"  # The output directory of parsing results


benchmark_settings = {
    "HDFS": {
        "log_file": "HDFS/HDFS_2k.log",
        "log_format": "<Date> <Time> <Pid> <Level> <Component>: <Content>",
        "regex": [r'(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)'],
        "st": 0.5,
        "tau": 0.57,
        "depth": 4,
        "delimiter_pattern": r"\.|_"
    },
    "Hadoop": {
        "log_file": "Hadoop/Hadoop_2k.log",
        "log_format": "<Date> <Time> <Level> \[<Process>\] <Component>: <Content>",
        "regex": [],
        "st": 0.5,
        "tau": 0.75,
        "depth": 4,
        "delimiter_pattern": r"\.|_"
    },
    "Spark": {
        "log_file": "Spark/Spark_2k.log",
        "log_format": "<Date> <Time> <Level> <Component>: <Content>",
        "regex": [],
        "st": 0.5,
        "tau": 0.75,
        "depth": 4,
        "delimiter_pattern": r"\.|_"
    },
    "Zookeeper": {
        "log_file": "Zookeeper/Zookeeper_2k.log",
        "log_format": "<Date> <Time> - <Level>  \[<Node>:<Component>@<Id>\] - <Content>",
        "regex": [],
        "st": 0.5,
        "tau": 0.75,
        "depth": 4,
        "delimiter_pattern": r"\.|_"
    },
    "BGL": {
        "log_file": "BGL/BGL_2k.log",
        "log_format": "<Label> <Timestamp> <Date> <Node> <Time> <NodeRepeat> <Type> <Component> <Level> <Content>",
        "regex": [],
        "st": 0.5,
        "tau": 0.75,
        "depth": 4,
        "delimiter_pattern": r"\.|_"
    },
    "HPC": {
        "log_file": "HPC/HPC_2k.log",
        "log_format": "<LogId> <Node> <Component> <State> <Time> <Flag> <Content>",
        "regex": [],
        "st": 0.5,
        "tau": 0.75,
        "depth": 4,
        "delimiter_pattern": r"\.|_"
    },
    "Thunderbird": {
        "log_file": "Thunderbird/Thunderbird_2k.log",
        "log_format": "<Label> <Timestamp> <Date> <User> <Month> <Day> <Time> <Location> <Component>(\[<PID>\])?: <Content>",
        "regex": [],
        "st": 0.5,
        "tau": 0.75,
        "depth": 4,
        "delimiter_pattern": r"\.|_"
    },
    "Windows": {
        "log_file": "Windows/Windows_2k.log",
        "log_format": "<Date> <Time>, <Level>                  <Component>    <Content>",
        "regex": [],
        "st": 0.7,
        "tau": 0.75,
        "depth": 5,
        "delimiter_pattern": r"\.|_"
    },
    "Linux": {
        "log_file": "Linux/Linux_2k.log",
        "log_format": "<Month> <Date> <Time> <Level> <Component>(\[<PID>\])?: <Content>",
        "regex": [],
        "st": 0.39,
        "tau": 0.75,
        "depth": 6,
        "delimiter_pattern": r"\.|_"
    },
    "Android": {
        "log_file": "Android/Android_2k.log",
        "log_format": "<Date> <Time>  <Pid>  <Tid> <Level> <Component>: <Content>",
        "regex": [
        ],
        "st": 0.2,
        "tau": 0.75,
        "depth": 6,
        "delimiter_pattern": r"\.|_"
    },
    "HealthApp": {
        "log_file": "HealthApp/HealthApp_2k.log",
        "log_format": "<Time>\|<Component>\|<Pid>\|<Content>",
        "regex": [],
        "st": 0.2,
        "tau": 0.75,
        "depth": 4,
        "delimiter_pattern": ""
    },
    "Apache": {
        "log_file": "Apache/Apache_2k.log",
        "log_format": "\[<Time>\] \[<Level>\] <Content>",
        "regex": [],
        "st": 0.5,
        "tau": 0.75,
        "depth": 4,
        "delimiter_pattern": ""
    },
    "Proxifier": {
        "log_file": "Proxifier/Proxifier_2k.log",
        "log_format": "\[<Time>\] <Program> - <Content>",
        "regex": [],
        "st": 0.6,
        "tau": 0.75,
        "depth": 3,
        "delimiter_pattern": ""
    },
    "OpenSSH": {
        "log_file": "OpenSSH/OpenSSH_2k.log",
        "log_format": "<Date> <Day> <Time> <Component> sshd\[<Pid>\]: <Content>",
        "regex": [],
        "st": 0.6,
        "tau": 0.75,
        "depth": 5,
        "delimiter_pattern": ""
    },
    "OpenStack": {
        "log_file": "OpenStack/OpenStack_2k.log",
        "log_format": "<Logrecord> <Date> <Time> <Pid> <Level> <Component> \[<ADDR>\] <Content>",
        "regex": [],
        "st": 0.5,
        "tau": 0.75,
        "depth": 5,
        "delimiter_pattern": ""
    },
    # "Mac": {
    #     "log_file": "Mac/Mac_2k.log",
    #     "log_format": "<Month>  <Date> <Time> <User> <Component>\[<PID>\]( \(<Address>\))?: <Content>",
    #     "regex": [],
    #     "st": 0.7,
    #     "tau": 0.75,
    #     "depth": 6,
    #     "delimiter_pattern": r"\.|_"
    # },
}

bechmark_result = []
for dataset, setting in benchmark_settings.items():
    print("\n=== Evaluation on %s ===" % dataset)
    indir = os.path.join(input_dir, os.path.dirname(setting["log_file"]))
    log_file = os.path.basename(setting["log_file"])

    parser = LogParser(
        log_format=setting["log_format"],
        indir=indir,
        outdir=output_dir,
        rex=setting["regex"],
        depth=setting["depth"],
        st=setting["st"],
        tau=setting["tau"],
        delimiter_pattern=setting["delimiter_pattern"]
    )
    TimeToken = parser.parse(log_file)

    F1_measure, accuracy, Precision, Recall = evaluator.evaluate(
        groundtruth=os.path.join(indir, log_file + "_structured.csv"),
        parsedresult=os.path.join(output_dir, log_file + "_structured.csv"),
    )
    bechmark_result.append([dataset, F1_measure, accuracy, Precision, Recall, TimeToken])


print("\n=== Overall evaluation results ===")
df_result = pd.DataFrame(bechmark_result, columns=["Dataset", "F1_measure", "Accuracy", "Precision", "Recall", "TimeToken"])
df_result.set_index("Dataset", inplace=True)
print(df_result)
df_result.to_csv("MLParser_bechmark_result.csv", float_format="%.6f")
