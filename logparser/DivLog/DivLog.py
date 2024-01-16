import json
import os
import math
import numpy as np
import pandas as pd
import re
import time
import openai
import tiktoken as tt
from tqdm import tqdm
from random import sample
from sklearn.model_selection import train_test_split
from openai.embeddings_utils import get_embedding, cosine_similarity
from collections import Counter


def dpp(kernel_matrix, max_length, epsilon=1E-10):
    item_size = kernel_matrix.shape[0]
    cis = np.zeros((max_length, item_size))
    di2s = np.copy(np.diag(kernel_matrix))
    selected_items = list()
    selected_item = np.argmax(di2s)
    selected_items.append(selected_item)
    while len(selected_items) < max_length:
        k = len(selected_items) - 1
        ci_optimal = cis[:k, selected_item]
        di_optimal = math.sqrt(di2s[selected_item])
        elements = kernel_matrix[selected_item, :]
        eis = (elements - np.dot(ci_optimal, cis[:k, :])) / di_optimal
        cis[k, :] = eis
        di2s -= np.square(eis)
        selected_item = np.argmax(di2s)
        selected_items.append(selected_item)
    return selected_items

def getDppIndex(log_emb_list, 
                item_size,    # log dataset size
                split_ratio):

    max_length = int(item_size * split_ratio)
    feature_vectors = np.array(log_emb_list) 

    # standarization no need for log embeddings
    feature_vectors /= np.linalg.norm(feature_vectors, axis=1, keepdims=True)

    # calculate similarity matrix of log embeddings
    similarities = np.dot(feature_vectors, feature_vectors.T) 

    t = time.time()
    result = dpp(similarities, max_length)
    result.sort()
    print('DPP algorithm running time: ' + '\t' + "{0:.4e}".format(time.time() - t))
    return result


def DPPsplit(log_list, groundtruth_template, candidate_idx):
    cand_logs = [log_list[idx] for idx in candidate_idx]
    cand_templates = [groundtruth_template[idx] for idx in candidate_idx]
    test_idx = []
    for i in range(len(log_list)):
      if i not in candidate_idx: test_idx.append(i)
    test_idx.sort()
    test_logs = [log_list[idx] for idx in test_idx]
    test_templates = [groundtruth_template[idx] for idx in test_idx]
    return test_logs, cand_logs, test_templates, cand_templates

# calculate parsing accuracy
def evaluatePA(groundtruth, result):
    # len(predicted_list) may smaller than len(groundtruth)
    length = len(result['template'])
    if length == 0: return 0
    correct = 0
    for i in range(length):
        if result['template'][i] == groundtruth.loc[groundtruth['Content'] == result['log'][i]]['EventTemplate'].values[0]:
            correct += 1
    return correct/length

# correctly identified templates over total num of identified template
def evaluatePTA(groundtruth, result):
    # generate a "template: log indexes list" mapping for groundtruth
    oracle_tem_dict = {}
    for idx in range(len(result['template'])):
        if groundtruth['EventTemplate'][idx] not in oracle_tem_dict:
          oracle_tem_dict[groundtruth['EventTemplate'][idx]] = [groundtruth['Content'][idx]]
        else: oracle_tem_dict[groundtruth['EventTemplate'][idx]].append(groundtruth['Content'][idx])

    # generate mapping for identified template
    result_tem_dict = {}
    for idx in range(len(result['template'])):
        if result['template'][idx] not in result_tem_dict:
          result_tem_dict[result['template'][idx]] = [result['log'][idx]]
        else: result_tem_dict[result['template'][idx]].append(result['log'][idx])

    correct_num = 0
    for key in result_tem_dict.keys():
        if key not in oracle_tem_dict: continue
        else:
          if Counter(oracle_tem_dict[key]) == Counter(result_tem_dict[key]): correct_num += 1
    
    return correct_num/len(result_tem_dict)

