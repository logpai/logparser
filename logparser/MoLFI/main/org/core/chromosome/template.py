from typing import List


class Template:
    """ An object representing the smallest element of a chromosome which is a template
        Template is a list of strings
    """

    def __init__(self, p_template: List[str]):
        """ The constructor of the Class Template
        initialize the object with a list of strings
        and initialize the frequency and specificity with 0.0
        and an empty list that will contain the line number matching the template
        """
        self.token = p_template
        self.specificity = 0.0
        self.matched_lines = []
        self.changed = True

    def get_length(self):
        """ Gets the number of strings in the list    
        """
        return len(self.token)

    def to_string(self):
        """ Returns the template's token as one string
        """
        s = "[ "
        for i in self.token:
            s = s+i+' '

        s = s + ']'
        return s

    def is_changed(self):
        """ Returns the status of the template (changed or did not change)
        """
        return self.changed

    def set_changed(self, p_changed : bool):
        """ Sets the status of a template to True if one of its tokens changes,
        else the status is False (not changed)
        """
        self.changed = p_changed
