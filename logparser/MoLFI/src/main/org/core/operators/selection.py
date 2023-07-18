import random


def apply_tournament_selection(individuals, tot_rounds: int):
    """Tournament selection based on dominance (D) between two individuals, if
    the two individuals do not interdominate the selection is made
    based on crowding distance (CD). The *individuals* sequence length has to
    be a multiple of 4. Starting from the beginning of the selected
    individuals, two consecutive individuals will be different (assuming all
    individuals in the input list are unique). 

    This selection requires the individuals to have a :attr:`crowding_dist`
    attribute, which can be set by the :func:`assignCrowdingDist` function.

    :param individuals: A list of individuals to select from.
    :param tot_rounds: number of rounds in the tournament.
    :returns: One selected individuals.
    """
    winner = random.choice(individuals)

    for i in range(0, tot_rounds-1):
        ind = random.choice(individuals)

        if ind.fitness.dominates(winner.fitness):
            winner = ind
        elif not winner.fitness.dominates(ind.fitness):
            if ind.fitness.crowding_dist < winner.fitness.crowding_dist:
                winner = ind

    return winner
