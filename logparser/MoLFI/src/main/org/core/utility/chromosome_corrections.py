import random
from ..chromosome.chromosome import Chromosome
from ..chromosome.template import Template

random.seed(0)
def check_variable_parts(chromosome: Chromosome, messages: dict):
    """ checks each variable element in a template agiants the values of the matched lines
    
    :param chromosome: the chromosome with the templates
    :param messages: the original log messages
    :return: possibly corrected templates
    """
    for key in chromosome.templates.keys():
        for template in chromosome.templates[key]:
            for index in range(0, len(template.token)):
                token = template.token[index]
                words = set([])
                # gets all values at position index from the matched lines
                if token == "*" or token == "#spec#":
                    for message_index in template.matched_lines:
                        message = messages[key][message_index]
                        words.add(message.words[index])
                    # if all matched lines have the same word,
                    # the star in the template will be replaced with that word
                    if len(words) == 1:
                        template.token[index] = words.pop()


def is_all_star_template(template: Template):
    has_no_star = False
    for token in template.token:
        if not (token == "*" or token.startswith("[") or token == "#spec#"):
            has_no_star = True
            break
    return not has_no_star


def fix_all_star_template(ch: Chromosome, cluster_id: int, template_index: int, messages: dict):
    if is_all_star_template(ch.templates[cluster_id][template_index]):
        star_indexes = list()
        template = ch.templates[cluster_id][template_index]
        for index in range(0, template.get_length()-1):
            if template.token[index] == '*':
                star_indexes.append(index)
        if len(star_indexes) > 0:
            # print(star_indexes)
            index = random.choice(star_indexes)
            words = set([])
            for message_index in ch.templates[cluster_id][template_index].matched_lines:
                message = messages[cluster_id][message_index].words
                words.add(message[index])
            if len(words) > 0:
                ch.templates[cluster_id][template_index].token[index] = words.pop()
                ch.templates[cluster_id][template_index].set_changed(True)
