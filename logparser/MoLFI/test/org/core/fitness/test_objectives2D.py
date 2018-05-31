import unittest
from definitions import ROOT_DIR
from main.org.core.fitness.objectives2D import Objective2D
from main.org.core.utility.Chromosome_Generator import *


class Test(unittest.TestCase):

    def test_constructor(self):
        logfile = ROOT_DIR + '/test/resources/File.log'
        chrom_gen = ChromosomeGenerator(logfile, 0, '\n', [])
        obj2_d = Objective2D(chrom_gen)
        self.assertEqual(len(obj2_d.get_messages()), 15)

    def test_zero_frequency(self):
        # create a chromosome with only one template with maximum specificity but that
        # does not match any message
        chromosome = Chromosome({})
        template = ["A", "b", "c"]
        t = Template(template)
        chromosome.add_template(t)
        # let's read the messages
        logfile = ROOT_DIR + '/test/resources/File.log'
        chrom_gen = ChromosomeGenerator(logfile, 0, '\n', [])
        obj2_d = Objective2D(chrom_gen)
        # assertion section
        self.assertEqual(obj2_d.compute_objective(chromosome), [1.0, 0])

    def test_star_template(self):
        logfile = ROOT_DIR + '/test/resources/File.log'
        chrom_gen = ChromosomeGenerator(logfile, 0, '\n', [])

        t = Template(["*", "*", "*"])
        compute_matched_lines(chrom_gen.messages, t)
        chromosome = Chromosome({})
        chromosome.add_template(t)

        obj = Objective2D(chrom_gen)
        self.assertEqual(obj.compute_objective(chromosome), [0, 0])

    def test_compute_objective(self):
        logfile = ROOT_DIR + '/test/resources/File.log'
        chrom_gen = ChromosomeGenerator(logfile, 0, '\n', ["'[\w\d\$\-:,\./_ ><\|]*'"])

        template1 = ["Message", "sent", "by", "*", ",", "at", "port", "*"]
        template2 = ["generating", "reading", "files"]
        t1 = Template(template1)
        t2 = Template(template2)
        ch = Chromosome({})
        ch.add_template(t1)
        ch.add_template(t2)
        # update matched info
        compute_matched_lines(chrom_gen.messages, t1)
        print(t1.matched_lines)
        compute_matched_lines(chrom_gen.messages, t2)
        print(t2.matched_lines)
        ch.coverage = 9.0 / 15
        obj = Objective2D(chrom_gen)
        scores = obj.compute_objective(ch)
        self.assertEqual(scores[0], (((6/8)+1)/2))
        self.assertEqual(scores[1], (8/7)/2)

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test)
    unittest.TextTestRunner(verbosity=2).run(suite)
