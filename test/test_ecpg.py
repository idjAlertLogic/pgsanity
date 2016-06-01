import unittest

from pgsanity import ecpg

class TestEcpg(unittest.TestCase):
    def test_simple_success(self):
        text = u"EXEC SQL select a from b;"
        (success, msglist) = ecpg.check_syntax(0, text)
        self.assertTrue(success)

    def test_simple_failure(self):
        text = u"EXEC SQL garbage select a from b;"
        (success, msglist) = ecpg.check_syntax(0, text)
        self.assertFalse(success)
        self.assertEqual(['line 1: ERROR: unrecognized data type name "garbage"'], msglist)

    def test_parse_error_simple(self):
        error = '/tmp/tmpLBKZo5.pgc:1: ERROR: unrecognized data type name "garbage"'
        expected = ['line 1: ERROR: unrecognized data type name "garbage"']
        self.assertEqual(expected, ecpg.parse_error(0, error))

    def test_parse_error_comments(self):
        error = '/tmp/tmpLBKZo5.pgc:5: ERROR: syntax error at or near "//"'
        expected = ['line 5: ERROR: syntax error at or near "--"']
        self.assertEqual(expected, ecpg.parse_error(0, error))
