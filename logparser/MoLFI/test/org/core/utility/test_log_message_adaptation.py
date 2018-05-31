import re
import unittest

from numpy.core.defchararray import startswith

from main.org.core.utility.log_message_adaptation import adapt_log_message


class Test(unittest.TestCase):


    def test_adapt_log_messages(self):
        """ detecting trivial values
        """
        line1 = "read file (ABC1/sder3/er34.txt)"
        line2 = "A start server id: {{}} from: <at ' /path/to/file'>"
        line3 = "Open folder config, at (4), id(9) to file <file id <fct> at 12345 , number 9834>"
        line4 = "Server stop 'Server-AB1'"
        line5 = "Server stop 'ID-123','SERVER-1'"
        line6 = "Server stop /file/onffile.cfg"
        line7 = "Method AB starts - open parameter file: </path/to/param-file id from 123454 >, < >"
        line8 = "Method BC end: 45:6:7 state = 11-22-333 and .xml"

        new_msg1 = adapt_log_message(line1)
        self.assertEqual(new_msg1.words, ['read', 'file', '(', '#spec#', ')'])
        new_msg2 = adapt_log_message(line2)
        self.assertEqual(new_msg2.words, ['A', 'start', 'server', 'id', ':', '{', '{', '}', '}', 'from', ':', '<', 'at', "'", '#spec#', "'", '>'])
        new_msg3 = adapt_log_message(line3)
        self.assertEqual(new_msg3.words, ['Open', 'folder', 'config', ',', 'at', '(', '4',')', ',', 'id', '(', '9',')', 'to', 'file', '<', 'file', 'id', '<', 'fct', '>','at', '#spec#', ',', 'number', '9834', '>'])
        new_msg4 = adapt_log_message(line4)
        self.assertEqual(new_msg4.words, ['Server', 'stop', "'", 'Server-AB1', "'"])
        new_msg5 = adapt_log_message(line5)
        self.assertEqual(new_msg5.words, ['Server', 'stop', "'", 'ID-123', "'", ',', "'", 'SERVER-1', "'"])
        new_msg6 = adapt_log_message(line6)
        self.assertEqual(new_msg6.words, ['Server', 'stop',  '#spec#'])
        new_msg7 = adapt_log_message(line7)
        self.assertEqual(new_msg7.words, ['Method', 'AB', 'starts', '-', 'open', 'parameter', 'file', ':', '<', '#spec#', 'id', 'from', '#spec#', '>', ',', '<', '>'])
        new_msg8 = adapt_log_message(line8)
        self.assertEqual(new_msg8.words, ['Method', 'BC', 'end', ':', '45', ':', '6', ':', '7', 'state', '=', '#spec#', 'and', '#spec#'])

    def test_messages_with_acute_angles(self):
        regex = [
                 "< [\w\d/\. *_\|]+ >",  # text between acute angles, with no special char inside
                 "'[\w\d\$\-:,\./_ ><\|]*'",  # strings with the formats 'words', '[alphanumeric strings]'
                 '(/|\s)([0-9]+\.){3}[0-9]+([/:][0-9]+|\s)'
                 '(/*[\d\w\-_\.\#\$]*[/\.][\d\w\-_\.\#\$/*]*)+',
                 '0x([a-fA-F0-9])+',
                 '([0-9A-F]{2}[:-]){5,}([0-9A-F]{2})',
                 '(^| )(|-)\d+(|[-_/\.\d*]*)( |$)'
                 ]

        line = '<word> file "path/to/file"'
        new_msg1 = adapt_log_message(line, regex=regex)
        self.assertEqual(new_msg1.words, ['#spec#', 'file', '"', '#spec#', '"'])

        line = "<word1 word2>"
        new_msg1 = adapt_log_message(line, regex=regex)
        self.assertEqual(new_msg1.words, ['#spec#'])

        line = "<word1.word2>"
        new_msg1 = adapt_log_message(line, regex=regex)
        self.assertEqual(new_msg1.words, ['#spec#'])

        line = "<word1> <word2>"
        new_msg1 = adapt_log_message(line, regex=regex)
        self.assertEqual(new_msg1.words, ['#spec#', '#spec#'])

        line = "<word1> at <word2>"
        new_msg1 = adapt_log_message(line, regex=regex)
        self.assertEqual(new_msg1.words, ['#spec#', 'at', '#spec#'])

        line = "<word1 at 10>"
        new_msg1 = adapt_log_message(line, regex=regex)
        self.assertEqual(new_msg1.words, ['#spec#'])

    def test_messages_with_integers(self):
        line = "A sent 10"
        new_msg1 = adapt_log_message(line)
        self.assertEqual(new_msg1.words, ['A','sent','#spec#'])

        line = "10 is received"
        new_msg1 = adapt_log_message(line)
        self.assertEqual(new_msg1.words, ['#spec#', 'is', 'received'])

    def test_messages_with_memory_addresses(self):
        line = "0x0asdfertg"
        new_msg1 = adapt_log_message(line)
        self.assertEqual(new_msg1.words, ['#spec#'])

    def test_messages_with_if_addresses(self):
        line = "0.0.0.0"
        new_msg1 = adapt_log_message(line)
        self.assertEqual(new_msg1.words, ['#spec#'])

        line = "127.89.10.10"
        new_msg1 = adapt_log_message(line)
        self.assertEqual(new_msg1.words, ["#spec#"])


    def test_messages_with_paths(self):
        a = "([\d\w]*/[\d\w]*)+"
        match = re.findall(a,"aaa/aaa a/ /a")
        print(match)

        line = "folder/folder/file"
        new_msg1 = adapt_log_message(line)
        self.assertEqual(new_msg1.words, ['#spec#'])

        line = "/folder/file"
        new_msg1 = adapt_log_message(line)
        self.assertEqual(new_msg1.words, ['#spec#'])

        line = "/folder/"
        new_msg1 = adapt_log_message(line)
        self.assertEqual(new_msg1.words, ['#spec#'])

        line = "FILE log file: /path/to/log/file.log"
        new_msg1 = adapt_log_message(line)
        self.assertEqual(new_msg1.words, ['FILE', 'log', 'file', ':', '#spec#'])

    def test_messages_with_parentheses(self):
        line = "START read parameters {'param-1': 'value1223'}"
        regex = [
                 "'[\w\d\$\-:,\./_ ><\|]*'",  # strings with the formats 'words', '[alphanumeric strings]'
                 '(/|\s)([0-9]+\.){3}[0-9]+([/:][0-9]+|\s)'
                 '(/*[\d\w\-_\.\#\$]*[/\.][\d\w\-_\.\#\$/*]*)+',
                 '0x([a-fA-F0-9])+',
                 '([0-9A-F]{2}[:-]){5,}([0-9A-F]{2})',
                 '(^| )(|-)\d+(|[-_/\.\d*]*)( |$)'
                 ]
        new_msg1 = adapt_log_message(line, regex=regex)
        self.assertEqual(new_msg1.words, ['START', 'read', 'parameters', '{', '#spec#', ':', '#spec#', '}'])



if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test)
    unittest.TextTestRunner(verbosity=2).run(suite)
