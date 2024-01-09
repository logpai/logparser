import os
import openai
import argparse
from DivLog import ModelParser

def main(args):
    # get a tester object with data
    openai.api_key = args.key
    print("Parsing " + args.dataset + " ...")

    if not os.path.exists(args.result_path):
        os.mkdir(args.result_path)

    if not os.path.exists(args.map_path):
        os.mkdir(args.map_path)

    if not os.path.exists(args.log_path):
        print("Log path does not exist. Please check the path.")
        exit()

    if not os.path.exists(args.emb_path):
        print("Embedding path does not exist. Please check the path.")
        exit()

    parser = ModelParser(
                log_path = args.log_path,        # .log_structured_csv
                result_path=args.result_path,    # .result_csv
                map_path=args.map_path,          # .map_json
                dataset = args.dataset,             # 16 datasets
                emb_path = args.emb_path,           # embedding
                cand_ratio = args.cand_ratio,       # ratio of candidate set
                split_method = args.split_method,   # random or DPP
                order_method = args.order_method,   # random or KNN
                permutation = args.permutation,     # permutation
                warmup = args.warmup,               # warmup or not
                subname = args.subname,             # subname of the files
                evaluate = args.evaluate,           # evaluate or not
                )

    parser.BatchParse(model = args.model, 
                        model_name = args.model_name, 
                        limit = args.limit,         # number of logs for testing
                        N = args.N,                  # number of examples in the prompt
                        )

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-key', type=str, default="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", help='openai key')
    parser.add_argument('--log_path', type=str, default='../../data/loghub_2k', help='log path')
    parser.add_argument('--result_path', type=str, default='results', help='result path')
    parser.add_argument('--map_path', type=str, default='maps', help='map path')
    parser.add_argument('--dataset', type=str, default='HDFS', help='dataset name')
    parser.add_argument('--emb_path', type=str, default='embeddings', help='embedding path')
    parser.add_argument('--cand_ratio', type=float, default=0.1, help='ratio of candidate set')
    parser.add_argument('--split_method', type=str, default='DPP', help='random or DPP')
    parser.add_argument('--order_method', type=str, default='KNN', help='random or KNN')
    parser.add_argument('--permutation', type=str, default='ascend', help='ascend, descend, or random')
    parser.add_argument('--warmup', type=bool, default=False, help='warmup or not')
    parser.add_argument('--model', type=str, default='curie', help='model name')
    parser.add_argument('--model_name', type=str, default='gptC', help='model name')
    parser.add_argument('--limit', type=int, default=2000, help='number of logs for testing')
    parser.add_argument('--N', type=int, default=5, help='number of examples in the prompt')
    parser.add_argument('--subname', type=str, default='', help='subname of the files')
    parser.add_argument('--evaluate', type=bool, default=False, help='evaluate or not')
    args = parser.parse_args()
    main(args)