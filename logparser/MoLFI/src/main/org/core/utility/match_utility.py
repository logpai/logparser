from typing import List, Set

from ..chromosome.chromosome import Chromosome
from ..chromosome.template import Template
from ..utility.message import Message
"""
    This utility contains methods used to control the templates
    
"""

def compute_matched_lines(messages: dict, template: Template):
    # if the templates has not be changed
    # we don't need to recompute the list of matched lines
    if not template.is_changed():
        return
    # Otherwise, we recompute the list of matched lines
    template.matched_lines = []
    cluster_id = template.get_length()
    for index in range(0, len(messages[cluster_id])):
        message = messages[cluster_id][index]
        if match(message, template):
            template.matched_lines.append(index)
    # Now the template has to be set as NOT CHANGED
    template.set_changed(False)


def match(message: Message, template: Template):
    """ Compare two lists of strings
    :param message: a message from the log file
    :param template: a template from the chromosome
    :return: True if two list are equal
             False if two lists are different
    """
    if len(message.words) != template.get_length():
        return False
    for index in range(0, template.get_length()):
        if template.token[index] == "*" or template.token[index] == "#spec#":
            continue
        if template.token[index] != message.words[index]:
            return False
    return True


def template_match(template1: Template, template2: Template):
    """ Compare two lists of strings
    :param template1: first template
    :param template2: second template
    :return: True if template1 is a "sub-set" of template2
             False if two lists are different
    """
    if template1.get_length() != template2.get_length():
        return False
    for index in range(0, template1.get_length()):
        if template2.token[index] == "*":
            continue
        if template1.token[index] != template2.token[index]:
            return False
    return True


def remove_sub_templates(chromosome: Chromosome, cluster_id: int):
    chromosome.templates[cluster_id] = list(set(chromosome.templates[cluster_id]))

    template_to_remove = set()
    derive_sub_template(chromosome.templates[cluster_id], template_to_remove)

    for template in template_to_remove:
        chromosome.templates[cluster_id].remove(template)


def remove_super_templates(chromosome: Chromosome, cluster_id: int):
    chromosome.templates[cluster_id] = list(set(chromosome.templates[cluster_id]))

    template_to_remove = set()
    derive_super_template(chromosome.templates[cluster_id], template_to_remove)

    for template in template_to_remove:
        chromosome.templates[cluster_id].remove(template)


def derive_sub_template(partition: List[Template], template_to_remove: Set[Template]):
    for index1 in range(0, len(partition)-1):
        template1 = partition[index1]
        set1 = set(template1.matched_lines)
        for index2 in range(index1+1, len(partition)):
            template2 = partition[index2]
            set2 = set(template2.matched_lines)
            if template1 == template2:
                template_to_remove.add(template1)
                continue
            if set1.issubset(set2):
                template_to_remove.add(template1)
            else:
                if set2.issubset(set1):
                    template_to_remove.add(template2)
    return template_to_remove


def derive_super_template(partition: List[Template], template_to_remove: Set[Template]):
    for index1 in range(0, len(partition)-1):
        template1 = partition[index1]
        set1 = set(template1.matched_lines)
        for index2 in range(index1+1, len(partition)):
            template2 = partition[index2]
            set2 = set(template2.matched_lines)
            if template1 == template2:
                template_to_remove.add(template1)
                continue
            if set2.issubset(set1):
                template_to_remove.add(template1)
            else:
                if set1.issubset(set2):
                    template_to_remove.add(template2)
    return template_to_remove


def remove_all_stars_template(chromosome: Chromosome, cluster_id: int):
    template_to_remove = set()
    for template in chromosome.templates[cluster_id]:
        has_no_star = False
        for token in template.token:
            if not (token == "*"):
                has_no_star = True
                break
        if not has_no_star:
            template_to_remove.add(template)

    for template in template_to_remove:
        chromosome.delete_template(template)
