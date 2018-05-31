import tempfile
import unittest
import shutil

from main.org.core.validation.oracle import OracleTemplates
from main.org.core.validation.validate_chromosomes import *


class Test(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.outfile = self.test_dir + '/outfile.log'

    def test_is_correct(self):
        templatesfile = ROOT_DIR + '/test/resources/oracle_test.txt'
        o = OracleTemplates(templatesfile)

        # create chromosome
        t0 = Template(['message', '*', 'ABC'])
        is_true = is_correct([['message', '*', 'ABC']], t0)
        self.assertTrue(is_true)

    def test_is_not_correct(self):
        templatesfile = ROOT_DIR + '/test/resources/oracle_test.txt'
        o = OracleTemplates(templatesfile)
        # create template
        t1 = Template(['A', 'B', 'C', '*',
                       'F'])
        is_true = is_correct(o.messages[5], t1)
        self.assertFalse(is_true)

    def test_validate_chrom(self):
        templatesfile = ROOT_DIR + '/test/resources/oracle_test.txt'
        o = OracleTemplates(templatesfile)
        print(o.messages)
        t = Template(['STATE', 'server', '#spec#', ',', '*', 'from', 'A'])
        ch = Chromosome({7: [t]})
        f = open(self.outfile, 'a')
        c = validate_chromosome(o.messages, ch, f)
        f.close()

    def test_starts(self):
        templatesfile = ROOT_DIR + '/test/resources/oracle_test.txt'
        o = OracleTemplates(templatesfile)
        # create chromosome
        t0 = Template(['*', '*'])
        t1 = Template(['*'])

        is_true0 = is_correct(o.messages[2], t0)
        is_true1 = is_correct(o.messages[1], t1)

        self.assertFalse(is_true0)
        self.assertFalse(is_true1)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test)
    unittest.TextTestRunner(verbosity=2).run(suite)
