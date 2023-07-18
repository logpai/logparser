import random
from ..chromosome.chromosome import Chromosome


def multipoint_cx(ch1: Chromosome, ch2: Chromosome):
    """ apply crossover on two Chromosomes at a randomly selected crossover point
    :param ch1: first Chromosome
    :param ch2: second Chromosome
    :return: the two modified chromosomes
    """
    # select a random key
    for key in ch1.templates.keys():
        if random.random() <= 0.5:
            cluster_from1 = ch1.templates[key][:]
            cluster_from2 = ch2.templates[key][:]

            ch1.templates[key] = cluster_from2
            ch2.templates[key] = cluster_from1
    return ch1, ch2
