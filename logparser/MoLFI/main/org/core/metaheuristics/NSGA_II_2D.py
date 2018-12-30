import time
import random

from deap import base
from deap import creator
from deap import tools
from deap.tools import sortNondominated

# from definitions import ROOT_DIR
# import matplotlib.pyplot as plt
import numpy
from ..fitness.objectives2D import Objective2D
from ..operators.selection import apply_tournament_selection
from ..operators.crossover import multipoint_cx
from ..operators.mutation_100cov import ChromosomeMutator100cov
from ..post_process.post_process_chromosomes import *
from ..utility.Chromosome_Generator import ChromosomeGenerator
from ..utility.chromosome_corrections import check_variable_parts


def main(chrom_gen):

    toolbox = base.Toolbox()

    class ClassContainer:
        def __init__(self, ch: Chromosome):
            """ A container that generates a Chromosome object
            """
            self.chromosome = ch

    creator.create("FitnessMulti", base.Fitness, weights=(1.0, 1.0))
    creator.create("Individual", ClassContainer, fitness=creator.FitnessMulti)

    toolbox.register("attr_float", chrom_gen.generate_100cov_chromosome)
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.attr_float)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    object2D = Objective2D(chrom_gen)

    def evaluate_individual(indiv):
        return object2D.compute_objective(indiv.chromosome)

    toolbox.register("evaluate", evaluate_individual)
    toolbox.register("select", tools.selNSGA2)

    mutation = ChromosomeMutator100cov(chrom_gen)
    toolbox.register("mutate", mutation.apply_mutation)
    toolbox.register("mate", multipoint_cx)

    MU = 20  # population size (should be a multiple of 4 because we are using the selTournamentDCD)
    NGEN = 200  # number of generations
    CXPB = 0.7
    online_plot = False  # decide whether to show a dynamic plot with Pareto front across generations or not

    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("max", numpy.max, axis=0)
    stats.register("max", numpy.max, axis=0)

    logbook = tools.Logbook()
    logbook.header = "gen", "pop", "max"

    pop = toolbox.population(n=MU)

    invalid_ind = [ind for ind in pop if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)

    for ind1, fit in zip(invalid_ind, fitnesses):
        ind1.fitness.values = fit

    # This is just to assign the crowding distance to the individuals
    # no actual selection is done
    pop = toolbox.select(pop, len(pop))

    record = stats.compile(pop)
    logbook.record(gen=0, pop=len(invalid_ind), **record)
    # print('Results: \n ============================================================= \n ', logbook.stream)

    ################################################################################################################
    # Begin the generational process
    for gen in range(1, NGEN):
        # Vary the population
        offspring_pop = list()
        while len(offspring_pop) < len(pop):
            # select parent 1
            parent1 = apply_tournament_selection(pop, 2)
            offspring1 = toolbox.clone(parent1)
            # select parent 2
            parent2 = apply_tournament_selection(pop, 2)
            offspring2 = toolbox.clone(parent2)

            # apply crossover
            r = random.random()
            if r <= CXPB:
                toolbox.mate(offspring1.chromosome, offspring2.chromosome)

            # apply mutation
            toolbox.mutate(offspring1.chromosome)
            toolbox.mutate(offspring2.chromosome)

            # calculate objectives scores
            offspring1.fitness.values = toolbox.evaluate(offspring1)
            offspring2.fitness.values = toolbox.evaluate(offspring2)

            # add offsprings to the new population
            offspring_pop.append(offspring1)
            offspring_pop.append(offspring2)

        # Select the next generation population
        pop = toolbox.select(pop + offspring_pop, MU)

        # if online_plot:
        #     frontier = numpy.array([ind.fitness.values for ind in pop])
        #     plt.close()
        #     plt.scatter(frontier[:, 0], frontier[:, 1], c="r", marker='o',edgecolors='k')
        #     plt.xlabel('Specificity')
        #     plt.ylabel('Frequency')
        #     plt.pause(0.01)

        record = stats.compile(pop)
        logbook.record(gen=gen, pop=len(invalid_ind), **record)

        # print(logbook.stream)

    for ind in pop:
        # apply corrections
        check_variable_parts(ind.chromosome, chrom_gen.messages)

    # 1. Let's first extract only the Pareto front
    fitnesses = toolbox.map(toolbox.evaluate, pop)
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit
    ParetoSet = sortNondominated(pop, len(pop), first_front_only=True)
    pop = ParetoSet[0]

    front = numpy.array([ind.fitness.values for ind in pop])

    # get the max value for each objective
    # Specificity
    max_spec = 0.0
    min_spec = 1.0
    max_freq = 0.0
    min_freq = 1.0
    for individual in pop:
        if individual.fitness.values[0] > max_spec:
            max_spec = individual.fitness.values[0]
        if individual.fitness.values[0] < min_spec:
            min_spec = individual.fitness.values[0]
        if individual.fitness.values[1] > max_freq:
            max_freq = individual.fitness.values[1]
        if individual.fitness.values[1] < min_freq:
            min_freq = individual.fitness.values[1]

    #############################
    # search for the mid point
    # between the corner points
    mid_x = (max_spec + min_spec) / 2
    mid_y = (max_freq + min_freq) / 2
    mid = (mid_x, mid_y)
    # get the closest point to the mid_pt
    distance = []
    for opt in front:
        dist = numpy.sqrt(((mid[0] - opt[0]) ** 2) + ((mid[1] - opt[1]) ** 2))
        distance.append(dist)

    mid_pt = front[distance.index(min(distance))]
    # print('Middle point = ', mid_pt)

    #############################
    # search for the Knee point, the closets point ot the max objectives

    min_dist = 100.0
    for opt1 in front:
        dist = numpy.sqrt(((max_spec - opt1[0]) ** 2) + ((max_freq - opt1[1]) ** 2))
        if dist < min_dist:
            min_dist = dist
            knee_pt = opt1
    # print('Knee point = ', knee_pt)

    min_dist = 100.0
    for opt1 in front:
        dist = numpy.sqrt(((1.0 - opt1[0]) ** 2) + ((1.0 - opt1[1]) ** 2))
        if dist < min_dist:
            min_dist = dist
            knee_pt1 = opt1
    # print('Knee point11 = ', knee_pt1)

    for ch in pop:
        if ch.fitness.values[0] == knee_pt[0] and ch.fitness.values[1] == knee_pt[1]:
            knee_solution = ch
            break

    for ch in pop:
        if ch.fitness.values[0] == knee_pt1[0] and ch.fitness.values[1] == knee_pt1[1]:
            knee_solution1 = ch
            break

    for ch in pop:
        if ch.fitness.values[0] == mid_pt[0] and ch.fitness.values[1] == mid_pt[1]:
            mid_solution = ch
            break

    ## plot the pareto front
    # plt.scatter(front[:,0], front[:,1], c="r", marker='o')
    # # print the mid_pt
    # plt.scatter(mid_pt[0], mid_pt[1], c='b', marker='*')
    # plt.scatter(mid_x, mid_y, c='black', marker='*')
    # # print the knee point
    # plt.scatter(max_spec, max_freq, c='black', marker='^')
    # plt.scatter(knee_pt[0], knee_pt[1], c='g', marker='^')
    # # print the knee11 point
    # plt.scatter(knee_pt1[0], knee_pt1[1], c='y', marker='+')
    #
    # plt.xlabel('Specificity')
    # plt.ylabel('Frequency')
    #
    # plt.show()

    # pareto is a dict with three elements
    # key : name of the point from the pareto front
    # value: chromosome
    pareto = {'Knee_Solution': knee_solution.chromosome,
              'Knee_Solution_1': knee_solution1.chromosome,
              'Mid_Solution': mid_solution.chromosome
              }

    #return the three best points
    #       the logbook to see the variation of specificity and frequency values
    #       the execution time
    #       the Non dominated points from the last population
    # return pareto, logbook, execution_time, pop
    return pareto  #, logbook, pop
#
# if __name__ == "__main__":
#     log_file = ROOT_DIR + "/run_experiments/datasets/Proprietary/2K_log/2K_log_messages.log"
#     templates_file = ROOT_DIR + "/run_experiments/datasets/Proprietary/2K_log/2K_Oracle.txt"
#     chrom_gen = ChromosomeGenerator(log_file, 3, '\t')
#
#     pareto, logbook, execution_time = main(chrom_gen)
#
#     for i in pareto.keys():
#         print(pareto[i].chromosome.to_string())

    ############################
    # plt.scatter(front[:,0], front[:,1], c="r", marker='o')
    # # print the mid_pt
    # plt.scatter(mid_pt[0], mid_pt[1], c='b', marker='*')
    # plt.scatter(mid_x, mid_y, c='black', marker='*')
    # # print the knee point
    # plt.scatter(max_spec, max_freq, c='black', marker='^')
    # plt.scatter(knee_pt[0], knee_pt[1], c='g', marker='^')
    # # print the knee11 point
    # plt.scatter(knee_pt1[0], knee_pt1[1], c='y', marker='+')
    # plt.axis("tight")
    #
    # plt.xlabel('Specificity')
    # plt.ylabel('Frequency')
    #
    # plt.show()
