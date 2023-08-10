"""
Description : This file implements the function to evaluation accuracy of log parsing.
              Modified by zzkluck for stand-alone usage, involve only built-in python modules.
Author      : LogPAI team
Modifier    : zzkluck
License     : MIT
"""

import csv
from typing import Tuple, List
from collections import defaultdict, Counter
from math import comb

# when use python version < 3.8, use following comb_2(n) instead of math.comb(n, 2)
# def comb_2(n: int): return n * (n - 1) // 2


def evaluate(groundtruth: str, parsedresult: str) -> Tuple[float, float]:
    """ Evaluation function to benchmark log parsing accuracy

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
    invalid_line_id = set()
    ground_truth_event_id = []
    parsed_result_event_id = []

    with open(groundtruth, 'r') as gt_file:
        reader = csv.DictReader(gt_file)
        for i, line in enumerate(reader):
            if line['EventId'] == "":
                invalid_line_id.add(i)
            else:
                ground_truth_event_id.append(line['EventId'])

    with open(parsedresult, 'r') as pr_file:
        reader = csv.DictReader(pr_file)
        for i, line in enumerate(reader):
            if i not in invalid_line_id:
                parsed_result_event_id.append(line['EventId'])

    (precision, recall, f_measure, accuracy) = get_accuracy(ground_truth_event_id, parsed_result_event_id)
    print(f'Precision: {precision:.4f}, Recall: {recall:.4f}, '
          f'F1_measure: {f_measure:.4f}, Parsing_Accuracy: {accuracy:.4f}')
    return f_measure, accuracy


def get_accuracy(ground_truth: List[str], parsed_result: List[str], debug=None) -> Tuple[float, float, float, float]:
    """ Compute accuracy metrics between log parsing results and ground truth
    
    Arguments
    ---------
        ground_truth : List[str]
            A sequence of groundtruth event Ids
        parsed_result : List[str]
            A sequence of parsed event Ids
        debug : None
            Deprecated in this version

    Returns
    -------
        precision : float
        recall : float
        f_measure : float
        accuracy : float
    """
    gt_counter = defaultdict(list)
    for i, eventId in enumerate(ground_truth):
        gt_counter[eventId].append(i)
    real_pairs = sum(comb(len(ids), 2) for ids in gt_counter.values())

    pr_counter = defaultdict(list)
    for i, eventId in enumerate(parsed_result):
        pr_counter[eventId].append(i)
    parsed_pairs = sum(comb(len(ids), 2) for ids in pr_counter.values())
    accurate_pairs = 0
    accurate_events = 0  # determine how many lines are correctly parsed
    for parsed_eventId in pr_counter.keys():
        error_counter = Counter(ground_truth[i] for i in pr_counter[parsed_eventId])
        if len(error_counter) == 1:
            ground_truth_eventId = next(iter(error_counter.keys()))
            if len(gt_counter[ground_truth_eventId]) == len(pr_counter[parsed_eventId]):
                accurate_events += len(pr_counter[parsed_eventId])
        for count in error_counter.values():
            if count > 1:
                accurate_pairs += comb(count, 2)

    precision = float(accurate_pairs) / parsed_pairs
    recall = float(accurate_pairs) / real_pairs
    f_measure = 2 * precision * recall / (precision + recall)
    accuracy = float(accurate_events) / len(ground_truth)
    return precision, recall, f_measure, accuracy