# correctly identified templates over total num of oracle template
def evaluateRTA(groundtruth, result):
    # generate a "template: log indexes list" mapping for groundtruth
    oracle_tem_dict = {}
    for idx in range(len(result['template'])):
        if groundtruth['EventTemplate'][idx] not in oracle_tem_dict:
          oracle_tem_dict[groundtruth['EventTemplate'][idx]] = [groundtruth['Content'][idx]]
        else: oracle_tem_dict[groundtruth['EventTemplate'][idx]].append(groundtruth['Content'][idx])

    # generate mapping for identified template
    result_tem_dict = {}
    for idx in range(len(result['template'])):
        if result['template'][idx] not in result_tem_dict:
          result_tem_dict[result['template'][idx]] = [result['log'][idx]]
        else: result_tem_dict[result['template'][idx]].append(result['log'][idx])

    correct_num = 0
    for key in oracle_tem_dict.keys():
        if key not in result_tem_dict: continue
        else:
          if Counter(oracle_tem_dict[key]) == Counter(result_tem_dict[key]): correct_num += 1
    
    return correct_num/len(oracle_tem_dict)

# calculate grouping accuracy
def evaluateGA(groundtruth, result):
    # load logs and templates
    compared_list = result['log'].tolist()

    # select groundtruth logs that have been parsed
    parsed_idx = []
    for idx, row in groundtruth.iterrows():
        if row['Content'] in compared_list:
            parsed_idx.append(idx)
            compared_list.remove(row['Content'])

    if not (len(parsed_idx) == 2000):
        print(len(parsed_idx))
        print("Wrong number of groundtruth logs!")
        return 0

    groundtruth = groundtruth.loc[parsed_idx]

    # grouping
    groundtruth_dict = {}
    for idx, row in groundtruth.iterrows():
        if row['EventTemplate'] not in groundtruth_dict:
            # create a new key
            groundtruth_dict[row['EventTemplate']] = [row['Content']]
        else: 
            # add the log in an existing group
            groundtruth_dict[row['EventTemplate']].append(row['Content'])

    result_dict = {}
    for idx, row in result.iterrows():
        if row['template'] not in result_dict:
            # create a new key
            result_dict[row['template']] = [row['log']]
        else: 
            # add the log in an existing group
            result_dict[row['template']].append(row['log'])

    # sorting for comparison
    for key in groundtruth_dict.keys():
        groundtruth_dict[key].sort()

    for key in result_dict.keys():
        result_dict[key].sort()

    # calculate grouping accuracy
    count = 0
    for parsed_group_list in result_dict.values():
        for gt_group_list in groundtruth_dict.values():
            if parsed_group_list == gt_group_list:
                count += len(parsed_group_list)
                break

    return count / 2000


