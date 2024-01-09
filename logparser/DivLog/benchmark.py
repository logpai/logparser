import os
import pandas as pd
import argparse

parser = argparse.ArgumentParser(description="Runs batchtest.py with a provided OpenAI key.")
parser.add_argument('-key', type=str, default="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", help='openai key')
args = parser.parse_args()

datasets = ["HDFS", "Spark", "BGL", "Windows", "Linux", "Android", "Mac", "Hadoop", "HealthApp", "OpenSSH", "Thunderbird", "Proxifier", "Apache", "HPC", "Zookeeper", "OpenStack"]
    
for dataset in datasets:
    os.system(f"python demo.py -key {args.key} --dataset {dataset} --evaluate True")
df_results = pd.read_csv("DivLog_bechmark_result.csv")
print(df_results)