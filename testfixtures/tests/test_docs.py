#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\testfixtures\tests\test_docs.py
from doctest import REPORT_NDIFF, ELLIPSIS
from glob import glob
from manuel import doctest, capture
from manuel.testing import TestSuite
from nose.plugins.skip import SkipTest
from os.path import dirname, join, pardir
from . import compat
tests = glob(join(join(dirname(__file__), pardir, pardir), 'docs', '*.txt'))
if not tests:
    raise SkipTest('No docs found to test')

def test_suite():
    m = doctest.Manuel(optionflags=REPORT_NDIFF | ELLIPSIS, checker=compat.DocTestChecker())
    m += compat.Manuel()
    m += capture.Manuel()
    return TestSuite(m, *tests)
