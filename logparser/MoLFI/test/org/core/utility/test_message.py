import unittest
from main.org.core.utility.Chromosome_Generator import *


class Test(unittest.TestCase):

    def test_constructor(self):
        """ Testing the instantiation of an Message object
        """
        m = Message(['Start', 'reading', '*', 'data', '*'])
        l = m.get_length()
        self.assertEqual(l, 5)

    def test_to_string(self):
        """ Testing the conversion of a list of words to one string
        """
        m = Message(['open', 'text', '*', 'read', '*'])
        self.assertEqual(m.to_string(), 'open text * read *')

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test)
    unittest.TextTestRunner(verbosity=2).run(suite)
