'''
    Description: Logparser is an automated log parsing tool to extract event templates from 
        unstructured logs.
    Author: LogPAI team
    License: MIT
'''

import re
import sys
import os
import pandas as pd
import csv
import mlcs
from collections import defaultdict, deque, Counter


class Parser(object):
    def __init__(self, logformat=None, indir='./', outdir='result/', min_para_size=5):
        self.logformat = logformat
        self.outdir = outdir
        self.indir = indir
        if logformat is None:
            sys.exit('Please provide log message format!')
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        self.min_para_size = min_para_size
        self.df_log = None
        self.para_token_set = set(['NUM', '[+]', '[?]', '[IP]', '[STATE]'])
        # out_link_freq_dict = {((position, token1): {(splitter, token2): occurences}}
        self.out_link_freq_dict = defaultdict(lambda: Counter())
        # log_lines_over_link_dict = {(position, token1): {(splitter, token2): set(logIds)}}
        self.log_lines_over_link_dict = defaultdict(lambda: defaultdict(set))
        # in_link_dict = {(position, token2): set((token1, splitter))}
        self.in_link_dict = defaultdict(set)
        # token_freq_dict = {(position, token): freq}
        self.token_freq_dict = Counter()

    
    def parse(self, log_file, event_template=None):
        (headers, regex) = self.generate_logformat_regex(self.logformat)
        self.log2dataframe(os.path.join(self.indir, log_file), regex, headers)
        if event_template:
            template_counter = self.template_match(event_template, headers)
            self.dump_parsing_result(log_file, template_counter)
        else:
            self.generate_token_link(headers)
            print 'Generating template graph...'
            self.generate_template_graph()
            print 'Get path...'
            (all_paths, log_lines_with_path) = self.get_all_paths()
            (templates, log_id_with_template) = self.post_processing(all_paths, log_lines_with_path)
            self.dump_parsing_result(log_file, templates, log_id_with_template)
        print 'Parsing %d lines done!'%self.df_log.shape[0]



    def dump_parsing_result(self, log_file, templates=None, log_id_with_template=None):
        with open(self.outdir + log_file + '_templates.csv', 'wb') as four:
            writer = csv.writer(four, delimiter=',')
            writer.writerow(['EventId', 'EventTemplate', 'Occurences'])
            if log_id_with_template:
                i = 1
                for template in templates:
                    writer.writerow(['E' + str(i), template, len(log_id_with_template[template])])
                    i += 1
            else:
                template_list = []
                matched_count = 0
                for (evtId, template), cnt in templates.iteritems():
                    eventId = int(evtId.split('E')[-1])
                    template_list.append([eventId, template, cnt])
                    matched_count += cnt
                template_list.sort(key=lambda li: li[0]) # sort in place
                for template in template_list:
                    writer.writerow(['E' + str(template[0]), template[1], template[2]])
                no_match = self.df_log.shape[0] - matched_count
                if no_match > 0:
                    writer.writerow(['NO_MATCH', 'NA', no_match])

        if log_id_with_template:
            self.df_log['EventId'] = None
            self.df_log['EventTemplate'] = None
            i = 1
            for template in templates:
                logIds = log_id_with_template[template]
                for logId in logIds:
                    self.df_log.set_value(logId, 'EventId', 'E' + str(i))
                    self.df_log.set_value(logId, 'EventTemplate', template)
                i += 1
        self.df_log.to_csv(self.outdir + log_file + '_structured.csv', index=False)


    def generate_template_graph(self):
        queue = deque()
        queue_visited = set()
        queue.append((0, '$START$'))
        while queue:
            (pos, token1) = queue.popleft()
            if (pos, token1) in queue_visited:
                continue
            queue_visited.add((pos, token1))            
            print '%d\t%s'%(pos, token1)
            # Iterate over all out links of each token
            tokens_group = defaultdict(set) 
            token1_out_links = self.out_link_freq_dict[(pos, token1)].keys()
            token1_out_links = filter(lambda tk: tk[-1] != '$END$', token1_out_links)
            if not token1_out_links:
                continue
            if len(token1_out_links) == 1:
                (in_splitter, token2) = token1_out_links[0]
                self.update_token(pos, token1, in_splitter, token2, queue)
            else:
                # Group tokens of token1_out_links
                if all(map(self.is_number, map(lambda tk: tk[-1][-1], token1_out_links))):
                    tokens_group[token1] = set(token1_out_links)
                else:
                    for (in_splitter, token2) in token1_out_links:
                        token2_out_links = self.out_link_freq_dict[(pos + 2, token2)].keys()
                        tokens_group[frozenset(token2_out_links)].add((in_splitter, token2))
                # Further split token group linked to '$END$'               
                if frozenset([('', '$END$')]) in tokens_group:
                    token_set = tokens_group.pop(frozenset([('', '$END$')]))                    
                    # Group into numbers/tokens with non-word character/words                   
                    for tk in token_set:
                        if self.is_number(tk[-1][-1]):
                            tokens_group[('Group1', '$END$')].add(tk)
                        elif re.search(r'[^A-Za-z0-9]', tk[-1][-1]):
                            tokens_group[('Group2', '$END$')].add(tk)
                        else:
                            tokens_group[('Group3', '$END$')].add(tk)

                # Process for each group
                size1_group_tokens = []
                for key, token_set in tokens_group.iteritems():
                    if key == ('Group3', '$END$') and token1 == '$START$':
                        self.update_state_token(pos, token1, token_set, queue)
                    elif len(token_set) > self.min_para_size:
                        self.update_para_token(pos, token1, token_set, queue)
                    elif len(token_set) > 1:
                        # token2_links_freq = map(lambda tk: self.out_link_freq_dict[(pos, token1)][tk], token_set)
                        # if max(token2_links_freq) < self.min_para_size\
                        #     and sum(token2_links_freq) < self.min_para_size * len(token1_out_links):
                        #       self.update_para_token(pos, token1, token_set, queue)
                        # else: # State idenfication
                        self.update_state_token(pos, token1, token_set, queue)
                    else:
                        size1_group_tokens.append(token_set.pop())
                if token1 == '$START$' or len(size1_group_tokens) < self.min_para_size:
                    for (in_splitter, token2) in size1_group_tokens:
                        self.update_token(pos, token1, in_splitter, token2, queue)
                elif size1_group_tokens:
                    self.update_para_token(pos, token1, size1_group_tokens, queue)


    def update_token(self, pos, token1, splitter, token2, queue):
        new_token = token2
        token2_link_freq = self.out_link_freq_dict[(pos, token1)][(splitter, token2)]
        if token2_link_freq <= self.min_para_size:
            sub_tokens = re.split(r'([^A-Za-z0-9])', token2[-1])
            if len(sub_tokens) > 1:
                sub_tokens = ['[NUM]' if self.is_number(tk) else tk for tk in sub_tokens]
                sub_tokens = ['[+]' if re.search('\d', tk) else tk for tk in sub_tokens]
                token_str = ''.join(sub_tokens)
                new_token = (token2[0], token_str)
            else:
                if self.is_number(token2[-1]):
                    new_token = (token2[0], '[NUM]')
                elif re.search('\d', token2[-1]):
                    new_token = (token2[0], '[+]')
            if new_token != token2:
                self.update_graph(pos + 2, token2, new_token, token2_link_freq)     
        queue.append((pos + 2, new_token))  

    def update_para_token(self, pos, token1, token_set, queue):
        common_pattern = self.get_common_pattern(map(lambda tk: tk[-1][-1], token_set))
        for tk in token_set:
            new_token = (tk[-1][0], common_pattern)
            tk_link_freq = self.out_link_freq_dict[(pos, token1)][tk]
            self.update_graph(pos + 2, tk[-1], new_token, tk_link_freq)
        queue.append((pos + 2, new_token))


    def update_state_token(self, pos, token1, token_set, queue):
        token_list = [tk[-1][-1] for tk in token_set]
        if all(map(self.is_number, token_list)):
            # new_token = (token2[0], '[STATE:{%s}]'%(','.join(token_list)))
            for tk in token_set:
                new_token = (tk[-1][0], '[STATE]')
                tk_link_freq = self.out_link_freq_dict[(pos, token1)][tk]
                self.update_graph(pos + 2, tk[-1], new_token, tk_link_freq)
            queue.append((pos + 2, new_token))
        else:
            if self.get_common_pattern(token_list) != '[+]':
                self.update_para_token(pos, token1, token_set, queue)
            else:
                for tk in token_set:
                    queue.append((pos + 2, tk[-1]))


    def update_graph(self, pos, token, new_token, token_freq):
        # Update token freq
        self.token_freq_dict[(pos, new_token)] += token_freq
        self.token_freq_dict[(pos, token)] -= token_freq
        if self.token_freq_dict[(pos, token)] <= 0:
            self.token_freq_dict.pop((pos, token))
        out_token_links = list(self.out_link_freq_dict[(pos, token)].keys())
        for (out_splitter, out_token) in out_token_links:
            # Update out links of token
            self.out_link_freq_dict[(pos, new_token)][(out_splitter, out_token)] += self.out_link_freq_dict[(pos, token)].pop((out_splitter, out_token))
            # Update in links of out_token
            self.in_link_dict[(pos + 2, out_token)].discard((token, out_splitter))
            self.in_link_dict[(pos + 2, out_token)].add((new_token, out_splitter))
            # Update log_lines_over_link_dict
            self.log_lines_over_link_dict[(pos, new_token)][(out_splitter, out_token)] =\
                self.log_lines_over_link_dict[(pos, new_token)][(out_splitter, out_token)] | self.log_lines_over_link_dict[(pos, token)].pop((out_splitter, out_token))
        self.out_link_freq_dict.pop((pos, token))
        in_token_links = self.in_link_dict[(pos, token)].copy()
        for (in_token, in_splitter) in in_token_links:
            # Update in links of token
            self.in_link_dict[(pos, new_token)].add((in_token, in_splitter))
            self.out_link_freq_dict[(pos - 2, in_token)][(in_splitter, new_token)] += self.out_link_freq_dict[(pos - 2, in_token)].pop((in_splitter, token))
            # Update log_lines_over_link_dict
            self.log_lines_over_link_dict[(pos - 2, in_token)][(in_splitter, new_token)] =\
                self.log_lines_over_link_dict[(pos - 2, in_token)][(in_splitter, new_token)] | self.log_lines_over_link_dict[(pos - 2, in_token)].pop((in_splitter, token))
        self.in_link_dict.pop((pos, token))


    def get_common_pattern(self, tokens):
        # Replace numbers with [NUM]
        tokens = [re.sub(r'(?<=^)(\-)(?=[0-9]+)', '', tk) for tk in tokens]
        tokens = [re.sub(r'(?<=[^A-Za-z0-9])(\-)(?=[0-9]+)', '', tk) for tk in tokens]
        common_pattern = ''
        df_tokens_split = pd.DataFrame()
        token_size_set = set()
        for token in tokens:
            token_split = re.split(r'([^A-Za-z0-9]+)', token)
            token_size_set.add(len(token_split))
            df_tokens_split = pd.concat([df_tokens_split, pd.DataFrame([token_split])], ignore_index=True)
        if len(token_size_set) == 1 and next(iter(token_size_set)) > 1: # tokens are in equal size
            token_size = next(iter(token_size_set))
            for i in xrange(token_size):
                token_set = set(df_tokens_split.iloc[:, i])
                if len(token_set) == 1:
                    token = token_set.pop()
                    if self.is_number(token):
                        token = '[NUM]'
                    common_pattern += token
                else:
                    common_pattern += self.get_para_type(token_set)
        elif len(token_size_set) > 1:
            token_list = []
            for idx, row in df_tokens_split.iterrows():
                li = ['[NUM]' if self.is_number(tk) else tk for tk in row.dropna().tolist()]
                token_list.append(li)
            token_list.sort(key=len)
            common_prefix = os.path.commonprefix(token_list)
            common_suffix = os.path.commonprefix([li[::-1] for li in token_list])[::-1]
            if len(common_prefix) + len(common_suffix) < len(token_list[0]):
                common_pattern = ''.join(common_prefix + ['[+]'] + common_suffix)
            else:
                common_pattern = ''.join(common_prefix + ['[?]'] + common_suffix)
        else:
            if all(map(self.is_number, tokens)):
                common_pattern = '[NUM]'
            else:
                # Get common prefix or suffix
                new_token_set = set()
                for token in tokens:
                    sub_tokens = re.split(r'(\d+)', token)
                    if len(sub_tokens) == 3:
                        sub_tokens = ['[NUM]' if self.is_number(tk) else tk for tk in sub_tokens]
                        new_token_set.add(''.join(sub_tokens))
                    if len(new_token_set) > 1:
                        common_pattern = '[+]'
                        break
                if len(new_token_set) == 1:
                    common_pattern = new_token_set.pop()
                elif not new_token_set:
                    common_pattern = '[+]'
        common_pattern = re.sub(r'(\[\+\])+', '[+]', common_pattern)
        return common_pattern


    def get_para_type(self, token_set):
        new_token = '[NUM]'
        for token in token_set:
            if not self.is_number(token):
                new_token = '[+]'
                break
        return new_token


    def generate_token_link(self, headers):
        ''' Function to generate links between two consective tokens of each log message '''    
        for idx, msg in self.df_log[headers[-1]].iteritems():
            tokens = self.generate_tokens_with_splitters(msg)
            log_length = len(tokens)
            for i in xrange(0, log_length - 2, 2):
                token1 = (log_length, tokens[i])
                token2 = (log_length, tokens[i + 2])
                if tokens[i] == '$START$':
                    token1 = tokens[i]
                if tokens[i + 2] == '$END$':
                    token2 = tokens[i + 2]
                splitter = tokens[i + 1]
                self.token_freq_dict[(i, token1)] += 1
                self.in_link_dict[(i + 2, token2)].add((token1, splitter))
                self.out_link_freq_dict[(i, token1)][(splitter, token2)] += 1
                self.log_lines_over_link_dict[(i, token1)][(splitter, token2)].add(idx)
            self.token_freq_dict[(log_length - 1, '$END$')] += 1


    def generate_logformat_regex(self, logformat):
        ''' Function to generate regular expression to split log messages '''
        headers = []
        splitters = re.split(r'(\w+)', logformat)       
        regex = ''
        for k in xrange(len(splitters)):
            if k % 2 == 0:
                splitter = re.sub(' +', '\s+', splitters[k])                
                regex += splitter
            else:
                regex += '(?P<%s>.*?)'%splitters[k]             
                headers.append(splitters[k])        
        regex = re.compile('^' + regex + '$')
        return headers, regex


    def log2dataframe(self, log_file, regex, headers):
        ''' Function to transform log file to dataframe '''
        log_messages = []
        with open(log_file, 'r') as fin:
            for line in fin.readlines():
                try:
                    match = regex.search(line.strip())
                    message = [match.group(header) for header in headers]
                    log_messages.append(message)
                except Exception as e:
                    print 'Logformat does not match: ', line.strip()        
        self.df_log = pd.DataFrame(log_messages, columns=headers)



    def generate_tokens_with_splitters(self, string):
        ''' Function to generate a list of tokens and splitters '''
        tokens = re.split(r'([^A-Za-z0-9]*\s[^A-Za-z0-9\-]*)', string)
        tokens = ['$START$', ''] + tokens + ['', '$END$']
        return tokens


    def recur_get_path(self, pos, src, dest, visited, path, all_paths, log_lines, log_lines_with_path):
        ''' A recursive helper function to get all paths from arc to dest

        Arguments
        ---------
            pos: int, the position of source vertice
            src: str, source vertice
            dest: str, destination vertice
            visited: list
                a list of Boolean values to denote whether a vertice is visited
            path: list, a list to store the sequence of vertices visited
        '''
        visited.add((pos, src))
        # recur for all the vertices adjacent to this vertex
        for (w, v) in self.out_link_freq_dict[(pos, src)].keys():
            if (pos + 2, v) not in visited:
                # If current vertex is same as destination, then keep current path[]
                if isinstance(v, str) and v == dest:
                    path_tokens = reduce(lambda x, y : x + y, path)
                    path_str = ''.join(path_tokens)
                    all_paths.append(path_str)
                    log_lines_with_path[path_str] = log_lines[tuple(path)]
                # If current vertex is not destination
                else:
                    log_lines_intersect = set()
                    if path:
                        log_lines_intersect = log_lines[tuple(path)] & self.log_lines_over_link_dict[(pos, src)][(w, v)]
                    else:
                        log_lines_intersect = self.log_lines_over_link_dict[(pos, src)][(w, v)]
                    if log_lines_intersect:
                        path.append((w, v[-1]))                    
                        log_lines[tuple(path)] = log_lines_intersect
                    else:
                        continue
                    self.recur_get_path(pos + 2, v, dest, visited, path, all_paths, log_lines, log_lines_with_path)

        # Remove current edge from path[] and mark it as unvisited
        if path:
            path.pop()
        visited.discard((pos, src))



    def get_all_paths(self):
        ''' Get all paths from src to dest '''
        # Create lists to store paths
        path = []
        all_paths = []
        visited = set()
        log_lines = dict()
        log_lines_with_path = {}
        src = '$START$'
        dest = '$END$'
        # Call the recursive helper function to get all paths
        self.recur_get_path(0, src, dest, visited, path, all_paths, log_lines, log_lines_with_path)
        return all_paths, log_lines_with_path

    
    def post_processing(self, all_paths, log_lines_with_path):
        all_path_refined = []
        log_lines_with_path_refined = dict()
        # Identify IP address and remove negative NUM
        for path in all_paths:
            refined_path = re.sub('([0-9]+|\[NUM\])\.([0-9]+|\[NUM\])\.([0-9]+|\[NUM\])\.([0-9]+|\[NUM\])', '[IP]', path)
            refined_path = re.sub('\[IP\]:[0-9]+', '[IP]:[NUM]', refined_path)
            refined_path = re.sub(r'(?<=[^A-Za-z0-9])(-\[NUM\])', '[NUM]', refined_path)
            refined_path = re.sub(r'(?<=[^A-Za-z0-9])(-\[STATE\])', '[STATE]', refined_path)
            if refined_path in log_lines_with_path_refined:
                log_lines_with_path_refined[refined_path] |= log_lines_with_path[path]
            else:
                all_path_refined.append(refined_path)
                log_lines_with_path_refined[refined_path] = log_lines_with_path[path]

        # Merge the similar templates with different length
        similar_path = defaultdict(list)
        for path in all_path_refined:
            tokens = path.split()
            common_path_tokens = set()  # deduplicate consective para tokens
            for token in tokens:
                if any([tk in token for tk in self.para_token_set]):
                    common_path_tokens.add('[Para]')
                else:
                    common_path_tokens.add(token)
            common_path_tokens = frozenset(common_path_tokens)
            similar_path[common_path_tokens].append(path)
        log_lines_with_path_result = dict()
        all_path_result = []
        for key, templates in similar_path.iteritems():
            refined_path = ''
            if len(templates) > 1:
                template_list = map(self.split_message, templates)
                refined_path = mlcs.get_common_pattern(template_list)
            else:
                refined_path = templates[0]
            all_path_result.append(refined_path)
            for path in templates:
                if refined_path in log_lines_with_path_result:
                    log_lines_with_path_result[refined_path] |= log_lines_with_path_refined[path]
                else:
                    log_lines_with_path_result[refined_path] = log_lines_with_path_refined[path]
        all_path_result.sort()
        return all_path_result, log_lines_with_path_result



    def is_number(self, token):
        if token == '':
            return False
        elif token == '[NUM]':
            return True
        else:
            if token[0] in ('-', '+'):
                token = token[1:]
            if token.isdigit():
                return True
            else:
                try:
                    int(token, 16)
                    return True
                except Exception as e:
                    return False


    def split_message(self, message):
        regex = '%s'%('|'.join([re.sub(r'([^A-Za-z0-9\s])', r'\\\1', tk) for tk in self.para_token_set]))
        token_list = re.split('(%s)'%regex, message)
        token_list = [[l] if l in self.para_token_set else re.split(r'([^A-Za-z0-9])', l) for l in token_list]
        message = [item for sublist in token_list for item in sublist]
        message = filter(lambda x: x != '', message)
        return message



    def template_match(self, event_template, headers):
        template_dict = self.generate_template_dict(event_template)
        template_counter = Counter()
        self.df_log['EventId'] = None
        self.df_log['EventTemplate'] = None
        for idx, msg in self.df_log[headers[-1]].iteritems():
            start_token = msg.split()[0]
            event = None
            if start_token in template_dict:
                for regex, evt in template_dict[start_token].iteritems():
                    if re.search(regex, msg.strip()):
                        event = evt
                        break
            if not event:
                for regex, evt in template_dict['OTHERS'].iteritems():
                    if re.search(regex, msg.strip()):
                        event = evt
                        break
            if event:
                self.df_log.set_value(idx, 'EventId', event[0])
                self.df_log.set_value(idx, 'EventTemplate', event[1])
                template_counter[event] += 1
            else:
                print 'Line does not match: ', (idx, msg)
                self.df_log.set_value(idx, 'EventId', 'NO_MATCH')
        return template_counter


    def generate_template_dict(self, event_template):
        para_token_set = set(['[NUM]', '[*]', '[IP]'])
        template_dict = defaultdict(dict)
        df_template = pd.read_csv(os.path.join(self.indir, event_template))
        for idx, row in df_template.iterrows():
            template = row[1]
            start_token = template.split()[0]
            for token in para_token_set:
                if token in start_token:
                    start_token = 'OTHERS'
                    break
            template = re.sub(r'([^A-Za-z0-9\s])', r'\\\1', template)
            regex = template.replace('\[NUM\]', '(-?\d+)')
            regex = regex.replace('\[\*\]', '(.*?)')
            regex = regex.replace('\[IP\]', '(\d+\.\d+\.\d+\.\d+)')
            regex = '^' + regex + '$'
            template_dict[start_token][regex] = (row[0], row[1])
        return template_dict
            





























































































































































































































            































































































                






































                    











































































