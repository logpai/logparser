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
from logparser.Contrast import Drain
from logparser.Contrast import Drain_A
from logparser.Contrast import Spell
from logparser.Contrast import Spell_A
from logparser.Contrast import HLM_Parser
from logparser.Contrast import HLM_Parser_S
from logparser.utils import evaluator
import os
import pandas as pd


input_dir = "../../data/loghub_2k/"  # The input directory of log file
output_dir = "Contrast_result/"  # The output directory of parsing results


benchmark_settings = {
    "HDFS": {
        "log_file": "HDFS/HDFS_2k.log",
        "log_format": "<Date> <Time> <Pid> <Level> <Component>: <Content>",
        "regex": [r"(\d+\.){3}\d+(:\d+)?"],
        "st": 0.5,
        "depth": 4,
        "tau": 0.7,
        "delimiter_pattern": r"\.|/|_|-"
    },
    # "Hadoop": {
    #     "log_file": "Hadoop/Hadoop_2k.log",
    #     "log_format": "<Date> <Time> <Level> \[<Process>\] <Component>: <Content>",
    #     "regex": [r"(\d+\.){3}\d+"],
    #     "st": 0.5,
    #     "depth": 4,
    #     "tau": 0.7,
    #     "delimiter_pattern": r"\.|/|_"
    # },
    # "Spark": {
    #     "log_file": "Spark/Spark_2k.log",
    #     "log_format": "<Date> <Time> <Level> <Component>: <Content>",
    #     "regex": [r"(\d+\.){3}\d+", r"\b[KGTM]?B\b", r"([\w-]+\.){2,}[\w-]+"],
    #     "st": 0.5,
    #     "depth": 4,
    # },
    # "Zookeeper": {
    #     "log_file": "Zookeeper/Zookeeper_2k.log",
    #     "log_format": "<Date> <Time> - <Level>  \[<Node>:<Component>@<Id>\] - <Content>",
    #     "regex": [r"(/|)(\d+\.){3}\d+(:\d+)?"],
    #     "st": 0.5,
    #     "depth": 4,
    # },
    # "BGL": {
    #     "log_file": "BGL/BGL_2k.log",
    #     "log_format": "<Label> <Timestamp> <Date> <Node> <Time> <NodeRepeat> <Type> <Component> <Level> <Content>",
    #     "regex": [r"core\.\d+"],
    #     "st": 0.5,
    #     "depth": 4,
    #     "tau": 0.75,
    #     "delimiter_pattern": r"\.|/|_"
    # },
    # "HPC": {
    #     "log_file": "HPC/HPC_2k.log",
    #     "log_format": "<LogId> <Node> <Component> <State> <Time> <Flag> <Content>",
    #     "regex": [r"=\d+"],
    #     "st": 0.5,
    #     "depth": 4,
    # },
    # "Thunderbird": {
    #     "log_file": "Thunderbird/Thunderbird_2k.log",
    #     "log_format": "<Label> <Timestamp> <Date> <User> <Month> <Day> <Time> <Location> <Component>(\[<PID>\])?: <Content>",
    #     "regex": [r"(\d+\.){3}\d+"],
    #     "st": 0.5,
    #     "depth": 4,
    # },
    # "Windows": {
    #     "log_file": "Windows/Windows_2k.log",
    #     "log_format": "<Date> <Time>, <Level>                  <Component>    <Content>",
    #     "regex": [r"0x.*?\s"],
    #     "st": 0.7,
    #     "depth": 5,
    # },
    # "Linux": {
    #     "log_file": "Linux/Linux_2k.log",
    #     "log_format": "<Month> <Date> <Time> <Level> <Component>(\[<PID>\])?: <Content>",
    #     "regex": [r"(\d+\.){3}\d+", r"\d{2}:\d{2}:\d{2}"],
    #     "st": 0.39,
    #     "depth": 6,
    # },
    # "Android": {
    #     "log_file": "Android/Android_2k.log",
    #     "log_format": "<Date> <Time>  <Pid>  <Tid> <Level> <Component>: <Content>",
    #     "regex": [
    #         r"(/[\w-]+)+",
    #         r"([\w-]+\.){2,}[\w-]+",
    #         r"\b(\-?\+?\d+)\b|\b0[Xx][a-fA-F\d]+\b|\b[a-fA-F\d]{4,}\b",
    #     ],
    #     "st": 0.2,
    #     "depth": 6,
    # },
    # "HealthApp": {
    #     "log_file": "HealthApp/HealthApp_2k.log",
    #     "log_format": "<Time>\|<Component>\|<Pid>\|<Content>",
    #     "regex": [],
    #     "st": 0.2,
    #     "depth": 4,
    # },
    # "Apache": {
    #     "log_file": "Apache/Apache_2k.log",
    #     "log_format": "\[<Time>\] \[<Level>\] <Content>",
    #     "regex": [r"(\d+\.){3}\d+"],
    #     "st": 0.5,
    #     "depth": 4,
    # },
    # "Proxifier": {
    #     "log_file": "Proxifier/Proxifier_2k.log",
    #     "log_format": "\[<Time>\] <Program> - <Content>",
    #     "regex": [
    #         r"<\d+\ssec",
    #         r"([\w-]+\.)+[\w-]+(:\d+)?",
    #         r"\d{2}:\d{2}(:\d{2})*",
    #         r"[KGTM]B",
    #     ],
    #     "st": 0.6,
    #     "depth": 3,
    # },
    # "OpenSSH": {
    #     "log_file": "OpenSSH/OpenSSH_2k.log",
    #     "log_format": "<Date> <Day> <Time> <Component> sshd\[<Pid>\]: <Content>",
    #     "regex": [r"(\d+\.){3}\d+", r"([\w-]+\.){2,}[\w-]+"],
    #     "st": 0.6,
    #     "depth": 5,
    # },
    # "OpenStack": {
    #     "log_file": "OpenStack/OpenStack_2k.log",
    #     "log_format": "<Logrecord> <Date> <Time> <Pid> <Level> <Component> \[<ADDR>\] <Content>",
    #     #"regex": [r"((\d+\.){3}\d+,?)+", r"/.+?\s", r"\d+"],
    #     "regex": [
    #         r"((\d+\.){3}\d+,?)+",
    #         r"/.+?\s",
    #         r"\d+",
    #         # r"(\[instance:\s*)[^]]+(\])"
    #     ],
    #     "st": 0.5,
    #     "depth": 5,
    #     "tau": 0.9,
    #     "delimiter_pattern": r"\.|/|_"
    # },
    # "Mac": {
    #     "log_file": "Mac/Mac_2k.log",
    #     "log_format": "<Month>  <Date> <Time> <User> <Component>\[<PID>\]( \(<Address>\))?: <Content>",
    #     "regex": [r"([\w-]+\.){2,}[\w-]+"],
    #     "st": 0.7,
    #     "depth": 6,
    # },
}

