import unittest
from main.org.core.chromosome.template import *


class Test(unittest.TestCase):

    def test_instantiation(self):
        """ Testing the instantiation of an object of type Template
        """
        template1 = Template(['a', 'b', 'c'])
        self.assertEqual(template1.token[0], 'a')
        self.assertEqual(template1.token[1], 'b')
        self.assertEqual(template1.token[2], 'c')

    def test_get_length(self):
        t = ['START', 'read', 'configuration']
        template = Template(t)
        self.assertEqual(template.get_length(), 3)

    def test_to_string(self):
        template = Template(['File', 'data', 'stat'])
        string = template.to_string()
        self.assertEqual(string, '[ File data stat ]')

    def test_is_changed(self):
        template = Template(['open', 'file', 'server'])
        template.set_changed(False)
        self.assertFalse(template.is_changed())

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test)
    unittest.TextTestRunner(verbosity=2).run(suite)
