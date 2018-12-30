from typing import List
from ..chromosome.chromosome import Chromosome

""" Remove cloned chromosomes: having same templates
    Remove templates that are equal or a subset of another templates.
"""


def remove_clones(chromosomes: List[Chromosome]):
    hashs = []
    for ch in chromosomes:
        hashs.append(hash(ch.to_string()))

    unique = []
    indexes = []
    for index, x in enumerate(hashs):
        if x not in unique:
            unique.append(x)
        else:
            indexes.append(index)
    for i in reversed(indexes):
        chromosomes.pop(i)
    return chromosomes
