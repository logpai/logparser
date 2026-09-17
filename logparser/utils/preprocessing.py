import re

weekday_abb = ['Mon', 'Tue', 'Wed', "Thu", 'Fri', 'Sat', 'Sun']
weekday = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
month_abb = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
months = ["January", "February", "March", "April",
    "May", "June", "July", "August",
    "September", "October", "November", "December"]

regex_match = {
    'IPv4_port': r'(/|)(\d+\.){3}\d+(:\d+)?',
    'host_port': r'([\w-]+\.)+[\w-]+\:\d+',
    'package_host': r'([\w-]+\.){2,}[\w-]+(\$[\w-]+)*(\@[\w-]+)?',
    'Mac_address': r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$',
    'IPv6': r'(([0-9a-fA-F]{1,4}:){7}([0-9a-fA-F]{1,4}|:)|(([0-9a-fA-F]{1,4}:){1,7}|:):((:[0-9a-fA-F]{1,4}){1,7}|:))',
    'path': r'(/|)(([\w.-]+|\<\*\>)/)+([\w.-]+|\<\*\>)',
    'size': r'\b\d+\.?\d*\s?([KGTMkgtm]?(B|b)|([KGTMkgtm]))\b',
    'duration': r'\b\<?\d+\s?(sec|s|ms)\b',
    'block': r'blk\_\-?\d+',
    'numerical': r'\b(\-?\+?\d+\.?\d*)\b|\b0[Xx][a-fA-F\d]+\b|\b[a-fA-F\d]{4,}\b',
    'time': r'\b\d{2}:\d{2}(:\d{2}|:\d{2},\d+)?\b',
    'date': r'\b(\d{4}-\d{2}-\d{2})|\d{4}/\d{2}/\d{2}\b',
    'url': r'\bhttps?:\/\/(www\.)?[a-zA-Z0-9-]+(\.[a-zA-Z]{2,})+(:[0-9]{1,5})?(\/[^\s]*)?\b',
    'weekday_months': r'\b(%s)\b' % '|'.join(weekday_abb+weekday+month_abb+months),
}

regex_map = {
    'path': '<*>',
    'URL': '<*>',
    'IPv4_port': '<*>:<*>',
    'package_host': '<*>',
    'Mac_address': '<*>',
    'host_port': '<*>:<*>',
    'IPv6': '<*>',
    'size': '<*>',
    'numerical': '<*>',
    'duration': '<*>',
    'block': '<*>',
    'time': '<*>:<*>:<*>',
    'date1': '<*>-<*>-<*>',
    'date2': '<*>/<*>/<*>',
    'url': '<*>',
    'weekday_months': '<*>',
}

sequence = ['url', 'IPv4_port', 'host_port', 'package_host', 'IPv6', 'Mac_address', 'time', 'path', 'block', 'date', 'duration', 'size', 'numerical', 'weekday_months']
def preprocess(log, use_keys=False, estimation_stage=False, use_sequence=sequence):
    matched_types = []
    new_log = log
    if estimation_stage:
        if use_keys:
            # Replace the ones with symbols
            for key in use_sequence:
                new_log = re.sub(regex_match[key], regex_map[key], new_log)
                if new_log != log: 
                    matched_types.append(key)
                    log = new_log
        else:
            # Combine regex patterns into a single pattern
            for key in use_sequence:
                new_log = re.sub(regex_match[key], '<*>', new_log)
                if new_log != log: 
                    matched_types.append(key)
                    log = new_log
        # Eliminate repetitive <*>s
        new_log = re.sub(r'(\<\*\>\s?)+\<\*\>', '<*>', new_log)
        return new_log, sequence, matched_types
    else:
        if use_keys:
            # Replace the ones with symbols
            for key in use_sequence:
                new_log = re.sub(regex_match[key], regex_map[key], new_log)
        else:
            # Combine regex patterns into a single pattern
            for key in use_sequence:
                new_log = re.sub(regex_match[key], '<*>', new_log)
        # Eliminate repetitive <*>s
        new_log = re.sub(r'(\<\*\>\s?)+\<\*\>', '<*>', new_log)
        return new_log