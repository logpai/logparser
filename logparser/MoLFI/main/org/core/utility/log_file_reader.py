

def log_file_reader(logpath):

    with open(logpath) as f_read:
        lines = f_read.readlines()

    return lines

