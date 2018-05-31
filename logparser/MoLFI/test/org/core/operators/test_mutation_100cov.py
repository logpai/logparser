import unittest

from definitions import ROOT_DIR
from main.org.core.chromosome.chromosome import Chromosome
from main.org.core.chromosome.template import Template
from main.org.core.operators.mutation_100cov import ChromosomeMutator100cov
from main.org.core.utility.Chromosome_Generator import ChromosomeGenerator


class Test(unittest.TestCase):

    def test_apply_mutation(self):
        logfile = ROOT_DIR + '/test/resources/File.log'
        chrom_gen = ChromosomeGenerator(logfile, 0, '\n', ["'[\w\d\$\-:,\./_ ><\|]*'"])
        chrom_mutator_100 = ChromosomeMutator100cov(chrom_gen)
        template = Template(['Driver', ':', '*'])
        template.matched_lines = [5]
        chromosome = Chromosome({3: [template]})
        chrom_mutator_100.apply_mutation(chromosome)

        chromosome_matched_lines = []
        for t in chromosome.templates[3]:
            for i in t.matched_lines:
                chromosome_matched_lines.append(i)
        self.assertEqual(len(set(chromosome_matched_lines)), len(chrom_gen.messages[3]))

    def test_add_template_to_reach_100cov(self):
        logfile = ROOT_DIR + '/test/resources/File.log'
        chrom_gen = ChromosomeGenerator(logfile, 0, '\n', ["'[\w\d\$\-:,\./_ ><\|]*'"])
        chrom_mutator_100 = ChromosomeMutator100cov(chrom_gen)
        template = Template(['Message', 'sent', 'by', 'EEE', ',', 'at', 'port', '1'])
        template.matched_lines = [0]
        chromosome = Chromosome({8: [template]})
        chrom_mutator_100.add_template_to_reach_100cov(chromosome, 8)
        chromosome_matched_lines = []
        for t in chromosome.templates[8]:
            for i in t.matched_lines:
                chromosome_matched_lines.append(i)

        self.assertEqual(len(set(chromosome_matched_lines)), len(chrom_gen.messages[8]))


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test)
    unittest.TextTestRunner(verbosity=2).run(suite)
