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

import hashlib
import pandas as pd
import regex as re
from datetime import datetime
from ...logmatch import RegexMatch
import subprocess
import os


class LogParser(object):
    def __init__(
        self, indir, outdir, log_format, support, para_j=True, saveLog=False, rex=[]
    ):
        self.outdir = outdir
        self.log_format = log_format
        self.rex = rex
        self.para = {}
        self.para["dataPath"] = indir
        self.para["para_j"] = para_j
        self.para["savePath"] = outdir
        self.para["support"] = support
        self.para["saveLog"] = saveLog

    def parse(self, logname):
        self.para["dataName"] = logname
        SLCT(self.para, self.log_format, self.rex)


def SLCT(para, log_format, rex):
    startTime = datetime.now()  # start timing
    logname = os.path.join(para["dataPath"], para["dataName"])
    print("Parsing file: {}".format(logname))

    # SLCT compilation
    if not os.path.isfile("../SLCT/slct"):
        try:
            print("Compile SLCT...\n>> gcc -o ./src/slct -O2 ./src/cslct.c")
            subprocess.check_output(
                "gcc -o ./src/slct -O2 ./src/cslct.c",
                stderr=subprocess.STDOUT,
                shell=True,
            )
        except:
            raise "Compile error! Please check GCC installed."

    headers, regex = generate_logformat_regex(log_format)
    df_log = log_to_dataframe(logname, regex, headers, log_format)
    print("load data done.")
    # Generate input file
    with open("slct_input.log", "w") as fw:
        for line in df_log["Content"]:
            if rex:
                for currentRex in rex:
                    line = re.sub(currentRex, "<*>", line)
            fw.write(line + "\n")
    print("modify data done.")
    # Run SLCT command
    SLCT_command = extract_command(para, "slct_input.log")
    try:
        print("Run SLCT...\n>> {}".format(SLCT_command))
        subprocess.check_call(SLCT_command, shell=True)
    except:
        print("SLCT executable is invalid! Please compile it using GCC.\n")
        raise

    # Collect and dump templates
    tempParameter = TempPara(
        path="./", savePath=para["savePath"], logname="slct_input.log"
    )
    tempProcess(tempParameter)
    print("temProcess done!")
    matcher = RegexMatch(outdir=para["savePath"], logformat=log_format)
    matched_df = matcher.match(logname, "temp_templates.csv")
    print("regex match done!")
    # sys.exit()
    os.remove("slct_input.log")
    os.remove("slct_outliers.log")
    os.remove("slct_templates.txt")
    os.remove("temp_templates.csv")

    for idx, line in matched_df.iterrows():
        if line["EventTemplate"] == "None":
            content = line["Content"]
            matched_df.loc[idx, "EventTemplate"] = content
            matched_df.loc[idx, "EventId"] = hashlib.md5(
                content.encode("utf-8")
            ).hexdigest()[0:8]

    occ_dict = dict(matched_df["EventTemplate"].value_counts())
    df_event = pd.DataFrame()
    df_event["EventTemplate"] = matched_df["EventTemplate"].unique()
    df_event["EventId"] = df_event["EventTemplate"].map(
        lambda x: hashlib.md5(x.encode("utf-8")).hexdigest()[0:8]
    )
    df_event["Occurrences"] = df_event["EventTemplate"].map(occ_dict)

    df_event.to_csv(
        os.path.join(para["savePath"], para["dataName"] + "_templates.csv"),
        index=False,
        columns=["EventId", "EventTemplate", "Occurrences"],
    )
    matched_df.to_csv(
        os.path.join(para["savePath"], para["dataName"] + "_structured.csv"),
        index=False,
    )
    print("Parsing done. [Time: {!s}]".format(datetime.now() - startTime))


def extract_command(para, logname):
    support = para["support"]
    parajTF = para["para_j"]
    input = ""

    if parajTF:
        input = (
            "./src/slct -j -o "
            + "slct_outliers.log -r -s "
            + str(support)
            + " "
            + logname
        )
    else:
        input = (
            "./src/slct -o " + "slct_outliers.log -r -s " + str(support) + " " + logname
        )
    return input


def log_to_dataframe(log_file, regex, headers, logformat):
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


def generate_logformat_regex(logformat):
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


class TempPara:
    def __init__(
        self,
        path="./",
        logname="rawlog.log",
        savePath="./",
        templateName="slct_templates.txt",
        outlierName="slct_outliers.log",
    ):
        self.path = path
        self.logname = logname
        self.savePath = savePath
        self.templateName = templateName
        self.outlierName = outlierName


def tempProcess(tempPara):
    print("Dumping event templates...")
    if not os.path.exists(tempPara.savePath):
        os.makedirs(tempPara.savePath)

    # read the templates
    templates = []
    with open("./" + tempPara.templateName) as tl:
        for line in tl:
            templates.append([0, line.strip(), 0])

    pd.DataFrame(templates, columns=["EventId", "EventTemplate", "Occurrences"]).to_csv(
        "temp_templates.csv", index=False
    )


def matchTempLog(templates, logs):
    len_temp = {}
    for tidx, temp in enumerate(templates):
        tempL = temp.split()
        templen = len(tempL)
        if templen not in len_temp:
            len_temp[templen] = [(tidx, tempL)]
        else:
            len_temp[templen].append((tidx, tempL))
    logid_groupid = []
    for idx, log in enumerate(logs):
        logL = log.split()
        logid = idx + 1
        if len(logL) in len_temp:
            logid_groupid.append([idx + 1, get_groupid(logL, len_temp[len(logL)])])
        else:
            logid_groupid.append([idx + 1, -1])

    return logid_groupid


def get_groupid(logL, tempLs):
    maxvalue = -1
    for templ in tempLs:
        starnum = 0
        shot = 0
        for idx, token in enumerate(logL):
            if token == templ[1][idx] or templ[1][idx].count("*"):
                shot += 1
            if templ[1][idx].count("*"):
                starnum += 1
        shot = shot - starnum
        if shot > maxvalue:
            maxvalue = shot
            groupid = templ[0]
    return groupid