def Drain_Parser():
    # Drain
    parser_Drain = Drain(
        log_format=setting["log_format"],
        indir=indir,
        outdir=output_dir,
        rex=setting["regex"],
        depth=setting["depth"],
        st=setting["st"],
    )
    TimeToken = parser_Drain.parse(log_file)
    F1_measure, accuracy, Precision, Recall = evaluator.evaluate(
        groundtruth=os.path.join(indir, log_file + "_structured.csv"),
        parsedresult=os.path.join(output_dir, log_file + "_Drain" + "_structured.csv"),
    )

    bechmark_result.append([Drain.__name__, dataset, F1_measure, accuracy, Precision, Recall, TimeToken])

def Drain_A_Parser():
    # Drain_A
    parser_Drain_A = Drain_A(
        log_format=setting["log_format"],
        indir=indir,
        outdir=output_dir,
        rex=setting["regex"],
        depth=setting["depth"],
        st=setting["st"],
        delimiter_pattern=setting["delimiter_pattern"]
    )
    TimeToken = parser_Drain_A.parse(log_file)
    F1_measure, accuracy, Precision, Recall = evaluator.evaluate(
        groundtruth=os.path.join(indir, log_file + "_structured.csv"),
        parsedresult=os.path.join(output_dir, log_file + "_Drain" + "_structured.csv"),
    )

    bechmark_result.append([Drain_A.__name__, dataset, F1_measure, accuracy, Precision, Recall, TimeToken])


