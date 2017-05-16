import re
import sys, os
import pandas as pd
from collections import defaultdict, deque


def parse(log_file, logformat=None, outdir='result/'):
    if logformat is None:
        sys.exit('Please provide log format as necessary!')
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    (headers, regex) = generate_regex(logformat)
    df_log = log2df(log_file, regex, headers)
    df_log = df_log.head(50)
    df_content = load_message_content(df_log, headers)
    (token_dict, out_link_dict, in_link_dict) = generate_token_link(df_content)
    graph = generate_template_graph(token_dict, out_link_dict, in_link_dict)
    print graph.graph
    all_paths = graph.get_all_paths((0, '$START$'), '$END$')
    print all_paths


def prune_graph(pos, token1, token2, splitter, token_dict, out_link_dict, in_link_dict):
    link_freq = out_link_dict[(pos, token1)][(token2, splitter)]
    token1_freq = token_dict[(pos, token1)]
    token2_freq = token_dict[(pos + 2, token2)]
    prob_forward = float(link_freq) / token1_freq
    prob_backward = float(link_freq) / token2_freq
    token1_out_links = len(out_link_dict[(pos, token1)].keys())
    token2_in_links = len(in_link_dict[(pos + 2, token2)])
    u = token1
    v = token2
    if token1.decode('utf-8', 'ignore').isnumeric()\
        and token2.decode('utf-8', 'ignore').isnumeric():
        u = '[NUM]'
        v = '[NUM]'
    else:
        if prob_forward == 1 and prob_backward < 1:
            if prob_backward <= 0.2 or (prob_backward < 1 and token1_freq <= 1):
                # if token1_freq <= 5 or token2_in_links >= 5:
                if token1.decode('utf-8', 'ignore').isnumeric():
                    u = '[NUM]'
                else:
                    u = '[*]'
        elif prob_backward == 1 and prob_forward < 1:
            if prob_forward <= 0.2 or (prob_forward < 1 and token2_freq <= 1):
                # if token2_freq <= 5 or token1_out_links >= 5:
                if token2.decode('utf-8', 'ignore').isnumeric():
                    v = '[NUM]'
                else:
                    v = '[*]'
        else:
            if token1.decode('utf-8', 'ignore').isnumeric():
                u = '[NUM]'
            else:
                u = '[*]'
            if token2.decode('utf-8', 'ignore').isnumeric():
                v = '[NUM]'
            else:
                v = '[*]'
    return u, v


def generate_template_graph(token_dict, out_link_dict, in_link_dict):
    ''' Function to build log template graph '''

    graph = TemplateGraph()
    queue = deque()
    queue.append((0, '$START$'))
    while queue:
        (pos, token1) = queue.popleft()
        for (token2, splitter) in out_link_dict[(pos, token1)].keys():
            queue.append((pos + 2, token2))
            if pos > 0:
                (u, v) = prune_graph(pos, token1, token2, splitter, token_dict, out_link_dict, in_link_dict)
                if pos == 2 and u != token1:
                    graph.add_edge((0, '$START$'), (2, u), '')
                if v != token2:
                    graph.add_edge((pos, u), (pos + 2, v), splitter)


    with open('link.txt', 'w') as fout:
        for k1, v1 in out_link_dict.items():
            (pos, token1) = k1
            for k2, v2 in v1.items():
                (token2, splitter) = k2
                link_freq = v2
                token1_freq = token_dict[(pos, token1)]
                token2_freq = token_dict[(pos + 2, token2)]
                prob_forward = float(link_freq) / token1_freq
                prob_backward = float(link_freq) / token2_freq
                token1_out_links = len(v1.keys())
                token2_in_links = len(in_link_dict[(pos + 2, token2)])
                fout.write('%d\t%s%s%s\t(%d, %d, %d, %.2f, %.2f, %d, %d)\n'\
                          %(pos, token1, splitter, token2, token1_freq, link_freq, 
                          token2_freq, prob_forward, prob_backward, token1_out_links, token2_in_links))

    return graph            
                # u = token1
                # v = token2
                # if token1.decode('utf-8', 'ignore').isnumeric()\
                #     and token2.decode('utf-8', 'ignore').isnumeric():
                #     u = '[NUM]'
                #     v = '[NUM]'
                # else:
                #     if prob_forward == 1 and prob_backward < 1:
                #         if prob_backward <= 0.2 or (prob_backward < 1 and token1_freq <= 1):
                #             # if token1_freq <= 5 or token2_in_links >= 5:
                #             if token1.decode('utf-8', 'ignore').isnumeric():
                #                 u = '[NUM]'
                #             else:
                #                 u = '[*]'
                #     elif prob_backward == 1 and prob_forward < 1:
                #         if prob_forward <= 0.2 or (prob_forward < 1 and token2_freq <= 1):
                #             # if token2_freq <= 5 or token1_out_links >= 5:
                #             if token2.decode('utf-8', 'ignore').isnumeric():
                #                 v = '[NUM]'
                #             else:
                #                 v = '[*]'
                #     else:
                #         if token1.decode('utf-8', 'ignore').isnumeric():
                #             u = '[NUM]'
                #         else:
                #             u = '[*]'
                #         if token2.decode('utf-8', 'ignore').isnumeric():
                #             v = '[NUM]'
                #         else:
                #             v = '[*]'
                # print pos, ', ', u, ', ', v, ', ', splitter
                # graph.add_edge((pos, u), (pos + 2, v), splitter)


