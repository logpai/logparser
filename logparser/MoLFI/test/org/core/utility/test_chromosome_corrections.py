import unittest

from main.org.core.chromosome.chromosome import Chromosome
from main.org.core.chromosome.template import Template
from main.org.core.utility.chromosome_corrections import check_variable_parts, fix_all_star_template, \
    is_all_star_template
from main.org.core.utility.message import Message


class Test(unittest.TestCase):

    def test_check_variable_parts(self):
        # create messages
        message1 = Message(['read', 'text', 'file', 'from', 'ABC1'])
        message2 = Message(['read', 'text', 'file', 'from', 'ABC2'])
        message3 = Message(['read', 'text', 'file', 'from', 'ABC3'])
        messages = {5: [message1, message2, message3]}
        # create a chromosome
        template = Template(['read', 'text', '*', 'from', '*'])
        template.matched_lines = [0, 1, 2]
        ch = Chromosome({5:[template]})
        # code to test
        check_variable_parts(ch, messages)
        print(ch.to_string())
        self.assertEqual(ch.templates[5][0].to_string(), "[ read text file from * ]")

    def test_no_variable_parts(self):
        # create messages
        message1 = Message(['read', 'text', 'file1', 'from', 'ABC1'])
        message2 = Message(['read', 'text', 'file2', 'from', 'ABC2'])
        message3 = Message(['read', 'text', 'file3', 'from', 'ABC3'])
        messages = {5: [message1, message2, message3]}
        # create a chromosome
        template = Template(['read', 'text', '*', 'from', '*'])
        template.matched_lines = [0, 1, 2]
        ch = Chromosome({5: [template]})
        # code to test
        check_variable_parts(ch, messages)
        self.assertEqual(ch.templates[5][0].to_string(), "[ read text * from * ]")

    def test_check_variable_parts_2templates(self):
        # create messages
        message1 = Message(['read', 'text', 'file1', 'from', 'ABC1'])
        message2 = Message(['read', 'text', 'file2', 'from', 'ABC3'])
        message3 = Message(['read', 'text', 'file2', 'from', 'ABC4'])
        message4 = Message(['read', 'text', 'file', 'ABC', 'from', 'DB', '98765'])
        message5 = Message(['read', 'text', 'file', 'DSE', 'from', 'DB', '7654'])

        messages = {5: [message1, message2, message3], 7: [message4, message5]}
        # create a chromosome
        template1 = Template(['read', '*', '*', 'from', '*'])
        template1.matched_lines = [0, 1, 2]
        template2 = Template(['read', '*', 'file', '*', 'from', 'DB', '*'])
        template2.matched_lines = [0, 1]
        ch = Chromosome({5: [template1], 7: [template2]})
        # code to test
        check_variable_parts(ch, messages)
        self.assertEqual(ch.templates[5][0].to_string(), "[ read text * from * ]")
        self.assertEqual(ch.templates[7][0].to_string(), "[ read text file * from DB * ]")

    def test_is_all_star_template(self):
        template = Template(['*', '*', '*', '*'])
        self.assertTrue(is_all_star_template(template))

        template1 = Template(['*', 'message', '*', '*'])
        chromosome = Chromosome({4: [template1]})
        self.assertFalse(is_all_star_template(chromosome.templates[4][0]))

    def test_fix_all_star_template(self):
        message1 = Message(['message', 'sent', 'A1'])
        message2 = Message(['message', 'sent', 'A2'])
        message3 = Message(['message', 'sent', 'A2', 'from', ':', 'B1'])
        message4 = Message(['message', 'sent', 'A2', 'from', ':', 'B2'])
        messages = {3: [message1, message2], 6: [message3, message4]}

        template = Template(['*', '*', '*', '*', '*', '*' ])
        template.matched_lines = [0, 1]
        ch = Chromosome({6:[template]})
        fix_all_star_template(ch, 6, 0, messages)
        self.assertFalse(is_all_star_template(ch.templates[6][0]))

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test)
    unittest.TextTestRunner(verbosity=2).run(suite)
