import unittest
from definitions import ROOT_DIR
from main.org.core.operators.mutation import *


class Test(unittest.TestCase):
    def test_constructor(self):
        logfile = ROOT_DIR + '/test/resources/File.log'
        chrom_gen = ChromosomeGenerator(logfile, 0, '\n', [])
        chrom_mutator = ChromosomeMutator(chrom_gen)

        self.assertEqual(len(chrom_mutator.chGenerator.messages.keys()), 4)

    def test_change_template_one_template(self):
        logfile = ROOT_DIR + '/test/resources/File.log'
        chrom_gen = ChromosomeGenerator(logfile, 0, '\n', ["'[\w\d\$\-:,\./_ ><\|]*'"])
        chrom_mutator = ChromosomeMutator(chrom_gen)
        t = chrom_mutator.chGenerator.generate_template_from_line(8, 0)
        chromosome = Chromosome({8: [t]})
        chrom_mutator.change_template(chromosome, 8, 0)

        self.assertEqual(chromosome.templates[8][0].token[4], ",")
        self.assertEqual(chromosome.templates[8][0].token[3], "#spec#")
        for index in chromosome.templates[8][0].matched_lines:
            for i, word in enumerate(chromosome.templates[8][0].token):
                self.assertTrue(word == chrom_mutator.chGenerator.messages[8][index].words[i]
                                or word in {"*", "#spec#"})

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test)
    unittest.TextTestRunner(verbosity=2).run(suite)