def generate_token_link(df):
    ''' Function to generate links between two consective tokens '''

    # out_link_dict = {(position, token1): {(token2, splitter): freq}}
    out_link_dict = defaultdict(lambda: defaultdict(int))
    # in_link_dict = {(position, token2): set(token1)}
    in_link_dict = defaultdict(set)
    # token_freq_dict = {(position, token): freq}
    token_freq_dict = defaultdict(int)
    for idx, row in df.iterrows():
        i = 0
        while row[i] != '$END$':
            token_freq_dict[(i, row[i])] += 1
            in_link_dict[(i + 2, row[i + 2])].add(row[i])
            out_link_dict[(i, row[i])][(row[i + 2], row[i + 1])] += 1
            i += 2
        token_freq_dict[(i, '$END$')] += 1
    return token_freq_dict, out_link_dict, in_link_dict


def generate_regex(logformat):
    ''' Function to generate regular expression to split log messages '''
    headers = re.findall(r'(\w+)', logformat)
    regex = logformat
    for tag in headers:
        regex = re.sub(tag, '(?P<%s>.*?)'%tag, regex)
    regex = re.compile('^' + regex + '$')
    return headers, regex


def log2df(log_file, regex, headers):
    ''' Function to transform log file to dataframe '''
    log_messages = []
    with open(log_file, 'r') as fin:
        for line in fin.readlines():
            match = regex.search(line.strip())
            message = [match.group(header) for header in headers]
            log_messages.append(message)
    df = pd.DataFrame(log_messages, columns=headers)
    return df


def load_message_content(df_log, headers):
    ''' Function to load log message content to dataframe '''
    df_content = pd.DataFrame()
    for msg_content in df_log[headers[-1]].tolist():
        splitters = re.findall(r'[^A-Za-z0-9\s]|\s+', msg_content)
        tokens = re.split(r'[^A-Za-z0-9\s]|\s+', msg_content)
        tokens = interleave_tokens_splitters(tokens, splitters)
        df_content = pd.concat([df_content, pd.DataFrame([tokens])], ignore_index=True)
    return df_content


def interleave_tokens_splitters(tokens, splitters):
    ''' Function to interleave lists of tokens and splitters '''
    interleave_tokens = ['$START$', '']
    i = 0
    j = 0
    while True:
        if j < len(tokens):
            interleave_tokens.append(tokens[j])
            j += 1
        if i < len(splitters):
            if splitters[i] == ' ':
                interleave_tokens.append(splitters[i])
            else:
                interleave_tokens += ['', splitters[i], '']
            i += 1
        elif j == len(tokens):
            break
    interleave_tokens += ['', '$END$']
    return interleave_tokens 

class TemplateGraph(object):
    '''
    This class represents a directed acyclic graph of log templates using 
    adjacency list representation

    '''
    
    def __init__(self):   
        # Default dictionary to store graph
        self.graph = defaultdict(set)
        # Default dictionary to mark all the edges as visited or not
        self.visited = defaultdict(bool)
        # Store available paths (or equivalently, log templates)
        self.all_paths = []


    def add_edge(self, u, v, w):
        ''' Function to add an edge to graph

        Arguments
        ---------
            pos: int, the starting position of edge
            u: str, the starting token
            v: str, the ending token
            w: str, the splitter (or equivalently, edge weight)
        '''
        self.graph[u].add((v, w))
        self.visited[(u, v, w)] = False


    def get_all_paths_util(self, src, dest, weight, visited, path):
        ''' A recursive helper function to get all paths from src to dest
        
        Arguments
        ---------
            pos: int, the position of source vertice
            src: str, source vertice
            dest: str, destination vertice
            visited: list
                a list of boolen values to denote whether a vertice is visited
            path: list, a list to store the sequence of vertices visited 
        '''
        # Mark the current edge as visited and store in path
        if path:
            visited[(path[-1], src, weight)] = True
        path.append((src, weight))
        # If current vertex is same as destination, then keep current path[]
        if dest == src[1]:
            self.all_paths.append(list(path))
        else:
            # If current vertex is not destination,
            # recur for all the vertices adjacent to this vertex
            for (v, w) in self.graph[src]:
                if visited[(src, v, w)] == False:
                    self.get_all_paths_util(v, dest, w, visited, path)
                     
        # Remove current edge from path[] and mark it as unvisited
        path.pop()
        if path:
            visited[(path[-1], src, weight)] = False


    def get_all_paths(self, src, dest):
        ''' Get all paths from src to dest '''

        # Create a list to store paths
        path = []
        # Inital weight
        weight = None
        # Call the recursive helper function to get all paths
        self.get_all_paths_util(src, dest, weight, self.visited, path)
        return self.all_paths