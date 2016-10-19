#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\testfixtures\tests\test_diff.py
from unittest import TestCase, TestSuite, makeSuite
from testfixtures import diff

class TestDiff(TestCase):

    def test_example(self):
        actual = diff('\n        line1\n        line2\n        line3\n        ', '\n        line1\n        line changed\n        line3\n        ')
        expected = '--- first\n+++ second\n@@ -1,5 +1,5 @@\n\n         line1\n-        line2\n+        line changed\n         line3\n         '
        self.assertEqual([ line.strip() for line in expected.split('\n') ], [ line.strip() for line in actual.split('\n') ], '\n%r\n!=\n%r' % (expected, actual))

    def test_no_newlines(self):
        actual = diff('x', 'y')
        try:
            expected = '@@ -1 +1 @@\n-x\n+y'
            self.assertEqual(expected, actual, '\n%r\n!=\n%r' % (expected, actual))
        except AssertionError:
            expected = '--- first\n+++ second\n@@ -1 +1 @@\n-x\n+y'
            self.assertEqual(expected, actual, '\n%r\n!=\n%r' % (expected, actual))
