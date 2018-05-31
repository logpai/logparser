import random
import re

from numpy.core.defchararray import startswith
from ..chromosome.chromosome import Chromosome
from ..chromosome.template import Template
from ..utility.Chromosome_Generator import ChromosomeGenerator
from ..utility.match_utility import compute_matched_lines


class ChromosomeMutator:
    def __init__(self, gen_ch: ChromosomeGenerator):
        """ Initialize the class with the list of log messages
        """
        self.chGenerator = gen_ch

    def change_template(self, ch: Chromosome, cluster_id: int, template_index: int):
        # get the template at position index
        template = ch.templates[cluster_id][template_index]

        star_indexes = list()
        non_star_indexes = list()
        for index in range(0, template.get_length()):
            if template.token[index] == '*':
                star_indexes.append(index)
            elif not (startswith(template.token[index], "[") or template.token[index] == '#spec#' or
                            re.match("\B\W\Z", template.token[index])):
                non_star_indexes.append(index)

        if random.random() <= 0.50:
            if len(star_indexes) > 0:
                index = random.choice(star_indexes)
                message_index = random.choice(template.matched_lines)
                message = self.chGenerator.messages[cluster_id][message_index]
                template.token[index] = message.words[index]
        else:
            if len(non_star_indexes) > 0:
                index = random.choice(non_star_indexes)
                clone = Template(template.token[:])
                clone.token[index] = '*'
                compute_matched_lines(self.chGenerator.messages, clone)
                if len(clone.matched_lines) > len(template.matched_lines):
                    template.token[index] = '*'

        template.set_changed(True)
        compute_matched_lines(self.chGenerator.messages, template)

    def update_info_template(self, chromosome: Chromosome):
        for template_list in chromosome.templates.values():
            for t in template_list:
                compute_matched_lines(self.chGenerator.messages, t)
