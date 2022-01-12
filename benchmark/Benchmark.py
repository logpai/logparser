#!/usr/bin/env python

import sys
sys.path.append('../')
from logparser import evaluator, AEL, Drain, IPLoM, LenMa, LFA, LKE, LogCluster, LogMine, LogSig,  SHISO, SLCT, Spell
from LogSettings import benchmark_settings, input_dir
import pandas as pd
import os


# How to construct a parser for specific parameters
parsers = {
    "AEL": lambda setting: AEL.LogParser(log_format=setting['log_format'], indir=indir, outdir=output_dir,
                                         minEventCount=setting['minEventCount'], merge_percent=setting['merge_percent'], rex=setting['regex']),
    "Drain": lambda setting: Drain.LogParser(log_format=setting['log_format'], indir=indir, outdir=output_dir, rex=setting['regex'], depth=setting['depth'], st=setting['st']),
    "IPLoM": lambda setting: IPLoM.LogParser(log_format=setting['log_format'], indir=indir, outdir=output_dir,
                                             CT=setting['CT'], lowerBound=setting['lowerBound'], rex=setting['regex']),
    "Lenma": lambda setting: LenMa.LogParser(log_format=setting['log_format'], indir=indir, outdir=output_dir, rex=setting['regex'], threshold=setting['threshold']),
    "LFA": lambda setting: LFA.LogParser(log_format=setting['log_format'], indir=indir, outdir=output_dir, rex=setting['regex']),
    "LKE": lambda setting: LKE.LogParser(log_format=setting['log_format'], indir=indir, outdir=output_dir, rex=setting['regex'],
                                         split_threshold=setting['split_threshold']),
    "LogCluster": lambda setting: LogCluster.LogParser(indir, setting['log_format'], output_dir, rex=setting['regex'], rsupport=setting['rsupport']),
    "LogMine": lambda setting: LogMine.LogParser(log_format=setting['log_format'], indir=indir, outdir=output_dir,
                                                 rex=setting['regex'], max_dist=setting['max_dist'], k=setting['k'],
                                                 levels=setting['levels']),
    "LogSig": lambda setting: LogSig.LogParser(log_format=setting['log_format'], indir=indir, outdir=output_dir, rex=setting['regex'], groupNum=setting['groupNum']),
    #"MoLFI": lambda setting: MoLFI.LogParser(log_format=setting['log_format'], indir=indir, outdir=output_dir, rex=setting['regex']),
    "SHISO": lambda setting: SHISO.LogParser(log_format=setting['log_format'], indir=indir, outdir=output_dir, rex=setting['regex'],
                                             maxChildNum=setting['maxChildNum'], mergeThreshold=setting['mergeThreshold'],
                                             formatLookupThreshold=setting['formatLookupThreshold'], superFormatThreshold=setting['superFormatThreshold']),
    "SLCT": lambda setting: SLCT.LogParser(log_format=setting['log_format'], indir=indir, outdir=output_dir,
                                           rex=setting['regex'], support=setting['support']),
    "Spell": lambda setting:  Spell.LogParser(log_format=setting['log_format'], indir=indir,
                                              outdir=output_dir, rex=setting['regex'], tau=setting['tau'])
}

bm_parsers = []
for arg in sys.argv:
  if arg in parsers:
    bm_parsers.append(arg)
if bm_parsers == []:
  bm_parsers = parsers.keys()

bm_datasets = []
for arg in sys.argv:
  if arg in benchmark_settings.keys():
    bm_datasets.append(arg)
if bm_datasets == []:
  bm_datasets = benchmark_settings.keys()

print("\n== Benchmarking " + ', '.join(bm_parsers) + " on " + ', '.join(bm_datasets) + " ==\n")

for bm_parser_name in bm_parsers:
    bm_parser = parsers[bm_parser_name]
    # The output directory of parsing results
    output_dir = bm_parser_name + '_result/'
    benchmark_result = []
    for dataset, setting in benchmark_settings.iteritems():
        if not (dataset in bm_datasets):
          continue
        print('\n=== Evaluation of %s on %s ===' % (bm_parser_name, dataset))
        indir = os.path.join(input_dir, os.path.dirname(setting['log_file']))
        log_file = os.path.basename(setting['log_file'])
        bm_parser(setting).parse(log_file)

        F1_measure, accuracy = evaluator.evaluate(
            groundtruth=os.path.join(indir, log_file + '_structured.csv'),
            parsedresult=os.path.join(output_dir, log_file + '_structured.csv')
        )
        benchmark_result.append([dataset, F1_measure, accuracy])

    print('\n=== Overall evaluation results ===')
    df_result = pd.DataFrame(benchmark_result, columns=[
                             'Dataset', 'F1_measure', 'Accuracy'])
    df_result.set_index('Dataset', inplace=True)
    print(df_result)
    df_result.T.to_csv(bm_parser_name + '_benchmark_result.csv')
