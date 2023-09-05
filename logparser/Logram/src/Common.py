"""
This file is modified from:
https://github.com/BlueLionLogram/Logram/tree/master/Evaluation
"""

import regex as re

MyRegex = [
    r"blk_(|-)[0-9]+",  # block id
    r"(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)",  # IP
    r"(?<=[^A-Za-z0-9])(\-?\+?\d+)(?=[^A-Za-z0-9])|[0-9]+$",  # Numbers
]


def preprocess(logLine, specialRegex):
    line = logLine
    for regex in specialRegex:
        line = re.sub(regex, "<*>", " " + logLine)
    return line


def tokenSpliter(logLine, regex, specialRegex):
    match = regex.search(logLine.strip())
    # print(match)
    if match == None:
        tokens = None
        pass
    else:
        message = match.group("Content")
        # print(message)
        line = preprocess(message, specialRegex)
        tokens = line.strip().split()
    # print(tokens)
    return tokens, message


def regexGenerator(logformat):
    headers = []
    splitters = re.split(r"(<[^<>]+>)", logformat)
    regex = ""
    for k in range(len(splitters)):
        if k % 2 == 0:
            splitter = re.sub(" +", "\\\s+", splitters[k])
            regex += splitter
        else:
            header = splitters[k].strip("<").strip(">")
            regex += "(?P<%s>.*?)" % header
            headers.append(header)
    regex = re.compile("^" + regex + "$")
    return regex
