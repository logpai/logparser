import re
from difflib import SequenceMatcher

def split_string_preserve_delimiters(s):
    """
    分割字符串，使用非字母和数字字符进行划分，并保留所有分隔符
    """
    # return re.split(r'([^\w*])', s)
    return re.split(r'([^a-zA-Z0-9*])', s)  # 使用捕获组保留分隔符

def LCS( seq1, seq2):
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

def getTemplate(lcs, seq):
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

def process_strings(str1, str2):
    """
    主函数，处理两个字符串
    """
    # 切割字符串
    str2 = re.sub(r'<\*>', '', str2)
    split1 = split_string_preserve_delimiters(str1)
    split2 = split_string_preserve_delimiters(str2)
    split1 = list(filter(None, split1))
    split2 = list(filter(None, split2))

    # 找到最长公共子序列
    lcs = LCS(split1, split2)
    print(lcs)
    lcs = compress_repeated_delimiters(lcs)
    lcs = list(filter(None, lcs))
    print(lcs)

    # 根据 LCS 替换并合并结果
    return getTemplate(lcs, split1)

# 示例字符串
str1 = "/user/root/rand4/_temporary/abc/_task_200811101024_0009_m_000115_0/part-00115."
str2 = "/user/root/sortrand/_temporaryc/def/_task_200811092030_0002_r_000230_0/part-00230."
str3 = "/opsadmin/root/sortrand/_temporaryc/def/_task_200811092030_0002_r_000230_0/part-00230."
str4 = "/opsadmin/home/sortrand/_temporaryc/def/_task_200811092030_0002_r_000230_0/part-00230."


str9 = "/user/root/<*>part-<*>."
str10 = "/<*>root/<*>part-<*>."


str5 = "python.exe"
str6 = "c++.exe"
str7 = "<*>.exe"
str21 = "blk_4029139044660806713"
str22 = "blk_-5471189807977280544"
result = process_strings(str1, str2)
print(result)
result = compress_repeated_delimiters(result)
print("".join(result))