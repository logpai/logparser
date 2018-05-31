import unittest

from definitions import ROOT_DIR
from main.org.core.chromosome.chromosome import *
from main.org.core.utility.Chromosome_Generator import ChromosomeGenerator


class Test(unittest.TestCase):

    def test_constructor(self):
        chromosome = Chromosome({})
        self.assertTrue(type(chromosome) is Chromosome)
        self.assertTrue(type(chromosome.templates) is dict)
        self.assertEqual(chromosome.number_of_clusters(), 0)

    def test_add(self):
        """ Testing an empty chromosome
        then the addition of one template
        """
        chromosome1 = Chromosome({})
        t1 = Template(['a', 'b', 'c'])
        t2 = Template(['a', 'b'])
        t3 = Template(['cccc', 'qqqq'])
        chromosome1.add_template(t1)
        self.assertEqual(chromosome1.number_of_clusters(), 1)
        chromosome1.add_template(t2)
        self.assertEqual(chromosome1.number_of_clusters(), 2)

        chromosome1.add_template(t3)
        self.assertEqual(chromosome1.cluster_size(2), 2)

    def test_to_string(self):
        t1 = Template(['a'])
        t2 = Template(['a', 'b'])
        t22 = Template(['word1', 'word2'])
        ch = Chromosome({1: [t1], 2: [t2, t22]})
        string = '[ a ]\n[ a b ]\n[ word1 word2 ]\n'
        self.assertEqual(ch.to_string(), string)

    def test_delete(self):
        """ Testing the deletion of a template at a given position
        """
        t1 = Template(['a'])
        t2 = Template(['a', 'b'])
        t22 = Template(['word1', 'word2'])
        ch = Chromosome({1: [t1], 2: [t2, t22]})
        self.assertEqual(ch.number_of_clusters(), 2)
        self.assertEqual(ch.cluster_size(2), 2)

        ch.delete_template(t2)
        self.assertEqual(ch.cluster_size(2), 1)
        ch.delete_template(t22)
        self.assertEqual(ch.cluster_size(2), 0)

    def test_delete_no_cluster(self):
        """ Testing the insertion of a negative index to the delete_template method
        """
        t1 = Template(['a', 'b'])
        t2 = Template(['a'])
        t3 = Template(['1', '2', '3'])
        ch = Chromosome({1: [t2], 2: [t1]})

        with self.assertRaises(IndexError):
            ch.delete_template(t3)

    def test_all_templates(self):
        t1 = Template(['a'])
        t2 = Template(['a', 'b'])
        t22 = Template(['word1', 'word2'])
        ch = Chromosome({1: [t1], 2: [t2, t22]})
        self.assertEqual(ch.all_templates(), 3)

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test)
    unittest.TextTestRunner(verbosity=2).run(suite)