class ModelParser():
  def __init__(self, 
        log_path, 
        result_path, 
        map_path, 
        dataset,
        emb_path,
        cand_ratio,
        split_method, # random or DPP
        order_method, # random or KNN
        permutation,
        warmup, # warmup or not
        subname, # subname of the files
        evaluate, # evaluate or not
    ):

    self.log_path = log_path + "/{}/{}_2k.log_structured.csv".format(dataset,dataset)
    self.result_path = result_path
    self.map_path = map_path + "/{}_{}_lookupmap.json".format(cand_ratio,dataset)
    self.dataset = dataset
    self.emb_path = emb_path + "/{}.json".format(dataset)
    self.cand_ratio = cand_ratio
    self.split_method = split_method
    self.order_method = order_method
    self.permutation = permutation
    self.warmup = warmup
    self.subname = subname
    self.evaluate = evaluate

    # split candidate set
    self.log_test, self.log_cand, self.gt_test, self.gt_cand = self.splitCandidates(self.log_path, self.cand_ratio, self.split_method)

    # build lookup map
    self.lookUpMap = self.buildLookupMap(self.map_path)
  
  # generate lookup map
  def buildLookupMap(self, map_path):
    # build lookup map
    if (os.path.exists(map_path)): 
      print("Loading look up map of {} ...".format(self.dataset))
      with open(map_path, "r") as file:
            return json.load(file)
    else: return self.generateLuMap(map_path)

  # extract groundtruth templates from log_structured.csv file
  def extractCsvContent(self, groundtruth_path):
      dataframe = pd.read_csv(groundtruth_path)
      content_list = dataframe['Content'].values.tolist()
      return content_list

  # extract groundtruth templates from log_structured.csv file
  def extractCsvTemplate(self, groundtruth_path):
      dataframe = pd.read_csv(groundtruth_path)
      template_list = dataframe['EventTemplate'].values.tolist()
      return template_list

  # split the candidate set from raw logs
  def splitCandidates(self, groundtruth_path, cand_ratio, method="random"):
      log_list = self.extractCsvContent(groundtruth_path)
      groundtruth_template = self.extractCsvTemplate(groundtruth_path)
      if method == "random":
          self.map_path += '_random.json'
          # split randomly
          log_test, log_cand, gt_test, gt_cand = train_test_split(log_list, groundtruth_template, test_size=cand_ratio, random_state=42)
      elif method == "DPP":
          # split with diversity
          file = open(self.emb_path, "r")
          emb_map = json.load(file)
          file.close()
          log_embs = []
          for log in log_list:
            log_embs.append(emb_map[log])
          print(f"length of log embs is {len(log_embs)}")
          candidate_idx = getDppIndex(log_embs, 2000, cand_ratio)
          log_test, log_cand, gt_test, gt_cand = DPPsplit(log_list, groundtruth_template, candidate_idx)
          log_test = log_test + log_cand
          gt_test = gt_test + gt_cand
      return log_test, log_cand, gt_test, gt_cand

  def generateEmbeddings(self, str_list):
      # each embedding has length 2048
      # engine: text-search-{ada, babbage, curie, davinci}-{query, doc}-001 
      # | code-search-{ada, babbage}-{code, text}-001
      return [get_embedding(log, engine="text-search-babbage-query-001") for log in str_list]

  # generate a look up map that records the cosine similarity 
  # between two logs with descendant sequence
  def generateLuMap(self, look_up_map_path):
      # get embeddings from embedding json file
      print('Generating lookup map for {} ...'.format(self.dataset))
      with open(self.emb_path, "r") as file:
          emb_map = json.load(file)

      test_embs = [emb_map[log] for log in self.log_test]
      cand_embs = [emb_map[log] for log in self.log_cand]

      lookUpMap = {}
      for test_idx in tqdm(range(len(self.log_test))):
        dis_dict = {}
        for cand_idx in range(len(self.log_cand)):
          dis_dict[cosine_similarity(test_embs[test_idx], cand_embs[cand_idx])] = cand_idx
        # get a list in sorted key (descending order), key = cosine similarity
        sorted_list = []
        for key in sorted(dis_dict, reverse=True): 
          sorted_list.append(dis_dict[key])
        # dict: {log_message : list of similar candidate indexes in order}
        lookUpMap[self.log_test[test_idx]] = sorted_list

      # write the map into a json file
      with open(look_up_map_path, 'w') as file:
        file.write(json.dumps(lookUpMap))
      return lookUpMap
    
  # find the N most similar logs to the input log
  # the index represents the similar ranking
  def getNearest(self, log, N=5):
      cand_list = self.lookUpMap[log]
      if self.order_method == 'random':
        return sample(cand_list, N)
      # return the idexes of most similar N log candidates
      elif self.order_method == 'KNN':
        shift = 0
        result = cand_list[0:N]
        while log in result:
          shift += 1
          result = cand_list[shift:N+shift]
        if self.permutation == 'ascend':
          return result
        elif self.permutation == 'descend':
          result.reverse()
          return result
        elif self.permutation == 'random':
          result = sample(result, N)
          return result

  # generate a prompt in str for a specific log message
  def generatePrompt(self, log, nearest_num=5):
      idxes = self.getNearest(log, nearest_num)
      prompt = ""
      # backward iteration
      for i in range(len(idxes)-1,-1,-1):
        # update: modify the prompt format to <prompt>:xx \n <extraction>:xx \n\n <prompt>: xx ...
        prompt = prompt + "<prompt>:" + self.log_cand[idxes[i]].strip() + \
              '\n<extraction>: <START> ' + self.gt_cand[idxes[i]].strip() + ' <END>\n\n'  
      similarist_gt = self.gt_cand[idxes[0]]
      return prompt, similarist_gt

  def writeResult(self, result, path, limit):
      output = pd.DataFrame(data={"log": self.log_test[:limit], "template": result})
      output.to_csv(path, index=False)

  # extract result from model's response
  def extractResultTemplate(self, text):
      # this pattern is for ChatGPT
      # pattern = re.compile('<START> <Event\d> (.+) <END>')
      pattern = re.compile('<START> (.+) <END>')
      # findall return a list
      result = pattern.findall(text)
      if (len(result)): return result[0]
      else: return ""


  def BatchParse(self, model, model_name, limit, N=5):
      # list to store the model's parsing on each log message
      enc = tt.encoding_for_model(model)
      answer_list = []
      instruction = "For each log after <prompt> tag, extract one log template\
(substitute variable tokens in the log as <*> and remain constant tokens to construct the template)\
and put the template after <extraction> tag and between <START> and <END> tags."

      self.result_path = self.result_path + "/{}_{}_result{}.csv".format(limit,self.dataset,self.subname)
      # if the result file already exists, load it
      if os.path.exists(self.result_path):
        print("Result file already exists, loading ...")
        answer_list = pd.read_csv(self.result_path)['template'].to_list()
      else:
        # if the result file does not exist, use api to generate result
        print("Result file does not exist, generating result ...")
        for line_idx in tqdm(range(len(self.log_test[:limit]))):
          re_id = 0
          temperature = 0
          if line_idx >= limit: break
          line = self.log_test[line_idx]
          token_len = len(enc.encode(line.strip())) + 20
          # get a prompt with five examples for each log message
          prompt, similarist_gt = self.generatePrompt(line, nearest_num=N)
          while True:
            try:
              response = openai.Completion.create(
                                                  model=model, 
                                                  prompt=instruction + "\n\n\n" + prompt + "<prompt>:" + line.strip() + "\n<extraction>: ", 
                                                  temperature=temperature,
                                                  max_tokens=token_len)
            except Exception as e: # if exception occurs
              print(e)
              re_id += 1
              if re_id < 5:
                time.sleep(0.1)
              else:
                result = similarist_gt
                answer_list.append(result)
                print("Too long waiting time, raw log: {}".format(line) + '\n')
                break
            else:
              # if no exception, the model response a dict
              # to avoid empty response
              result = self.extractResultTemplate(response["choices"][0]["text"])
              if result != "":
                answer_list.append(result)
                break
              else:
                if re_id >= 1:
                  result = similarist_gt
                  answer_list.append(result)
                  break
                else:
                  token_len += 10
                  re_id += 1
                  temperature += 0.25

      print("Writing result into {} ...".format(self.result_path))
      if not os.path.exists(self.result_path):
        self.writeResult(answer_list, self.result_path, limit)
      print("Result file generated.")

      if self.evaluate:          
        if not os.path.exists("DivLog_bechmark_result.csv"):
          df = pd.DataFrame(columns=['Dataset', 'Parsing Accuracy', 'Precision Template Accuracy', 'Recall Template Accuracy', 'Grouping Accuracy'])
        else:
          df = pd.read_csv("DivLog_bechmark_result.csv")
        df_groundtruth = pd.read_csv(self.log_path)
        df_parsedlog = pd.read_csv(self.result_path)
        PA = evaluatePA(df_groundtruth, df_parsedlog)
        PTA = evaluatePTA(df_groundtruth, df_parsedlog)
        RTA = evaluateRTA(df_groundtruth, df_parsedlog)
        GA = evaluateGA(df_groundtruth, df_parsedlog)
        print("{}:\t PA:\t{:.6f}\tPTA:\t{:.6f}\tRTA:\t{:.6f}\tGA:\t{:.6f}".format(self.dataset, PA, PTA, RTA, GA))
        if self.dataset not in df['Dataset'].values:
          df.loc[len(df)] = [self.dataset, PA, PTA, RTA, GA]
        else:
          df.loc[df['Dataset'] == self.dataset, 'Parsing Accuracy'] = PA
          df.loc[df['Dataset'] == self.dataset, 'Precision Template Accuracy'] = PTA
          df.loc[df['Dataset'] == self.dataset, 'Recall Template Accuracy'] = RTA
          df.loc[df['Dataset'] == self.dataset, 'Grouping Accuracy'] = GA
        df.to_csv("DivLog_bechmark_result.csv", index=False, float_format="%.6f")
      return 