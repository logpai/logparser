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

import pandas as pd
from scipy.special import comb


def evaluate(groundtruth, parsedresult):
    """Evaluation function to benchmark log parsing accuracy

    Arguments
    ---------
        groundtruth : str
            file path of groundtruth structured csv file
        parsedresult : str
            file path of parsed structured csv file

    Returns
    -------
        f_measure : float
        accuracy : float
    """
    # 真实结果
    df_groundtruth = pd.read_csv(groundtruth)
    # 读取我们解析出的CSV文件
    df_parsedlog = pd.read_csv(parsedresult)
    # Remove invalid groundtruth event Ids
    # 筛选在 ground truth 中 EventId 不为空的行（因为可能有一些无效行）。到它们的索引，存到 non_empty_log_ids。
    non_empty_log_ids = df_groundtruth[~df_groundtruth["EventId"].isnull()].index
    # 用这个索引对 ground truth DataFrame 进行过滤，丢掉无效行。
    df_groundtruth = df_groundtruth.loc[non_empty_log_ids]
    # 同样对解析结果 DataFrame 做相同的过滤，以保证两者的行数和索引位置一致。
    df_parsedlog = df_parsedlog.loc[non_empty_log_ids]
    # 调用 get_accuracy 函数，对 ground truth 和解析结果的 EventId 列进行比较，得到四个指标：precision, recall, f_measure, accuracy。
    (precision, recall, f_measure, accuracy) = get_accuracy(
        df_groundtruth["EventId"], df_parsedlog["EventId"]
    )
    print(
        "Precision: {:.4f}, Recall: {:.4f}, F1_measure: {:.4f}, Parsing_Accuracy: {:.4f}".format(
            precision, recall, f_measure, accuracy
        )
    )
    return f_measure, accuracy, precision, recall

# 这个函数计算了四个指标：precision（精确率）、recall（召回率）、f_measure（F1 分数） 和 accuracy（准确率）。
# 它的核心思想是把日志解析“聚类”问题看作一个聚类对（pairwise）比较问题
def get_accuracy(series_groundtruth, series_parsedlog, debug=False):
    """Compute accuracy metrics between log parsing results and ground truth

    Arguments
    ---------
        series_groundtruth : pandas.Series
            A sequence of groundtruth event Ids
        series_parsedlog : pandas.Series
            A sequence of parsed event Ids
        debug : bool, default False
            print error log messages when set to True

    Returns
    -------
        precision : float
        recall : float
        f_measure : float
        accuracy : float
    """
    # 对 ground truth 的 EventId 做计数，比如 {"E1":10, "E2":5, ...}。
    series_groundtruth_valuecounts = series_groundtruth.value_counts()
    # 实际上的总“成对数（pair）”初始化为 0。
    real_pairs = 0
    for count in series_groundtruth_valuecounts:
        # 遍历每个 EventId 在 ground truth 中的出现次数 count。
        if count > 1:
            # 若某个 EventId 的出现次数大于 1，就说明在 ground truth 中有 count 行都属于这个事件 ID，
            # 那么这 count 行之间存在 comb(count, 2) 个对（组合数：从 count 条日志中选 2 条的组合）
            real_pairs += comb(count, 2)

    series_parsedlog_valuecounts = series_parsedlog.value_counts()
    parsed_pairs = 0
    for count in series_parsedlog_valuecounts:
        if count > 1:
            parsed_pairs += comb(count, 2)

    accurate_pairs = 0
    accurate_events = 0  # determine how many lines are correctly parsed
    for parsed_eventId in series_parsedlog_valuecounts.index:
        logIds = series_parsedlog[series_parsedlog == parsed_eventId].index
        series_groundtruth_logId_valuecounts = series_groundtruth[logIds].value_counts()
        error_eventIds = (
            parsed_eventId,
            series_groundtruth_logId_valuecounts.index.tolist(),
        )
        error = True
        if series_groundtruth_logId_valuecounts.size == 1:
            groundtruth_eventId = series_groundtruth_logId_valuecounts.index[0]
            if (
                logIds.size
                == series_groundtruth[series_groundtruth == groundtruth_eventId].size
            ):
                accurate_events += logIds.size
                error = False
        if error and debug:
            print(
                "(parsed_eventId, groundtruth_eventId) =",
                error_eventIds,
                "failed",
                logIds.size,
                "messages",
            )
        for count in series_groundtruth_logId_valuecounts:
            if count > 1:
                accurate_pairs += comb(count, 2)

    precision = float(accurate_pairs) / parsed_pairs
    recall = float(accurate_pairs) / real_pairs
    f_measure = 2 * precision * recall / (precision + recall)
    accuracy = float(accurate_events) / series_groundtruth.size
    return precision, recall, f_measure, accuracy
