from typing import List

from definitions import ROOT_DIR
from main.org.core.chromosome.chromosome import Chromosome
from main.org.core.chromosome.template import Template



def validation(pop: List[Chromosome], templates: dict, validation_file_path: str):

    validation_file = open(validation_file_path, 'a')
    for i, ch in enumerate(pop):
        validation_file.write("Chromosome %d:\n" % (i+1))
        validation_file.write("\t\t\t Templates: %d:\n\n" % ch.all_templates())
        metrics = []
        metrics = validate_chromosome(templates, ch, validation_file)
    validation_file.write("<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>"
                          "<><><><><><><><><><><><><><><><><><><><><><><><><><><><><>\n")

    validation_file.close()


def validate_chromosome(templates: dict, chromosome: Chromosome, out_file, fix=None):
    number_templates_oracle = 0
    for key in templates.keys():
        number_templates_oracle = number_templates_oracle + len(templates[key])

    # if fix = true
    if fix == True:

        #let's consider only the fixed part from the templates
        for key in chromosome.templates.keys():
            for tmp in chromosome.templates[key]:
                while tmp.token.__contains__('*'):
                    tmp.token.remove('*')
                while tmp.token.__contains__('#spec#'):
                    tmp.token.remove('#spec#')
    correct = 0
    incorrect = 0
    out_file.write("\t\t\t\t\t Correct templates  \t\t\t\t\t\t\t\t\t\t\t Incorrect templates \n\n")
    for key in chromosome.templates.keys():
        # check if the key in oracle.keys()
        if key not in templates.keys():
            incorrect = incorrect + chromosome.cluster_size(key)
        else:
            for index in range(0, chromosome.cluster_size(key)):
                template = chromosome.templates[key][index]

                for i in range(template.get_length()):
                    if template.token[i] == '#spec#':
                        template.token[i] = "*"

                if is_correct(templates[key], template):
                    out_file.write("\t\t\t %r\n" %((template.to_string())))
                    correct += 1
                else:
                    incorrect += 1
                    out_file.write("\t\t\t\t\t                    \t\t\t\t\t\t\t\t %r\n" %((template.to_string())))

    out_file.write("\n\n\t\t\t Correct:   \t\t %r\n" % correct)
    out_file.write("\t\t\t Incorrect: \t\t %r\n" % incorrect)
    # compute: Precision, Recall, Accuracy and F-Measure
    precision = (correct / chromosome.all_templates())
    recall = (correct / number_templates_oracle)
    accuracy = correct / (incorrect + number_templates_oracle)
    if precision != 0 or recall != 0:
        f_measure = (2 * (precision * recall)) / (precision + recall)
    else:
        f_measure = 0
    return correct, incorrect, precision, recall, accuracy, f_measure

def is_correct(templates: List[List[str]], t: Template):

    for i, tmp in enumerate(templates):
        if t.token == templates[i]:
            return True
    return False