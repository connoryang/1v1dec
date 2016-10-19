#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\testfixtures\tests\test_logcapture.py
from __future__ import print_function
from doctest import DocTestSuite
from mock import Mock
from testfixtures import Replacer, LogCapture, compare
from unittest import TestSuite, TestCase, makeSuite
from logging import getLogger
from warnings import catch_warnings
root = getLogger()
one = getLogger('one')
two = getLogger('two')
child = getLogger('one.child')

class DemoLogCapture:

    def test_simple(self):
        pass


class TestLogCapture:

    def test_simple(self):
        pass

    def test_specific_logger(self):
        pass

    def test_multiple_loggers(self):
        pass

    def test_simple_manual_install(self):
        pass

    def test_uninstall(self):
        pass

    def test_uninstall_all(self):
        pass

    def test_two_logcaptures_on_same_logger(self):
        pass

    def test_uninstall_more_than_once(self):
        pass

    def test_with_statement(self):
        pass


class LogCaptureTests(TestCase):

    def test_remove_existing_handlers(self):
        logger = getLogger()
        original_handlers = logger.handlers
        try:
            logger.handlers = start = [object()]
            with LogCapture() as l:
                logger.info('during')
            l.check(('root', 'INFO', 'during'))
            compare(logger.handlers, start)
        finally:
            logger.handlers = original_handlers

    def test_atexit(self):
        from mock import call
        m = Mock()
        with Replacer() as r:
            r.replace('testfixtures.LogCapture.atexit_setup', False)
            r.replace('atexit.register', m.register)
            l = LogCapture()
            expected = [call.register(l.atexit)]
            compare(expected, m.mock_calls)
            with catch_warnings(record=True) as w:
                l.atexit()
                self.assertTrue(len(w), 1)
                compare(str(w[0].message), 'LogCapture instances not uninstalled by shutdown, loggers captured:\n(None,)')
            l.uninstall()
            compare(set(), LogCapture.instances)
            l.atexit()

    def test_numeric_log_level(self):
        with LogCapture() as log:
            getLogger().log(42, 'running in the family')
        log.check(('root', 'Level 42', 'running in the family'))

    def test_enable_disabled_logger(self):
        logger = getLogger('disabled')
        logger.disabled = True
        with LogCapture('disabled') as log:
            logger.info('a log message')
        log.check(('disabled', 'INFO', 'a log message'))
        compare(logger.disabled, True)

    def test_no_propogate(self):
        logger = getLogger('child')
        compare(logger.propagate, True)
        with LogCapture() as global_log:
            with LogCapture('child', propagate=False) as child_log:
                logger.info('a log message')
                child_log.check(('child', 'INFO', 'a log message'))
        global_log.check()
        compare(logger.propagate, True)


def setUp(test):
    test.globs['log_capture'] = LogCapture()


def tearDown(test):
    test.globs['log_capture'].uninstall_all()


def test_suite():
    return TestSuite((DocTestSuite(setUp=setUp, tearDown=tearDown), makeSuite(LogCaptureTests)))
