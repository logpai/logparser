import unittest

from main.org.core.chromosome.template import Template
from main.org.core.post_process.post_process_chromosomes import *


class Test(unittest.TestCase):

    def test_remove_clones(self):
        # 1) construct the pop of chromosomes
        t1 = Template(['generate', 'code', '*'])
        t2 = Template(['state', ':', 'close'])
        t3 = Template(['Message', 'sent', 'by', 'EEE', 'at', 'port', '*'])
        t4 = Template(['*', ':', 'run'])

        ch1 = Chromosome({3: [t1, t2], 7: [t3]})
        ch2 = Chromosome({3: [t1, t2]})
        ch3 = Chromosome({3: [t1, t4], 7: [t3]})
        ch4 = Chromosome({3: [t1, t2]})
        ch5 = Chromosome({3: [t1, t2]})

        pop = [ch1, ch2, ch3, ch4, ch5]

        unique = remove_clones(pop)
        self.assertEqual(len(unique), 3)

        templates1 = "[ generate code * ]\n[ state : close ]\n" \
                     "[ Message sent by EEE at port * ]\n"
        templates2 = "[ generate code * ]\n[ * : run ]\n" \
                     "[ Message sent by EEE at port * ]\n"
        self.assertEqual(unique[0].to_string(), templates1)
        self.assertEqual(unique[2].to_string(), templates2)

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test)
    unittest.TextTestRunner(verbosity=2).run(suite)