def Spell_Parser():
    # Spell
    parser_Spell = Spell(
        log_format=setting["log_format"],
        indir=indir,
        outdir=output_dir,
        rex=setting["regex"],
        tau=setting["tau"],
    )
    TimeToken = parser_Spell.parse(log_file)
    F1_measure, accuracy, Precision, Recall = evaluator.evaluate(
        groundtruth=os.path.join(indir, log_file + "_structured.csv"),
        parsedresult=os.path.join(output_dir, log_file + "_Spell" + "_structured.csv"),
    )

    bechmark_result.append([Spell.__name__, dataset, F1_measure, accuracy, Precision, Recall, TimeToken])

def Spell_A_Parser():
    # Spell
    parser_Spell_A = Spell_A(
        log_format=setting["log_format"],
        indir=indir,
        outdir=output_dir,
        rex=setting["regex"],
        tau=setting["tau"],
    )
    TimeToken = parser_Spell_A.parse(log_file)
    F1_measure, accuracy, Precision, Recall = evaluator.evaluate(
        groundtruth=os.path.join(indir, log_file + "_structured.csv"),
        parsedresult=os.path.join(output_dir, log_file + "_Spell_A" + "_structured.csv"),
    )

    bechmark_result.append([Spell_A.__name__, dataset, F1_measure, accuracy, Precision, Recall, TimeToken])


def HLM_Parser_Parser():
    # Spell
    parser_HLM_Parser = HLM_Parser(
        log_format=setting["log_format"],
        indir=indir,
        outdir=output_dir,
        rex=setting["regex"],
        depth=setting["depth"],
        st=setting["st"],
        tau=setting["tau"],
        delimiter_pattern=setting["delimiter_pattern"]
    )
    TimeToken = parser_HLM_Parser.parse(log_file)
    F1_measure, accuracy, Precision, Recall = evaluator.evaluate(
        groundtruth=os.path.join(indir, log_file + "_structured.csv"),
        parsedresult=os.path.join(output_dir, log_file + "_HLM_Parser" + "_structured.csv"),
    )

    bechmark_result.append([HLM_Parser.__name__, dataset, F1_measure, accuracy, Precision, Recall, TimeToken])


def HLM_Parser_S_Parser():
    # Spell
    parser_HLM_Parser_S = HLM_Parser_S(
        log_format=setting["log_format"],
        indir=indir,
        outdir=output_dir,
        rex=setting["regex"],
        depth=setting["depth"],
        st=setting["st"],
        tau=setting["tau"],
        delimiter_pattern=setting["delimiter_pattern"]
    )
    TimeToken = parser_HLM_Parser_S.parse(log_file)
    F1_measure, accuracy, Precision, Recall = evaluator.evaluate(
        groundtruth=os.path.join(indir, log_file + "_structured.csv"),
        parsedresult=os.path.join(output_dir, log_file + "_HLM_Parser_S" + "_structured.csv"),
    )

    bechmark_result.append([HLM_Parser_S.__name__, dataset, F1_measure, accuracy, Precision, Recall, TimeToken])


bechmark_result = []
for dataset, setting in benchmark_settings.items():
    print("\n=== Evaluation on %s ===" % dataset)
    indir = os.path.join(input_dir, os.path.dirname(setting["log_file"]))
    log_file = os.path.basename(setting["log_file"])
    Drain_Parser()
    Spell_Parser()
    HLM_Parser_S_Parser()
    Drain_A_Parser()
    # Spell_A_Parser()
    HLM_Parser_Parser()



print("\n=== Overall evaluation results ===")
df_result = pd.DataFrame(bechmark_result,
                         columns=["Algorithm", "Dataset", "F1_measure", "Accuracy", "Precision", "Recall", "TimeToken"])
df_result.set_index("Dataset", inplace=True)
print(df_result)
df_result.to_csv("bechmark_result_HDFS.csv", float_format="%.6f")







