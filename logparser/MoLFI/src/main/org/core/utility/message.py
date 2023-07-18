from typing import List


class Message:
    """ This class represents a log message as a list of strings
    """

    def __init__(self, p_message: List[str]):
        """ Initialize the objet with an list of strings
        :param p_message
        """
        self.words = p_message

    def get_length(self):
        """ Get the number of strings in the list
        """
        return len(self.words)

    def to_string(self):
        """ Convert the list of words to one string
        """
        string = ""
        for index in range(0, len(self.words)):
            if index < len(self.words) - 1:
                string = string + self.words[index] + " "
            else:
                string = string + self.words[index]
        return string
