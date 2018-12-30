import csv
import os
import argparse
import pickle

from main.org.core.validation.oracle import OracleTemplates
from main.org.core.validation.validate_chromosomes import validate_chromosome

"""
    this script is a wrapper for the validation process of MoLFI and can be used from the command line as following
    python3.6 path/to/validation.py --chrom [serialized_templates] --time [exec_time_MoLFI] --oracle [oracle_file] 
                                    --csv [file to save validation metrics] --templ [file with validation results] --run [run_number_of_MoLFI]

"""

cmdline = argparse.ArgumentParser(
    usage="\
    \t validation.py --chrom generated_tmp --time time --oracle oracle.txt --csv file.csv --templ tmp.txt\n \
    \t--chrom: \t\t\t the generated chromosome with templates, the serialized file\n \
    \t--time: \t\t the execution time of MoLFI\n\
    \t--oracle: \t\t the oracle file with correct templates\n\
    \t--csv: \t\t the csv file where to save the metrics values after validation\n \
    \t--templ: \t\t the output file where to save the generated templates",
    description='validation: compare the generated templates by MoLFI against the oracle file '
                'and returns a csv file with the comparison results.')
cmdline.add_argument('--chrom',
                     '-c',
                     action='store',
                     help=r'the chromosomes file',
                     dest='achrom',
                     required=True
                     )
cmdline.add_argument('--time',
                     '-t',
                     action='store',
                     help=r"the execution time",
                     dest='atime',
                     required=True
                     )
cmdline.add_argument('--oracle',
                     '-o',
                     action='store',
                     help=r"oracle file",
                     dest='aoracle',
                     required=True
                     )
cmdline.add_argument('--csv',
                     '-s',
                     action='store',
                     help=r"the output csv file",
                     dest='acsv',
                     required=True
                     )
cmdline.add_argument('--templ',
                     '-to',
                     action='store',
                     help=r'the output file with templates',
                     dest='atempl',
                     required=True
                     )
cmdline.add_argument('--run',
                     '-r',
                     action='store',
                     help=r'number of run',
                     dest='arun',
                     required=True
                     )


args = cmdline.parse_args()

# if all the requirement arguments are provided, start the process

# get the log file folder
pareto_chromosomes = args.achrom
exec_time = args.atime
oracle_file = args.aoracle
csv_file = args.acsv
tmp_file = args.atempl
run = args.arun

with open(args.achrom, "rb" ) as pk:
    solutions = pickle.load(pk)

csvfile = open(csv_file, 'a')
writer = csv.writer(csvfile, quoting=csv.QUOTE_NONNUMERIC)
if os.stat(csv_file).st_size == 0:
    writer.writerow(('Run', 'Execution Time(s)', 'Point',
                 'Correct Templates', 'Incorrect Templates',
                 'Precision', 'Recall', 'Accuracy', 'F-Measure'))

oracle = OracleTemplates(oracle_file)
validate_file=open(tmp_file, 'w')
# validate the generated templates against the oracle
print("Validating chromosomes\n")
# validate the three best chromosomes: output of the NSGA_II script
# and return a list with the metrics
# pareto = [knee_solution, knee_solution1, mid_solution]
for key in solutions.keys():
    validate_file.write("Chromosome:")
    validate_file.write("\t\t\t Templates: %d:\n\n" % solutions[key].all_templates())
    metrics = validate_chromosome(oracle.messages, solutions[key], validate_file)

    writer.writerow((str(run), exec_time, key,
                     str(metrics[0]), str(metrics[1]),
                     str(metrics[2]), str(metrics[3]), str(metrics[4]), str(metrics[5])))
#

print('Finishing Template Extraction for Run ', str(run))
print('************************************************************************************************************')
validate_file.close()
csvfile.close()
