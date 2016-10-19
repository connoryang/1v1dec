#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\testfixtures\tests\test_components.py
from nose.plugins.skip import SkipTest
try:
    from testfixtures.components import TestComponents
except ImportError:
    raise SkipTest('zope.component is not available')

from mock import Mock, call
from testfixtures import Replacer, compare
from unittest import TestCase
from warnings import catch_warnings

class ComponentsTests(TestCase):

    def test_atexit(self):
        m = Mock()
        with Replacer() as r:
            r.replace('atexit.register', m.register)
            c = TestComponents()
            expected = [call.register(c.atexit)]
            compare(expected, m.mock_calls)
            with catch_warnings(record=True) as w:
                c.atexit()
                self.assertTrue(len(w), 1)
                compare(str(w[0].message), 'TestComponents instances not uninstalled by shutdown!')
            c.uninstall()
            compare(expected, m.mock_calls)
            c.atexit()
            compare(expected, m.mock_calls)
