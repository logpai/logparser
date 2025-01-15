import re


def LCS(seq1, seq2):
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
                token_result = process_strings(seq1[i], seq2[j])
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


def getCommonTemplate(lcs, seq):
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
        return "".join(compress_repeated_delimiters(retVal))

def split_string_preserve_delimiters(s):
        # 分割字符串，使用非字母和数字字符进行划分，并保留所有分隔符
        # return re.split(r'([^\w*])', s)
        # return re.split(r'([^a-zA-Z0-9*])', s)  # 使用捕获组保留分隔符
        """
        分割字符串，使用指定的分隔符模式划分，并保留所有分隔符。
        如果字符串中没有分隔符，返回包含原始字符串的列表。
        """
        # 使用捕获组进行分割
        delimiter_pattern=r"\.|/|_"
        if not delimiter_pattern:
            return [s]
        result = re.split(f"({delimiter_pattern})", s)

        # 如果结果为空或仅包含空字符串，返回原字符串作为单元素列表
        return [s] if not result or all(not part for part in result) else result

def compress_repeated_delimiters(lcs):
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

def LCSToken( seq1, seq2):
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

def process_strings(str1, str2):
        """
        主函数，处理两个字符串
        """
        # 切割字符串
        if str1 == str2:
            return str1
        rexStr2 = re.sub(r'<\*>', '', str2)
        split2 = split_string_preserve_delimiters(rexStr2)
        split1 = split_string_preserve_delimiters(str1)
        if len(split2) == 1 or len(split1) == 1:
            return "<*>"

        split1 = list(filter(None, split1))
        split2 = list(filter(None, split2))

        # 找到最长公共子序列
        lcs = list(filter(None, compress_repeated_delimiters(LCSToken(split1, split2))))
        if not lcs:
            return "<*>"

        # 根据 LCS 替换并合并结果
        return getCommonTemplate(lcs, split1)


seq1 = ["Process", "cmd.exe", "exited", "with", "code", "0"]
seq2 = ["Process", "NVIDIA", "abcd", "share.exe", "exited", "with", "code", "0"]
seq4 = ["Process", "<*>.exe", "exited", "with", "code", "<*>"]
lcs = LCS(seq2, seq4)
print(lcs)
