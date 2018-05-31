import unittest
from main.org.core.chromosome.chromosome import *
from main.org.core.operators.crossover import *


class Test(unittest.TestCase):

    def test_cx_chrom_percentage(self):
        t11 = Template(['start', '*', 'conf'])
        t12 = Template(["start", "send", "message", "from", "*"])
        ch1 = Chromosome({3: [t11], 5: [t12]})

        t21 = Template(['*', '*', 'conf'])
        t22 = Template(['Server', 'port', '*', 'at', 'vvvv'])
        ch2 = Chromosome({3: [t21], 5: [t22]})

        offsp1, offsp2 = multipoint_cx(ch1, ch2)

        for key in offsp1.templates.keys():
            self.assertTrue(offsp1.templates[key] == ch1.templates[key] or ch2.templates[key])
        for key in offsp2.templates.keys():
            self.assertTrue(offsp2.templates[key] == ch1.templates[key] or ch2.templates[key])


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test)
    unittest.TextTestRunner(verbosity=2).run(suite)
