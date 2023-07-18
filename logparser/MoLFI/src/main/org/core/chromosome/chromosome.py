
from .template import Template


class Chromosome:
    """ A chromosome in this class is a dictionary
        key: int
        value: List[Templates]
    """

    def __init__(self, p_templates: dict()):
        """ The constructor with an attribute of type List of Template
        :param p_templates: a dictionary of Template
        """
        self.templates = p_templates
        self.coverage = 0

    def add_template(self, template: Template):
        """ Adds a template to the chromosome
        
        :param template: an object of type Template
        :return: the template will be added to the corresponding cluster
        with key = len(template)
        """
        key = template.get_length()
        if key in self.templates.keys():
            self.templates[key].append(template)
        else:
            self.templates[key] = []
            self.templates[key].append(template)

    def delete_template(self, template: Template):
        """ Deletes the template from the given cluster id      
        :param 
            index: cluster id
        :return  
            the cluster without the template
        :raises 
            IndexError: An error occurs if a negative cluster id is provided
            or if the cluster id doesn't exist
        """
        key = template.get_length()
        if key not in self.templates:
            raise IndexError("No cluster with the giving id!")

        self.templates[key].remove(template)

    def number_of_clusters(self):
        """ Get the number of clusters inside the chromosome
        :return: 
            an integer: number of cluster 
        """
        return len(self.templates.keys())

    def cluster_size(self, cluster_id: int):
        """ Get the number of templates inside a given cluster
        :return: 
            an integer: number of templates 
        """
        return len(self.templates[cluster_id])

    def all_templates(self):
        """ Returns the total number of templates of a chromosome
        """
        number_templates = 0
        for key in self.templates.keys():
            number_templates = number_templates + self.cluster_size(key)
        return number_templates

    def to_string(self):
        """ Prints the content of a chromosome
       :return: all templates as a string 
        """
        s = ""
        for list_t in self.templates.values():
            for t in list_t:

                s = s + t.to_string() + "\n"
        return s
