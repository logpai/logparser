#!/usr/bin/env python

import sys
sys.path.append('../')
from logparser import LogSig, evaluator
import os
import pandas as pd
from LogSettings import benchmark_settings, input_dir

output_dir = 'LogSig_result/' # The output directory of parsing results

from LogSettings import benchmark_settings, input_dir

bechmark_result = []
for dataset, setting in benchmark_settings.iteritems():
    print('\n=== Evaluation on %s ==='%dataset)
    indir = os.path.join(input_dir, os.path.dirname(setting['log_file']))
    log_file = os.path.basename(setting['log_file'])

    parser = LogSig.LogParser(log_format=setting['log_format'], indir=indir, outdir=output_dir, rex=setting['regex'], groupNum=setting['groupNum'])
    parser.parse(log_file)
    
    F1_measure, accuracy = evaluator.evaluate(
                           groundtruth=os.path.join(indir, log_file + '_structured.csv'),
                           parsedresult=os.path.join(output_dir, log_file + '_structured.csv')
                           )
    bechmark_result.append([dataset, F1_measure, accuracy])

print('\n=== Overall evaluation results ===')
df_result = pd.DataFrame(bechmark_result, columns=['Dataset', 'F1_measure', 'Accuracy'])
df_result.set_index('Dataset', inplace=True)
print(df_result)
df_result.T.to_csv('LogSig_bechmark_result.csv')
