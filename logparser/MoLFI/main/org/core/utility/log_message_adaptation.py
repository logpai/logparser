import re

from numpy.core.defchararray import startswith

from ..utility.message import Message

'''
    change the log message if it contains a specific bloc of words
    that matched a special regular expression
'''

# sub_sign = ''
sub_sign = '   #spec#   '

def adapt_log_message(log_message, regex=None):
    # first detect time (12:34:56 or 12:54 )
    # date 21-03-2005 03/04/12
    # ip address
    # memory address
    # file path
    # mac address
    # before adding space around ':'

    is_time = re.findall('(^|\s+)(\d){1,2}:(\d){1,2}(|:(\d){2,4})(\s+|$)', log_message)
    if is_time:
        log_message = re.sub('(^|\s+)(\d){1,2}:(\d){1,2}(|:(\d){2,4})(\s+|$)', sub_sign, log_message)

    is_date = re.findall('(^|\s)(\d{1,2}(-|/)\d{1,2}(-|/)\d{2,4})(\s|$)', log_message)
    if is_date:
        log_message = re.sub('(^|\s)(\d{1,2}(-|/)\d{1,2}(-|/)\d{2,4})(\s|$)', sub_sign, log_message)

    is_ip_address1 = re.findall('(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)', log_message)
    if is_ip_address1:
        log_message = re.sub('(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)', sub_sign, log_message)

    is_ip_address = re.findall('(|^)\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(|$)', log_message)
    if is_ip_address:
        log_message = re.sub('(|^)\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(|$)', sub_sign, log_message)

    is_file_path = re.findall('(/[\d+\w+\-_\.\#\$]*[/\.][\d+\w+\-_\.\#\$/*]*)+', log_message)
    if is_file_path:
        log_message = re.sub('(|\w+)(/[\d+\w+\-_\.\#\$]*[/\.][\d+\w+\-_\.\#\$/*]*)+', sub_sign, log_message)

    is_memory_address = re.findall('0x([a-zA-Z]|[0-9])+', log_message)
    if is_memory_address:
        log_message = re.sub('0x([a-zA-Z]|[0-9])+', sub_sign, log_message)

    is_hex = re.findall('(^|\s)([0-9A-F]){9,}(\s|$)', log_message)
    if is_hex:
        log_message = re.sub('(^|\s)([0-9A-F]){9,}(\s|$)', sub_sign, log_message)

    is_hex1 = re.findall('(^|\s)([0-9a-f]){8,}(\s|$)', log_message)
    if is_hex1:
        log_message = re.sub('(^|\s)([0-9a-f]){8,}(\s|$)', sub_sign, log_message)

    is_mac_address = re.findall('([0-9A-F]{2}[:-]){5,}([0-9A-F]{2})', log_message)
    if is_mac_address:
        log_message = re.sub('([0-9A-F]{2}[:-]){5,}([0-9A-F]{2})', sub_sign, log_message)

    is_number = re.findall('(^| )\d+( |$)', log_message)
    if is_number:
        log_message = re.sub('(^| )\d+( |$)', sub_sign, log_message)

    # add space around '-->' [=:,] <> () [ ] { }
    log_message = re.sub("([<>=:,;'\(\)\{\}\[\]])", r' \1 ', log_message)
    # regex is empty if not given as parameter
    if regex is None:
        regex = []
    for i in range(len(regex)):
        match = re.findall(regex[i], log_message)
        if match:
            log_message = re.sub(regex[i], sub_sign, log_message)

    # let's identify the prefixes that we don't have to change
    prefix_regex = "^[ ]*\[[A-Z *]+\]"
    match = re.findall(prefix_regex, log_message)
    if len(match) > 0:
        log_message = log_message.replace(match[0], match[0].replace(' ', ''))

    log_message = log_message.replace("-- >", "-->")
    message = Message(log_message.split())

    for index in range(0, message.get_length()):
        match = False
        match = match or re.findall(".xml", message.words[index]) # xml files
        if match:
            message.words[index] = sub_sign.strip()
    return message
