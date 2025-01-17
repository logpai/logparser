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


class LCSObject:
    """Class object to store a log group with the same template"""
    def __init__(self, logTemplate="", logIDL=[]):
        self.logTemplate = logTemplate
        if logIDL is None:
            logIDL = []
        self.logIDL = logIDL


class Node:
    """A node in prefix tree data structure"""
    def __init__(self, token="", templateNo=0):
        self.logClust = None
        self.token = token
        self.templateNo = templateNo
        self.childD = dict()


class Spell_A:
    """LogParser class

    Attributes
    ----------
        path : the path of the input file
        logName : the file name of the input file
        savePath : the path of the output file
        tau : how much percentage of tokens matched to merge a log message
    """

    def __init__(
        self,
        indir="./",
        outdir="./result/",
        log_format=None,
        tau=0.5,
        rex=[],
        delimiter_pattern="",
        keep_para=True,
    ):
        self.path = indir
        self.logName = None
        self.savePath = outdir
        self.tau = tau
        self.logformat = log_format
        self.df_log = None
        self.rex = rex
        self.delimiter_pattern = delimiter_pattern
        self.keep_para = keep_para

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

    def LCSEfficient(self, seq1, seq2):
        # 确保较短的序列用于列滚动，以节省内存
        if len(seq1) < len(seq2):
            seq1, seq2 = seq2, seq1

        # 滚动数组，用于存储当前行和上一行的 LCS 长度
        prev = [0] * (len(seq2) + 1)
        curr = [0] * (len(seq2) + 1)

        # 填充滚动数组
        for i in range(1, len(seq1) + 1):
            for j in range(1, len(seq2) + 1):
                if seq1[i - 1] == seq2[j - 1]:
                    curr[j] = prev[j - 1] + 1
                else:
                    curr[j] = max(curr[j - 1], prev[j])
            prev, curr = curr, prev  # 滚动数组：当前行成为下一行的前一行

        # 逆序回溯得到 LCS
        result = []
        i, j = len(seq1), len(seq2)
        while i > 0 and j > 0:
            if seq1[i - 1] == seq2[j - 1]:
                result.append(seq1[i - 1])
                i -= 1
                j -= 1
            elif prev[j] == prev[j - 1]:
                j -= 1
            else:
                i -= 1

        return result[::-1]  # 返回正序的 LCS

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
            if seq[i] in parentn.childD:
                childn = parentn.childD[seq[i]]
                if childn.logClust is not None: # 总感觉这一块有点别扭
                    constLM = [w for w in childn.logClust.logTemplate if w != "<*>"] # logTemplate 是什么？有待验证
                    if float(len(constLM)) >= self.tau * length: # 判断相似的标准 给的长度>阈值*length判断是否相似
                        return childn.logClust
                else:
                    return self.PrefixTreeMatch(childn, seq, i + 1) # 如果当前childn的logClust为None 进入下一层？可能最后一层的 logClust不为空？

        return retLogClust

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

    def getTemplate(self, lcs, seq):
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
        return retVal

    def addSeqToPrefixTree(self, rootn, newCluster):
        parentn = rootn
        seq = newCluster.logTemplate
        seq = [w for w in seq if w != "<*>"]

        for i in range(len(seq)):
            tokenInSeq = seq[i]
            # Match
            if tokenInSeq in parentn.childD:   # 如果当前token存在，则孩子数加一
                parentn.childD[tokenInSeq].templateNo += 1 # 孩子数+1？
            # Do not Match
            else:   #如果当前token不存在，则把节点新建出来
                parentn.childD[tokenInSeq] = Node(token=tokenInSeq, templateNo=1)
            #无论 token是否存在，都向下传递，即走到最后。中间的 parentn.logClust不存任何东西。
            # 建一个len(seq)长的树
            parentn = parentn.childD[tokenInSeq]

        # 最后的叶子存储模板相关东西
        if parentn.logClust is None:
            parentn.logClust = newCluster

    def removeSeqFromPrefixTree(self, rootn, newCluster):
        parentn = rootn
        seq = newCluster.logTemplate
        seq = [w for w in seq if w != "<*>"]

        for tokenInSeq in seq:
            if tokenInSeq in parentn.childD:
                matchedNode = parentn.childD[tokenInSeq]
                if matchedNode.templateNo == 1:
                    del parentn.childD[tokenInSeq]
                    break
                else:
                    matchedNode.templateNo -= 1
                    parentn = matchedNode

    def outputResult(self, logClustL):
        templates = [0] * self.df_log.shape[0]
        ids = [0] * self.df_log.shape[0]
        df_event = []

        for logclust in logClustL:
            template_str = " ".join(logclust.logTemplate)
            eid = hashlib.md5(template_str.encode("utf-8")).hexdigest()[0:8]
            for logid in logclust.logIDL:
                templates[logid - 1] = template_str
                ids[logid - 1] = eid
            df_event.append([eid, template_str, len(logclust.logIDL)])

        df_event = pd.DataFrame(
            df_event, columns=["EventId", "EventTemplate", "Occurrences"]
        )

        self.df_log["EventId"] = ids
        self.df_log["EventTemplate"] = templates
        if self.keep_para:
            self.df_log["ParameterList"] = self.df_log.apply(
                self.get_parameter_list, axis=1
            )
        self.df_log.to_csv(
            os.path.join(self.savePath, self.logname +"_Spell_A" + "_structured.csv"), index=False
        )
        df_event.to_csv(
            os.path.join(self.savePath, self.logname +"_Spell_A" + "_templates.csv"), index=False
        )

    def printTree(self, node, dep):
        pStr = ""
        for i in xrange(dep):
            pStr += "\t"

        if node.token == "":
            pStr += "Root"
        else:
            pStr += node.token
            if node.logClust is not None:
                pStr += "-->" + " ".join(node.logClust.logTemplate)
        print(pStr + " (" + str(node.templateNo) + ")")

        for child in node.childD:
            self.printTree(node.childD[child], dep + 1)

    def parse(self, logname):
        starttime = datetime.now()
        print("Parsing file: " + os.path.join(self.path, logname))
        self.logname = logname
        self.load_data()
        rootNode = Node()
        logCluL = []

        count = 0
        for idx, line in self.df_log.iterrows():
            logID = line["LineId"]
            '''
                使用正则表达式对字符串进行分割，re.split 返回一个列表。
                正则表达式 r"[\s=:,]" 的含义：
                [\s=:,] 是一个字符集合，表示匹配以下任意一个字符：
                    \s：匹配任何空白字符（如空格、制表符、换行符等）。
                    =：匹配等号。
                    :：匹配冒号。
                    ,：匹配逗号。
                分割的逻辑是：以这些字符为分隔符，将字符串拆分成多个部分。
                
                filter 函数用于过滤掉列表中的空字符串。
	            lambda x: x != "" 是一个匿名函数，表示只保留非空字符串。
	            line = {"Content": "timestamp=2023-12-25, level=INFO, message=Log message here"}
	            假设 self.preprocess 方法没有改变内容。 
	            输出结果：
	            ['timestamp', '2023-12-25', 'level', 'INFO', 'message', 'Log', 'message', 'here']
            '''
            logmessageL = list(
                filter(
                    lambda x: x != "",
                    re.split(r"[\s=:,]", self.preprocess(line["Content"])),
                )
            )

            # 用途：过滤掉 logmessageL 中所有的 "<*>" 占位符，生成一个不包含占位符的子集列表。
	        # 结果：生成的新列表 constLogMessL 只保留实际有意义的内容。
            constLogMessL = [w for w in logmessageL if w != "<*>"]

            # Find an existing matched log cluster
            matchCluster = self.PrefixTreeMatch(rootNode, constLogMessL, 0)

            # 如果没有找到
            if matchCluster is None:
                # 奇怪，为什么不先遍历这个？疑问
                matchCluster = self.SimpleLoopMatch(logCluL, constLogMessL)

                if matchCluster is None:
                    # 遍历 logCluL
                    matchCluster = self.LCSMatch(logCluL, logmessageL)

                    # Match no existing log cluster
                    if matchCluster is None:
                        newCluster = LCSObject(logTemplate=logmessageL, logIDL=[logID])
                        logCluL.append(newCluster)
                        self.addSeqToPrefixTree(rootNode, newCluster)
                    # Add the new log message to the existing cluster
                    else:
                        newTemplate = self.getTemplateLCS(
                            logmessageL,
                            matchCluster.logTemplate,
                        )
                        if " ".join(newTemplate) != " ".join(matchCluster.logTemplate):
                            self.removeSeqFromPrefixTree(rootNode, matchCluster)
                            matchCluster.logTemplate = newTemplate
                            self.addSeqToPrefixTree(rootNode, matchCluster)

            if matchCluster:
                matchCluster.logIDL.append(logID)
            count += 1
            if count % 100000 == 0 or count == len(self.df_log):
                print(
                    "Processed {0:.1f}% of log lines.".format(
                        count * 100.0 / len(self.df_log)
                    )
                )

        if not os.path.exists(self.savePath):
            os.makedirs(self.savePath)

        self.outputResult(logCluL)
        print("Parsing done. [Time taken: {!s}]".format(datetime.now() - starttime))
        return format(datetime.now() - starttime)

    def load_data(self):
        headers, regex = self.generate_logformat_regex(self.logformat)
        self.df_log = self.log_to_dataframe(
            os.path.join(self.path, self.logname), regex, headers, self.logformat
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
                    print("Skip line: " + line)
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

