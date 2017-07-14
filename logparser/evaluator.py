'''
    Description: This file implements the function to evaluation accuracy of log parsing
    Author: LogPAI team
    License: MIT
'''

import sys
import pandas as pd
from collections import defaultdict
import scipy.misc


def evaluate(groundtruth_file, parsed_logfile):
	df_groundtruth = pd.read_csv(groundtruth_file)
	df_parsedlog = pd.read_csv(parsed_logfile)
	(precision, recall, f_measure, accuracy) = get_accuracy(df_groundtruth['EventId'], df_parsedlog['EventId'])
	print 'precision:%f, recall:%f, f_measure:%f, accuracy:%f'%(precision, recall, f_measure, accuracy)


def get_accuracy(series_groundtruth, series_parsedlog):
	series_groundtruth_valuecounts = series_groundtruth.value_counts()
	real_pairs = 0
	for count in series_groundtruth_valuecounts:
		if count > 1:
			real_pairs += scipy.misc.comb(count, 2)

	series_parsedlog_valuecounts = series_parsedlog.value_counts()
	parsed_pairs = 0
	for count in series_parsedlog_valuecounts:
		if count > 1:
			parsed_pairs += scipy.misc.comb(count, 2)

	accurate_pairs = 0
	accurate_events = 0 # determine how many lines are correctly parsed
	for parsed_eventId in series_parsedlog_valuecounts.index:
		logIds = series_parsedlog[series_parsedlog == parsed_eventId].index
		series_groundtruth_logId_valuecounts = series_groundtruth[logIds].value_counts()
		if series_groundtruth_logId_valuecounts.size == 1:
			groundtruth_eventId = series_groundtruth_logId_valuecounts.index[0]
			if logIds.size == series_groundtruth[series_groundtruth == groundtruth_eventId].size:
				accurate_events += logIds.size
		for count in series_groundtruth_logId_valuecounts:
			if count > 1:
				accurate_pairs += scipy.misc.comb(count, 2)

	precision = float(accurate_pairs) / parsed_pairs
	recall = float(accurate_pairs) / real_pairs
	f_measure = 2 * precision * recall / (precision + recall)
	accuracy = float(accurate_events) / series_groundtruth.size
	return precision, recall, f_measure, accuracy







