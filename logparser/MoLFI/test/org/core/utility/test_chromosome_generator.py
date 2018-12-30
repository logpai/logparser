import tempfile
import unittest

import shutil

from definitions import ROOT_DIR
from main.org.core.utility.Chromosome_Generator import *


class Test(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.logfile = self.test_dir+'/logfile.log'
        messages = ['A message B\nA message B\n'
                    'A message B\nA message B']
        file = open(self.logfile, 'w')
        file.writelines(messages)
        file.close()

    def test_load_log_message(self):
        chrom_gen = ChromosomeGenerator(self.logfile, 0, '\n', [])
        msg = Message(['Write', 'data', 'conf', 'to ', 'file', 'ABC'])
        chrom_gen.load_log_message(msg)
        self.assertEqual(len(chrom_gen.messages.keys()), 2)
        self.assertEqual(chrom_gen.messages[6][0].get_length(), 6)

    def test_constructor(self):
        logfile = ROOT_DIR + '/test/resources/File.log'
        regex = []
        chrom_gen = ChromosomeGenerator(logfile, 0, '\n', regex)
        self.assertEqual(len(chrom_gen.messages.keys()), 4)
        self.assertEqual(len(chrom_gen.messages[3]), 7)
        self.assertEqual(len(chrom_gen.messages[7]), 1)
        self.assertEqual(len(chrom_gen.messages[6]), 2)
        self.assertEqual(len(chrom_gen.messages[10]), 5)

    def test_generate_template_from_line(self):
        logfile = ROOT_DIR + '/test/resources/File.log'
        chrom_gen = ChromosomeGenerator(logfile, 0, '\n', [])
        template = chrom_gen.generate_template_from_line(3, 0)
        message = chrom_gen.messages[3][0]
        for index in range(0, message.get_length()):
            self.assertTrue(message.words[index] == template.token[index] or
                            template.token[index] in {"*", ":", "=", ",", "#spec#"})

    def test_generate_template_from_line2(self):
        logfile = ROOT_DIR + '/test/resources/File.log'
        chrom_gen = ChromosomeGenerator(logfile, 0, '\n', [])
        m = Message(["======================="])
        messages = {1:[m]}
        chrom_gen.messages = messages
        template = chrom_gen.generate_template_from_line(1, 0)
        self.assertEqual(template.token, ['======================='])

    def test_one_template_100_cov(self):
        chrom_gen = ChromosomeGenerator(self.logfile, 0, '\n', [])
        chromosome = chrom_gen.generate_100cov_chromosome()
        self.assertEqual(chromosome.number_of_clusters(), 1)
        self.assertEqual(len(chromosome.templates[3][0].matched_lines), 1)

    def test_generate_100cov_chromosome(self):
        logfile = ROOT_DIR + '/test/resources/File.log'
        chrom_gen = ChromosomeGenerator(logfile, 0, '\n', [])
        chromosome = chrom_gen.generate_100cov_chromosome()
        for key in chrom_gen.messages.keys():
            match_lines = set()
            for template in chromosome.templates[key]:
                match_lines = match_lines.union(template.matched_lines)
            self.assertEqual(len(match_lines), len(chrom_gen.messages[key]))


    def tearDown(self):
        shutil.rmtree(self.test_dir)

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test)
    unittest.TextTestRunner(verbosity=2).run(suite)
