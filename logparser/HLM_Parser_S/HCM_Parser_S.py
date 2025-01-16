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
import pandas as pd
import hashlib
from datetime import datetime


class LogCluster:
    def __init__(self, logTemplate="", logIDL=None):
        self.logTemplate = logTemplate
        if logIDL is None:
            logIDL = []
        self.logIDL = logIDL

class LCSNode:
    """A node in prefix tree data structure"""
    def __init__(self, token="", templateNo=0):
        self.logClust = None
        self.token = token
        self.templateNo = templateNo
        self.childD = dict()

class HamNode:
    def __init__(self, childD=None, depth=0, digitOrtoken=None):
        if childD is None:
            childD = dict()
        self.childD = childD
        self.depth = depth
        self.digitOrtoken = digitOrtoken


class LogParser:
    def __init__(
        self,
        log_format,
        indir="./",
        outdir="./result/",
        depth=4,
        st=0.4,
        maxChild=100,
        tau=0.5,
        rex=[],
        delimiter_pattern="",
        keep_para=True,
    ):
        """
        Attributes
        ----------
            rex : regular expressions used in preprocessing (step1)
            path : the input path stores the input log file name
            depth : depth of all leaf nodes
            st : similarity threshold
            maxChild : max number of children of an internal node
            logName : the name of the input file containing raw log messages
            savePath : the output path stores the file containing structured logs
        """
        self.path = indir
        self.depth = depth - 2
        self.st = st
        self.maxChild = maxChild
        self.logName = None
        self.savePath = outdir
        self.df_log = None
        self.log_format = log_format
        self.tau = tau
        self.rex = rex
        self.delimiter_pattern = delimiter_pattern
        self.keep_para = keep_para

    #  用于检查字符串 s 是否包含数字。
    def hasNumbers(self, s):
        return any(char.isdigit() for char in s)

    # seq1 is template Ham相似度
    def seqDist(self, seq1, seq2):
        assert len(seq1) == len(seq2)
        simTokens = 0
        numOfPar = 0

        for token1, token2 in zip(seq1, seq2):
            if token1 == "<*>":
                numOfPar += 1
                continue
            if token1 == token2:
                simTokens += 1

        retVal = float(simTokens) / len(seq1)

        return retVal, numOfPar

    def fastMatch(self, logClustL, seq):
        retLogClust = None

        maxSim = -1
        maxNumOfPara = -1
        maxClust = None

        for logClust in logClustL:
            curSim, curNumOfPara = self.seqDist(logClust.logTemplate, seq)
            if curSim > maxSim or (curSim == maxSim and curNumOfPara > maxNumOfPara):
                maxSim = curSim
                maxNumOfPara = curNumOfPara
                maxClust = logClust

        if maxSim >= self.st:
            retLogClust = maxClust

        return retLogClust

    '''
        入参：rootNode, logmessageL
        从 rootNode 中，找到 logmessageL的模版
    '''
    def treeSearch(self, rn, seq):
        retLogClust = None

        seqLen = len(seq)
        if seqLen not in rn.childD:
            return retLogClust

        # 先查找第一层，根据长度查找
        parentn = rn.childD[seqLen]

        currentDepth = 1
        # 对每一个Seq 的 token进行查找，如果第一层找到，就进行第二层查找。
        for token in seq:
            if currentDepth >= self.depth or currentDepth > seqLen:
                break

            if token in parentn.childD:
                parentn = parentn.childD[token]
            elif "<*>" in parentn.childD:
                parentn = parentn.childD["<*>"]
            else:
                return retLogClust
            currentDepth += 1

        logClustL = parentn.childD

        # 计算相似度， 通过Ham相似度进行查找，如果大于阈值，停止查找
        retLogClust = self.fastMatch(logClustL, seq)

        return retLogClust

    '''
        向Drain树中增加节点
        self.addSeqToPrefixTree(rootNode, newCluster)
    '''
    def addSeqToPrefixHamTree(self, rn, logClust):
        seqLen = len(logClust.logTemplate)
        if seqLen not in rn.childD:
            # 如果没有相应长度， 则新增一个长度
            firtLayerNode = HamNode(depth=1, digitOrtoken=seqLen)
            rn.childD[seqLen] = firtLayerNode
        else:
            firtLayerNode = rn.childD[seqLen]

        # 找到相应长度下面的节点
        parentn = firtLayerNode

        currentDepth = 1
        for token in logClust.logTemplate:
            # Add current log cluster to the leaf node
            # 如果当前深度大于之前定义深度，或者当前深度大于模版长度， 则进入判断。进入之后，判断当前节点的childD是否为空，不为空则追加，为空则直接插入。
            if currentDepth >= self.depth or currentDepth > seqLen:
                if len(parentn.childD) == 0:
                    parentn.childD = [logClust]
                else:
                    parentn.childD.append(logClust)
                break

            # If token not matched in this layer of existing tree.
            '''
                遍历logClust.logTemplate 的每个token, 
                如果遍历到当前token在 parentn.childD中，则深度加一，然后进入下一层循环（深度加一），判断下一个token；
                如果当前token不存在，则进行增加。增加又分为一下两种方式。
                    当前token不带数字
                        不带数字又分为两种情况：
                            当前parentn.childD有<*> 和 没有<*>
                                有<*> 
                                 判断孩子节点+1是否小于之前定义的maxChild, 如果小于，则在下一层新增token
                                 如果大于，则就把<*>当成父节点
                                无<*>
                                 判断孩子节点+1是否小于之前定义的maxChild, 如果小于，则在下一层新增token
                                 判断孩子节点+1是否小于之前定义的maxChild, 如果等于，则在下一层新增<*>
                                 判断孩子节点+1是否小于之前定义的maxChild, 如果大于，则返回父节点<*>
                                  
                    当前token带数字
                        带数字的话，查找当前parentn中的 childD 是否有"<*>", 如果有的话，parentn = parentn.childD["<*>"]
                        如果没有的话， 则新建一个节点，增加<*>节点
                        newNode = Node(depth=currentDepth + 1, digitOrtoken="<*>")
                        parentn.childD["<*>"] = newNode
                        parentn = newNode
                    
            '''
            if token not in parentn.childD:
                if not self.hasNumbers(token):
                    if "<*>" in parentn.childD:
                        if len(parentn.childD) < self.maxChild:
                            newNode = HamNode(depth=currentDepth + 1, digitOrtoken=token)
                            parentn.childD[token] = newNode
                            parentn = newNode
                        else:
                            parentn = parentn.childD["<*>"]
                    else:
                        if len(parentn.childD) + 1 < self.maxChild:
                            newNode = HamNode(depth=currentDepth + 1, digitOrtoken=token)
                            parentn.childD[token] = newNode
                            parentn = newNode
                        elif len(parentn.childD) + 1 == self.maxChild:
                            newNode = HamNode(depth=currentDepth + 1, digitOrtoken="<*>")
                            parentn.childD["<*>"] = newNode
                            parentn = newNode
                        else:
                            parentn = parentn.childD["<*>"]

                else:
                    if "<*>" not in parentn.childD:
                        newNode = HamNode(depth=currentDepth + 1, digitOrtoken="<*>")
                        parentn.childD["<*>"] = newNode
                        parentn = newNode
                    else:
                        parentn = parentn.childD["<*>"]

            # If the token is matched
            else:
                parentn = parentn.childD[token]  # 判断下一个token使用

            currentDepth += 1

    '''
        getTemplate 方法生成一个模板列表，其中比较两个输入序列，相同位置的元素相等则保留，不相等则替换为占位符 "<*>"
        self.getTemplate(logmessageL, matchCluster.logTemplate)
    '''
    def getTemplateHam(self, seq1, seq2):
        assert len(seq1) == len(seq2)
        retVal = []

        i = 0
        for word in seq1:
            if word == seq2[i]:
                retVal.append(word)
            else:
                retVal.append(self.process_strings(word, seq2[i]))

            i += 1

        return retVal

    def outputResult(self, logClustL):
        log_templates = [0] * self.df_log.shape[0]
        log_templateids = [0] * self.df_log.shape[0]
        df_events = []
        for logClust in logClustL:
            template_str = " ".join(logClust.logTemplate)
            occurrence = len(logClust.logIDL)
            '''
            这行代码的作用是生成一个基于给定字符串的 MD5 哈希值的 8 位十六进制字符串。下面是每个部分的详细解释：
            template_str.encode("utf-8")：将字符串 template_str 使用 UTF-8 编码转换为字节对象。这是因为 MD5 哈希函数需要一个字节对象作为输入。
            hashlib.md5(...).hexdigest()：使用 hashlib 模块生成 MD5 哈希值，并将其转换为十六进制字符串表示。
            [0:8]：截取生成的十六进制哈希值的前 8 个字符。
            总结来说，这行代码的目的是基于输入字符串 template_str 生成一个唯一的 8 位标识符 template_id
            '''
            template_id = hashlib.md5(template_str.encode("utf-8")).hexdigest()[0:8]
            for logID in logClust.logIDL:
                logID -= 1
                log_templates[logID] = template_str
                log_templateids[logID] = template_id
            df_events.append([template_id, template_str, occurrence])

        df_event = pd.DataFrame(
            df_events, columns=["EventId", "EventTemplate", "Occurrences"]
        )
        self.df_log["EventId"] = log_templateids
        self.df_log["EventTemplate"] = log_templates
        if self.keep_para:
            self.df_log["ParameterList"] = self.df_log.apply(
                self.get_parameter_list, axis=1
            )
        self.df_log.to_csv(
            os.path.join(self.savePath, self.logName + "_structured.csv"), index=False
        )

        occ_dict = dict(self.df_log["EventTemplate"].value_counts())
        df_event = pd.DataFrame()
        df_event["EventTemplate"] = self.df_log["EventTemplate"].unique()
        df_event["EventId"] = df_event["EventTemplate"].map(
            lambda x: hashlib.md5(x.encode("utf-8")).hexdigest()[0:8]
        )
        df_event["Occurrences"] = df_event["EventTemplate"].map(occ_dict)
        df_event.to_csv(
            os.path.join(self.savePath, self.logName + "_templates.csv"),
            index=False,
            columns=["EventId", "EventTemplate", "Occurrences"],
        )

    def printTree(self, node, dep):
        pStr = ""
        for i in range(dep):
            pStr += "\t"

        if node.depth == 0:
            pStr += "Root"
        elif node.depth == 1:
            pStr += "<" + str(node.digitOrtoken) + ">"
        else:
            pStr += node.digitOrtoken

        print(pStr)

        if node.depth == self.depth:
            return 1
        for child in node.childD:
            self.printTree(node.childD[child], dep + 1)

    def load_data(self):
        headers, regex = self.generate_logformat_regex(self.log_format)
        self.df_log = self.log_to_dataframe(
            os.path.join(self.path, self.logName), regex, headers, self.log_format
        )

    '''
        通过遍历正则表达式列表并替换匹配的部分，这段代码实现了日志行的归一化处理，将日志行中的动态内容替换为通配符 <*>。
        这有助于在后续的日志分析和模板挖掘中发现日志消息的结构化模式。
        预处理
    '''
    def preprocess(self, line):
        for currentRex in self.rex:
            line = re.sub(currentRex, "<*>", line)
        return line

    def log_to_dataframe(self, log_file, regex, headers, logformat):
        """Function to transform log file to dataframe"""
        log_messages = []
        linecount = 0
        with open(log_file, "r") as fin:
            for line in fin.readlines():
                line = re.sub(r"[^\x00-\x7F]+", "<NASCII>", line)
                try:
                    match = regex.search(line.strip())
                    message = [match.group(header) for header in headers]
                    log_messages.append(message)
                    linecount += 1
                except Exception as e:
                    print("[Warning] Skip line: " + line)
        logdf = pd.DataFrame(log_messages, columns=headers)
        logdf.insert(0, "LineId", None)
        logdf["LineId"] = [i + 1 for i in range(linecount)]
        print("Total lines: ", len(logdf))
        return logdf

    def generate_logformat_regex(self, logformat):
        """Function to generate regular expression to split log messages"""
        headers = []
        '''
            通过将 logformat 按照占位符拆分为若干部分，可以更方便地处理日志格式，提取日志中的各个字段。
            随后可以使用这些部分生成正则表达式，用于解析具体的日志条目。
            log_format = '<Date> <Time> <Pid> <Level> <Component>: <Content>'
            拆分结果 splitters 将是：
            ['', '<Date>', ' ', '<Time>', ' ', '<Pid>', ' ', '<Level>', ' ', '<Component>', ': ', '<Content>', '']
        '''
        splitters = re.split(r"(<[^<>]+>)", logformat)
        regex = ""
        for k in range(len(splitters)):
            if k % 2 == 0:
                splitter = re.sub(" +", "\\\s+", splitters[k])
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

    def split_string_preserve_delimiters(self, s):
        # 分割字符串，使用非字母和数字字符进行划分，并保留所有分隔符
        # return re.split(r'([^\w*])', s)
        # return re.split(r'([^a-zA-Z0-9*])', s)  # 使用捕获组保留分隔符
        """
        分割字符串，使用指定的分隔符模式划分，并保留所有分隔符。
        如果字符串中没有分隔符，返回包含原始字符串的列表。
        """
        # 使用捕获组进行分割
        if not self.delimiter_pattern:
            return [s]
        result = re.split(f"({self.delimiter_pattern})", s)

        # 如果结果为空或仅包含空字符串，返回原字符串作为单元素列表
        return [s] if not result or all(not part for part in result) else result

    def LCS(self, seq1, seq2):
        lengths = [[0 for j in range(len(seq2) + 1)] for i in range(len(seq1) + 1)]
        # row 0 and column 0 are initialized to 0 already
        for i in range(len(seq1)):
            for j in range(len(seq2)):
                if seq1[i] == seq2[j]:
                    lengths[i + 1][j + 1] = lengths[i][j] + 1
                else:
                    lengths[i + 1][j + 1] = max(lengths[i + 1][j], lengths[i][j + 1])

        # read the substring out from the matrix
        result = []
        lenOfSeq1, lenOfSeq2 = len(seq1), len(seq2)
        while lenOfSeq1 != 0 and lenOfSeq2 != 0:
            if lengths[lenOfSeq1][lenOfSeq2] == lengths[lenOfSeq1 - 1][lenOfSeq2]:
                lenOfSeq1 -= 1
            elif lengths[lenOfSeq1][lenOfSeq2] == lengths[lenOfSeq1][lenOfSeq2 - 1]:
                lenOfSeq2 -= 1
            else:
                assert seq1[lenOfSeq1 - 1] == seq2[lenOfSeq2 - 1]
                result.insert(0, seq1[lenOfSeq1 - 1])
                lenOfSeq1 -= 1
                lenOfSeq2 -= 1
        return result

    def getCommonTemplate(self, lcs, seq):
        retVal = []
        if not lcs:
            return retVal

        # 因为在 seq 中从左到右进行匹配，而 lcs 是按从后向前回溯生成的，需要反转顺序以便匹配。
        lcs = lcs[::-1]
        i = 0
        # 如果当前 token 等于 lcs 的最后一个元素（lcs[-1]），将其加入模板，并从 lcs 中移除该元素。
        # 如果不匹配，添加占位符 <*>。
        for token in seq:
            i += 1
            if token == lcs[-1]:
                retVal.append(token)
                lcs.pop()
            else:
                retVal.append("<*>")
            if not lcs:
                break
        if i < len(seq):
            retVal.append("<*>")
        return "".join(self.compress_repeated_delimiters(retVal))

    def compress_repeated_delimiters(self, lcs):
        """
        合并连续相同的字符（例如多个 '/' 合并为一个 '/'）
        """
        if not lcs:
            return []

        compressed = [lcs[0]]  # 初始化结果数组，包含第一个元素
        for i in range(1, len(lcs)):
            # 如果当前字符和前一个字符不同，添加到结果中
            if lcs[i] != lcs[i - 1]:
                compressed.append(lcs[i])
        return compressed

    def process_strings(self, str1, str2):
        """
        主函数，处理两个字符串
        """
        if str1 == str2:
            return str1
        # 切割字符串
        rexStr2 = re.sub(r'<\*>', '', str2)
        split2 = self.split_string_preserve_delimiters(rexStr2)
        split1 = self.split_string_preserve_delimiters(str1)
        if len(split2) == 1 or len(split1) == 1:
            return "<*>"

        split1 = list(filter(None, split1))
        split2 = list(filter(None, split2))

        # 找到最长公共子序列
        lcs = list(filter(None, self.compress_repeated_delimiters(self.LCS(split1, split2))))
        if not lcs:
            return "<*>"

        # 根据 LCS 替换并合并结果
        return self.getCommonTemplate(lcs, split1)


    def parse(self, logName):
        print("Parsing file: " + os.path.join(self.path, logName))
        start_time = datetime.now()
        self.logName = logName
        rootHamNode = HamNode()
        rootLCSNode = LCSNode()

        #  用于存储LogCluster
        logCluL = []

        self.load_data()

        count = 0
        for idx, line in self.df_log.iterrows():
            logID = line["LineId"]
            # 粗粒度解析 空格解析
            logmessageL = self.preprocess(line["Content"]).strip().split()
            # 先基于Drain固定深度解析树查找模版
            matchCluster = self.treeSearch(rootHamNode, logmessageL)

            # 没有匹配到，则新建一个，更新Drain解析树
            if matchCluster is None:
                # 这里增加对二层的查找 Spell, 如果第二层找不到，则在 第一层fixed deepth tree 和 第二层LCS tree 都增加模版
                # 用途：过滤掉 logmessageL 中所有的 "<*>" 占位符，生成一个不包含占位符的子集列表。
                # 结果：生成的新列表 constLogMessL 只保留实际有意义的内容。
                constLogMessL = [w for w in logmessageL if w != "<*>"]
                # 通过前缀树查询
                matchCluster = self.PrefixTreeMatch(rootLCSNode, constLogMessL, 0)

                # 如果没有找到
                if matchCluster is None:
                    # 遍历LogCluster模版
                    # SimpleLoopMatch 是一个简单的循环匹配函数，用于遍历日志模板列表 logClustL，尝试找到一个与输入序列 seq 匹配的日志模板。
                    # 如果找到相似的模板，返回对应的模板对象；如果未找到，则返回 None。
                    matchCluster = self.SimpleLoopMatch(logCluL, constLogMessL)
                    if matchCluster is None:
                        # 遍历 logCluL
                        # LCSMatch 方法通过计算最长公共子序列（LCS），从日志模板列表 logClustL 中找到一个与输入序列 seq 最相似的模板。
                        # 如果找到满足条件的模板，返回该模板对象；否则返回 None。
                        matchCluster = self.LCSMatch(logCluL, logmessageL)
                        # Match no existing log cluster
                        if matchCluster is None:
                            newCluster = LogCluster(logTemplate=logmessageL, logIDL=[logID])
                            logCluL.append(newCluster)
                            # 第一层，固定深度解析树增加
                            self.addSeqToPrefixHamTree(rootHamNode, newCluster)
                            # 第二层，LCS前缀树增加相应节点
                            self.addSeqToPrefixLCSTree(rootLCSNode, newCluster)
                        else:
                            # newTemplate = self.getTemplateLCS(
                            #     self.LCS(logmessageL, matchCluster.logTemplate),
                            #     matchCluster.logTemplate,
                            # )
                            newTemplate = self.getTemplateLCS(logmessageL, matchCluster.logTemplate)
                            if " ".join(newTemplate) != " ".join(matchCluster.logTemplate):
                                # 删除第二层
                                self.removeSeqFromPrefixLCSTree(rootLCSNode, matchCluster)
                                # 删除第一层
                                self.removeSeqFromPrefixHamTree(rootHamNode, matchCluster)
                                matchCluster.logTemplate = newTemplate
                                # 第一层，固定深度解析树增加
                                self.addSeqToPrefixHamTree(rootHamNode, matchCluster)
                                # 第二层，LCS前缀树增加相应节点
                                self.addSeqToPrefixLCSTree(rootLCSNode, matchCluster)

                if matchCluster:
                    matchCluster.logIDL.append(logID)

            # Add the new log message to the existing cluster
            else:
                # 比较模板，如果已经存在的模版和之前的模版不同，选取最新的模版
                newTemplate = self.getTemplateHam(logmessageL, matchCluster.logTemplate)
                # newTemplate = self.remove_redundant_placeholders(newTemplate)
                matchCluster.logIDL.append(logID)
                if " ".join(newTemplate) != " ".join(matchCluster.logTemplate):
                    # 同时更新第二层的模版
                    self.removeSeqFromPrefixLCSTree(rootLCSNode, matchCluster)
                    matchCluster.logTemplate = newTemplate
                    self.addSeqToPrefixLCSTree(rootLCSNode, matchCluster)

            count += 1
            if count % 1000000 == 0 or count == len(self.df_log):
                print(
                    "Processed {0:.1f}% of log lines.".format(
                        count * 100.0 / len(self.df_log)
                    )
                )

        if not os.path.exists(self.savePath):
            os.makedirs(self.savePath)

        self.outputResult(logCluL)

        print("Parsing done. [Time taken: {!s}]".format(datetime.now() - start_time))
        return format(datetime.now() - start_time)

    '''
        idx是字符串下标
        在前缀树中匹配给定日志序列，寻找是否有相似的模板
        功能：
	        PrefixTreeMatch 通过前缀树递归匹配给定序列，寻找相似的日志模板。
	        判断是否相似的标准是固定内容长度超过阈值 tau * length。
	    优点：
	        使用前缀树高效地组织和匹配日志模板。
	        支持动态和固定内容的混合匹配。
	    不足：
	        需要较高质量的前缀树结构，才能保证匹配效率和准确性。

	    一开始调用传的 idx = 0, 就是从constLogMessL 0开始的
	    matchCluster = self.PrefixTreeMatch(rootNode, constLogMessL, 0)

	    时间复杂度O(N2)
    '''
    def PrefixTreeMatch(self, parentn, seq, idx):
        retLogClust = None
        length = len(seq)
        for i in range(idx, length):
            x = seq[i]
            if seq[i] in parentn.childD:
                childn = parentn.childD[seq[i]]
                if childn.logClust is not None:  # 总感觉这一块有点别扭
                    constLM = [w for w in childn.logClust.logTemplate if "<*>" not in w] # logTemplate 是什么？有待验证
                    if float(len(constLM)) >= self.tau * length:  # 判断相似的标准 给的长度>阈值*length判断是否相似
                        return childn.logClust
                else:
                    return self.PrefixTreeMatch(childn, seq, i + 1)  # 如果当前childn的logClust为None 进入下一层？可能最后一层的 logClust不为空？

        return retLogClust

    '''
        SimpleLoopMatch 是一个简单的循环匹配函数，用于遍历日志模板列表 logClustL，尝试找到一个与输入序列 seq 匹配的日志模板。
        如果找到相似的模板，返回对应的模板对象；如果未找到，则返回 None。
    '''
    def SimpleLoopMatch(self, logClustL, seq):
        for logClust in logClustL:
            if float(len(logClust.logTemplate)) < 0.5 * len(seq):
                continue
            # Check the template is a subsequence of seq (we use set checking as a proxy here for speedup since
            # incorrect-ordering bad cases rarely occur in logs)
            # 将输入序列 seq 转换为集合 token_set，用于加速后续的匹配检查。
            token_set = set(seq)
            # 使用 all() 检查模板 logClust.logTemplate 中的每个 token 是否满足以下任意条件：
            # 	1.	token in token_set：模板中的 token 存在于输入序列中。
            # 	2.	token == "<*>"：模板中的 token 是占位符 <*>。
            # 如果模板中的所有 token 都满足以上条件，认为当前模板与输入序列匹配。
            if all(
                token in token_set or token == "<*>" for token in logClust.logTemplate
            ):
                return logClust
        return None

    '''
        LCSMatch 方法通过计算最长公共子序列（LCS），从日志模板列表 logClustL 中找到一个与输入序列 seq 最相似的模板。
        如果找到满足条件的模板，返回该模板对象；否则返回 None。
        self.LCSMatch(logCluL, logmessageL)
        set_seq & set_template
    	    &：集合的交集运算符，返回两个集合之间的公共元素。
    	    set_seq: 输入日志序列 seq 的集合表示。
    	    set_template: 当前日志模板 logClust.logTemplate 的集合表示。
    	    交集：
    	    用于快速检查 seq 和 logTemplate 之间的共有 token。
    	计算交集的大小，即 seq 和 logTemplate 之间共有 token 的数量
    	定义了一个相似性阈值，表示至少有一半的 token 需要匹配。
    	在执行复杂的 LCS 计算前，先通过集合交集快速判断模板是否有可能匹配。
    	如果交集大小过小，说明两者相似性很低，直接跳过。
    '''
    def LCSMatch(self, logClustL, seq):
        retLogClust = None

        maxLen = -1
        maxlcs = []
        maxClust = None
        set_seq = set(seq)
        size_seq = len(seq)
        for logClust in logClustL:
            set_template = set(logClust.logTemplate)
            if len(set_seq & set_template) < 0.5 * size_seq:
                continue
            lcs = self.LCS(seq, logClust.logTemplate)
            # 选取最符合的最长公共子序列
            if len(lcs) > maxLen or (
                len(lcs) == maxLen
                and len(logClust.logTemplate) < len(maxClust.logTemplate)
            ):
                maxLen = len(lcs)
                maxlcs = lcs
                maxClust = logClust

        # LCS should be large then tau * len(itself)
        # LCS 匹配的相似性应该大于 设置的阈值*长度
        if float(maxLen) >= self.tau * size_seq:
            retLogClust = maxClust

        return retLogClust


    def addSeqToPrefixLCSTree(self, rootn, newCluster):
        parentn = rootn
        seq = newCluster.logTemplate
        seq = [w for w in seq if "<*>" not in w]

        for i in range(len(seq)):
            tokenInSeq = seq[i]
            # Match
            if tokenInSeq in parentn.childD:   # 如果当前token存在，则孩子数加一
                parentn.childD[tokenInSeq].templateNo += 1 # 孩子数+1？
            # Do not Match
            else:   #如果当前token不存在，则把节点新建出来
                parentn.childD[tokenInSeq] = LCSNode(token=tokenInSeq, templateNo=1)
            #无论 token是否存在，都向下传递，即走到最后。中间的 parentn.logClust不存任何东西。
            # 建一个len(seq)长的树
            parentn = parentn.childD[tokenInSeq]

        # 最后的叶子存储模板相关东西
        if parentn.logClust is None:
            parentn.logClust = newCluster

    def removeSeqFromPrefixLCSTree(self, rootn, newCluster):
        parentn = rootn
        seq = newCluster.logTemplate
        seq = [w for w in seq if "<*>" not in w]

        for tokenInSeq in seq:
            if tokenInSeq in parentn.childD:
                matchedNode = parentn.childD[tokenInSeq]
                if matchedNode.templateNo == 1:
                    del parentn.childD[tokenInSeq]
                    break
                else:
                    matchedNode.templateNo -= 1
                    parentn = matchedNode


    def removeSeqFromPrefixHamTree(self, rn, newCluster):
        retLogClust = None
        seq = newCluster.logTemplate
        seqLen = len(seq)
        if seqLen not in rn.childD:
            return

        # 先查找第一层，根据长度查找
        parentn = rn.childD[seqLen]

        currentDepth = 1
        # 对每一个Seq 的 token进行查找，如果第一层找到，就进行第二层查找。
        for token in seq:
            if currentDepth >= self.depth or currentDepth > seqLen:
                break

            if token in parentn.childD:
                parentn = parentn.childD[token]
            elif "<*>" in parentn.childD:
                parentn = parentn.childD["<*>"]
            else:
                return
            currentDepth += 1

        logClustL = parentn.childD

        # 倒表删除
        for i in range(len(logClustL) - 1, -1, -1):
            if logClustL[i].logTemplate == newCluster.logTemplate:
                del logClustL[i]

    def getTemplateLCS(self, seq1, seq2):
        """
        利用 lengths 矩阵做 LCS 动态规划，并结合 self.process_strings 判定是否匹配。
        若 self.process_strings(a, b) != "<*>", 表示 a 和 b 在细粒度上可视为相等，
        并将返回的字符串作为 LCS 中的公共元素。
        """

        # 用于记录 LCS 的长度
        lengths = [[0 for _ in range(len(seq2) + 1)] for _ in range(len(seq1) + 1)]
        # 用于记录匹配后的字符串（如 "<*>.exe" 或实际完全相同的字符串）
        matched_token = [[None for _ in range(len(seq2) + 1)] for _ in range(len(seq1) + 1)]

        # 1) 填充 lengths 表和 matched_token
        for i in range(len(seq1)):
            for j in range(len(seq2)):
                if seq1[i] == "<*>" or seq2[j] == "<*>":
                    lengths[i + 1][j + 1] = lengths[i][j] + 1
                    matched_token[i + 1][j + 1] = "<*>"
                    continue
                # 调用 process_strings 看看是否匹配
                token_result = self.process_strings(seq1[i], seq2[j])
                if token_result != "<*>":
                    # 表示它们在细粒度上"相等"
                    lengths[i + 1][j + 1] = lengths[i][j] + 1
                    matched_token[i + 1][j + 1] = token_result
                else:
                    # 不匹配时，沿用上/左方向中 LCS 长度较大的
                    if lengths[i + 1][j] > lengths[i][j + 1]:
                        lengths[i + 1][j + 1] = lengths[i + 1][j]
                    else:
                        lengths[i + 1][j + 1] = lengths[i][j + 1]

        # 2) 回溯 lengths 矩阵，拼出最终的 LCS 序列
        result = []
        i, j = len(seq1), len(seq2)
        while i > 0 and j > 0:
            # 如果和上方的长度一样，则往上走
            if lengths[i][j] == lengths[i - 1][j]:
                i -= 1
            # 如果和左方的长度一样，则往左走
            elif lengths[i][j] == lengths[i][j - 1]:
                j -= 1
            else:
                # 能走到这里，说明 seq1[i-1] 与 seq2[j-1] 细粒度匹配
                # matched_token[i][j] 就是它们匹配后的结果
                result.insert(0, matched_token[i][j])
                i -= 1
                j -= 1

        return result


    def remove_redundant_placeholders(self, seq):
        """
        如果当前 token 为 "<*>", 且下一个 token 包含 "<*>",
        就删除当前 token。
        """
        new_seq = []
        i = 0
        while i < len(seq):
            current_token = seq[i]

            # 判断是否还有下一个 token，并且当前 token == "<*>"，下一个 token 包含 "<*>"
            if current_token == "<*>" and (i + 1 < len(seq)) and ("<*>" in seq[i+1]):
                # 跳过当前 token，不添加到 new_seq
                i += 1
            else:
                # 否则保留当前 token
                new_seq.append(current_token)
                i += 1

        return new_seq
