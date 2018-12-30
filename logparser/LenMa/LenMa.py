"""
Description: This file implements the Lenma algorithm for log parsing
Author: LogPAI team
License: MIT
"""

from templateminer import lenma_template 
import pandas as pd
import re
import os
import hashlib
from collections import defaultdict
from datetime import datetime

class LogParser(object):
    def __init__(self, indir, outdir, log_format, threshold=0.9, predefined_templates=None, rex=[]):
        self.path = indir
        self.savePath = outdir
        self.logformat = log_format
        self.rex = rex
        self.wordseqs = []
        self.df_log = pd.DataFrame()
        self.wordpos_count = defaultdict(int)
        self.templ_mgr = lenma_template.LenmaTemplateManager(threshold=threshold, predefined_templates=predefined_templates)
        self.logname = None

    def parse(self, logname):
        print('Parsing file: ' + os.path.join(self.path, logname))
        self.logname = logname
        starttime = datetime.now()
        headers, regex = self.generate_logformat_regex(self.logformat)
        self.df_log = self.log_to_dataframe(os.path.join(self.path, self.logname), regex, headers, self.logformat)
        for idx, line in self.df_log.iterrows():
            line = line['Content']
            if self.rex:
                for currentRex in self.rex:
                    line = re.sub(currentRex, '<*>', line)
            words = line.split()
            self.templ_mgr.infer_template(words, idx)
        self.dump_results()
        print('Parsing done. [Time taken: {!s}]'.format(datetime.now() - starttime))

    def dump_results(self):
        if not os.path.isdir(self.savePath):
            os.makedirs(self.savePath)

        df_event = []
        templates = [0] * self.df_log.shape[0]
        template_ids = [0] * self.df_log.shape[0]
        for t in self.templ_mgr.templates:
            template = ' '.join(t.words)
            eventid = hashlib.md5(' '.join(template).encode('utf-8')).hexdigest()[0:8]
            logids = t.get_logids()
            for logid in logids:
                templates[logid] = template
                template_ids[logid] = eventid
            df_event.append([eventid, template, len(logids)])

        self.df_log['EventId'] = template_ids
        self.df_log['EventTemplate'] = templates

        pd.DataFrame(df_event, columns=['EventId', 'EventTemplate', 'Occurrences']).to_csv(os.path.join(self.savePath, self.logname + '_templates.csv'), index=False)
        self.df_log.to_csv(os.path.join(self.savePath, self.logname + '_structured.csv'), index=False)


    def log_to_dataframe(self, log_file, regex, headers, logformat):
        ''' Function to transform log file to dataframe '''
        log_messages = []
        linecount = 0
        with open(log_file, 'r') as fin:
            for line in fin.readlines():
                try:
                    match = regex.search(line.strip())
                    message = [match.group(header) for header in headers]
                    log_messages.append(message)
                    linecount += 1
                except Exception as e:
                    pass
        logdf = pd.DataFrame(log_messages, columns=headers)
        logdf.insert(0, 'LineId', None)
        logdf['LineId'] = [i + 1 for i in range(linecount)]
        return logdf

    def generate_logformat_regex(self, logformat):
        ''' 
        Function to generate regular expression to split log messages
        '''
        headers = []
        splitters = re.split(r'(<[^<>]+>)', logformat)
        regex = ''
        for k in range(len(splitters)):
            if k % 2 == 0:
                splitter = re.sub(' +', '\s+', splitters[k])
                regex += splitter
            else:
                header = splitters[k].strip('<').strip('>')
                regex += '(?P<%s>.*?)' % header
                headers.append(header)
        regex = re.compile('^' + regex + '$')
        return headers, regex
