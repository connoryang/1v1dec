#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\testfixtures\tests\test_tempdir.py
import os
from mock import Mock
from tempfile import mkdtemp
from testfixtures import Replacer, ShouldRaise, TempDirectory, compare, tempdir
from unittest import TestCase
from ..rmtree import rmtree

class TestTempDir(TestCase):

    @tempdir()
    def test_simple(self, d):
        d.write('something', 'stuff')
        d.write('.svn', 'stuff')
        d.compare(('.svn', 'something'))

    @tempdir()
    def test_subdirs(self, d):
        subdir = ['some', 'thing']
        d.write(subdir + ['something'], 'stuff')
        d.write(subdir + ['.svn'], 'stuff')
        d.compare(path=subdir, expected=('.svn', 'something'))

    @tempdir()
    def test_not_same(self, d):
        d.write('something', 'stuff')
        with ShouldRaise(AssertionError("sequence not as expected:\n\nsame:\n()\n\nexpected:\n('.svn', 'something')\n\nactual:\n('something',)")):
            d.compare(['.svn', 'something'])

    @tempdir(ignore=('.svn',))
    def test_ignore(self, d):
        d.write('something', 'stuff')
        d.write('.svn', 'stuff')
        d.compare(['something'])

    def test_cleanup_properly(self):
        r = Replacer()
        try:
            m = Mock()
            d = mkdtemp()
            m.return_value = d
            r.replace('testfixtures.tempdirectory.mkdtemp', m)
            self.failUnless(os.path.exists(d))
            self.assertFalse(m.called)

            @tempdir()
            def test_method(d):
                d.write('something', 'stuff')
                d.compare(['something'])

            self.assertFalse(m.called)
            compare(os.listdir(d), [])
            test_method()
            self.assertTrue(m.called)
            self.failIf(os.path.exists(d))
        finally:
            r.restore()
            if os.path.exists(d):
                rmtree(d)

    @tempdir()
    def test_cleanup_test_okay_with_deleted_dir(self, d):
        rmtree(d.path)

    @tempdir()
    def test_decorator_returns_tempdirectory(self, d):
        self.failUnless(isinstance(d, TempDirectory))

    def test_dont_create_or_cleanup_with_path(self):
        with Replacer() as r:
            m = Mock()
            r.replace('testfixtures.tempdirectory.mkdtemp', m)
            r.replace('testfixtures.tempdirectory.rmtree', m)

            @tempdir(path='foo')
            def test_method(d):
                compare(d.path, 'foo')

            test_method()
            self.assertFalse(m.called)
