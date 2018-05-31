from typing import List

#from orderedset._orderedset import OrderedSet
from numpy import median, mean

from ..chromosome.chromosome import Chromosome
from ..utility.Chromosome_Generator import ChromosomeGenerator


class Objective2D:

    def __init__(self,  p_generator: ChromosomeGenerator):
        self.generator = p_generator

    # override method
    def compute_objective(self, chromosome: Chromosome):
        """ Evaluate a chromosome
                compute 2 objectives: 
                        - frequency: #matched log messages ((/#log messages)/#templates)
                        - specificity: fixed words / #words in a template
                :param chromosome: the list of templates
                :return: frequency value, specificity value
                """
        average_specificity = []
        average_frequency = []

        # compute frequency and specificity for each template
        for key in chromosome.templates:
            template_cluster = chromosome.templates[key]
            for template in template_cluster:
                template.specificity = 0

                for word in template.token:
                    if word != "*" and word != "#spec#":
                        template.specificity += 1.0

                template.specificity /= len(template.token)
                average_specificity.append(template.specificity)

                if template.specificity > 0:
                    average_frequency.append(1.0 * len(template.matched_lines) / len(self.generator.messages[key]))
                else:
                    average_frequency.append(0)

        # average specificity across templates
        average_specificity = mean(average_specificity)
        # average frequency across templates
        average_frequency = mean(average_frequency)

        chromosome.coverage = 1
        return [average_specificity, average_frequency]

    def get_messages(self):
        messages = list()
        for cluster in self.generator.messages.values():
            messages.extend(cluster)
        return messages
