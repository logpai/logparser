import re


class OracleTemplates:

    def __init__(self, path: str):
        self.messages = {}
        with open(path) as f_read:
            for line in f_read:
                line = re.sub("([<>=:;,'\(\)\{\}])", r' \1 ', line)
                msg = line.split()
                key = len(msg)
                if key in self.messages:
                    self.messages[key].append(msg)
                else:
                    self.messages[key] = []
                    self.messages[key].append(msg)
