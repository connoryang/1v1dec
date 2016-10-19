#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\testfixtures\tests\test_replacer.py
from doctest import DocTestSuite, REPORT_NDIFF, ELLIPSIS
from testfixtures import Replacer
from unittest import TestSuite

class TestReplacer:

    def test_function(self):
        pass

    def test_class(self):
        pass

    def test_method(self):
        pass

    def test_class_method(self):
        pass

    def test_multiple_replace(self):
        pass

    def test_gotcha(self):
        pass

    def test_remove_called_twice(self):
        pass

    def test_with_statement(self):
        pass

    def test_not_there(self):
        pass


def test_suite():
    return DocTestSuite(optionflags=REPORT_NDIFF | ELLIPSIS)
