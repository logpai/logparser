import unittest

import time

from main.org.core.chromosome.chromosome import Chromosome
from main.org.core.chromosome.template import Template
from main.org.core.utility.match_utility import *
from main.org.core.utility.message import Message


class Test(unittest.TestCase):

    def test_match(self):
        message = Message(['AAA', 'BBB', 'CCC', 'DDD:', 'xyz.txt'])
        template = Template(['AAA', 'BBB', 'CCC', 'DDD:', '*'])

        is_matching = match(message, template)
        self.assertTrue(is_matching)

    def test_no_match1(self):
        message = Message(['AAA', 'BBB', 'CCC', 'DDD:', 'xyz.txt'])
        template = Template(['read', 'config', 'File'])

        is_matching = match(message, template)
        self.assertFalse(is_matching)

    def test_no_match2(self):
        message = Message(['AAA', 'BBB', 'EEE', 'DDD:', 'xyz.txt'])
        template = Template(['AAA', 'BBB', 'CCC', 'DDD:', '*'])

        is_matching = match(message, template)
        self.assertFalse(is_matching)

    def test_compute_matched_lines(self):
        messages_dict = {1:[Message(['configuration']), Message(['Data']), Message(['Object'])],
                         2:[Message(['configuration', 'file']), Message(['context', 'folder']), Message(['Close', 'file'])],
                         4:[Message(['AAA', 'Found', 'context', 'configuration'])]}

        template = Template(['context', '*'])
        compute_matched_lines(messages_dict, template)
        self.assertTrue(template.matched_lines, [1])

    def test_template_match(self):
        t1 = Template(['read', 'text', 'file', 'ABC', 'from', 'DB', 'ZZZ'])
        t2 = Template(['read', 'text', 'file', '*', 'from', 'DB', '*'])

        is_subset = template_match(t1, t2)
        self.assertTrue(is_subset)

    def test_template_no_match(self):
        t1 = Template(['read', 'text', 'file', 'EFG', 'from', 'DB', '*'])
        t2 = Template(['read', 'text', 'file', 'ABC', 'from', 'DB', 'ZZZ'])

        is_subset = template_match(t1, t2)
        self.assertFalse(is_subset)

    def test_derive_template(self):
        t1 = Template(['configuration', 'file', '*'])
        t1.matched_lines = [0, 1, 2, 3, 4, 5]
        t2 = Template(['configuration', 'file', 'f1'])
        t2.matched_lines = [1]
        t3 = Template(['configuration', 'file', '*'])
        t3.matched_lines= [0, 1, 2, 3, 4, 5]
        t4 = Template(['configuration', 'file', 'f3'])
        t4.matched_lines = [4]
        t5 = Template(['configuration', 'file', 'f5'])
        t5.matched_lines = [5]
        t6 = Template(['configuration', 'file', 'f6'])
        t6.matched_lines = [3]
        partition = [t1, t2, t3, t4, t5, t6]
        to_remove_sub = set()
        derive_sub_template(partition, to_remove_sub)
        self.assertEqual(len(to_remove_sub),5)
        to_remove_super = set()
        derive_super_template(partition, to_remove_super)
        self.assertEqual(len(to_remove_super), 2)

    def test_remove_sub_templates(self):
        t1 = Template(['read', 'text', 'file', 'ABC', 'from', 'DB', 'ZZZ'])
        t1.matched_lines = [3]
        t2 = Template(['read', 'text', 'file', '*', 'from', 'DB', '*'])
        t2.matched_lines = [0, 1, 3]
        t3 = Template(['read', 'text', 'file', 'AEF', 'from', 'DB', 'YYY'])
        t3.matched_lines = [0]
        t4 = Template(['read', 'text', 'file', '*', 'from', 'DB', '*'])
        t4.matched_lines = [0, 1]

        t5 = Template(['file', 'configuration', '*'])
        t5.matched_lines = [2,3,4]
        t6 = Template(['file', 'configuration', 'A'])
        t6.matched_lines = [2]

        ch = Chromosome({7: [t1, t2, t3, t4, t3, t4], 3: [t5, t6]})
        remove_sub_templates(ch, 7)
        self.assertEqual(ch.cluster_size(7), 1)
        self.assertEqual(ch.templates[7][0].token, ['read', 'text', 'file', '*', 'from', 'DB', '*'])
        remove_sub_templates(ch, 3)
        self.assertEqual(ch.cluster_size(3), 1)

    def test_remove_super_templates(self):
        t1 = Template(['read', 'text', 'file', 'ABC', 'from', 'DB', '*'])
        t1.matched_lines = [3]
        t2 = Template(['read', 'text', 'file', '*', 'from', 'DB', '*'])
        t2.matched_lines = [0, 1]
        t3 = Template(['read', 'text', 'file', '*', 'from', 'DB', '2323232'])
        t3.matched_lines = [0]
        t4 = Template(['read', 'text', 'file', '*', 'from', 'DB', '*'])
        t4.matched_lines = [0, 1]

        t5 = Template(['file', 'configuration', '*'])
        t5.matched_lines = [2, 3, 4]
        t6 = Template(['file', 'configuration', 'A'])
        t6.matched_lines = [2]

        ch = Chromosome({7: [t1, t2, t3, t4, t3, t4], 3: [t5, t6]})
        remove_super_templates(ch, 7)
        self.assertEqual(ch.cluster_size(7), 2)
        remove_super_templates(ch, 3)
        self.assertEqual(ch.cluster_size(3), 1)
        self.assertEqual(ch.templates[3][0].token, ['file', 'configuration', 'A'])

    def test_remove_all_stars_template(self):
        template0 = Template(['*', '*', '2000'])
        template1 = Template(['file', 'config', '1000'])
        template2 = Template(['*', '*', '*'])
        chromosome = Chromosome({3:[template0, template1, template2]})
        remove_all_stars_template(chromosome, 3)
        self.assertEqual(chromosome.to_string(), "[ * * 2000 ]\n[ file config 1000 ]\n")


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test)
    unittest.TextTestRunner(verbosity=2).run(suite)
