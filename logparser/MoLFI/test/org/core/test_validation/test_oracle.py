import unittest

from definitions import ROOT_DIR
from main.org.core.validation.oracle import OracleTemplates


class Test(unittest.TestCase):


    def test_oracle(self):
        templates = ROOT_DIR + '/test/resources/oracle_test.txt'

        Oracle = OracleTemplates(templates)
        self.assertEqual(Oracle.messages[4][0], ['*', '*', ':', '*'])
        for msg in Oracle.messages:
            print(msg)
            print(Oracle.messages[msg])