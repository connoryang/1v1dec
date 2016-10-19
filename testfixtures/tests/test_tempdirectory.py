#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\testfixtures\tests\test_tempdirectory.py
import os
from doctest import DocTestSuite, ELLIPSIS
from mock import Mock
from tempfile import mkdtemp
from testfixtures import TempDirectory, Replacer, ShouldRaise, compare
from unittest import TestCase, TestSuite, makeSuite
from ..compat import Unicode, PY3
from testfixtures.tests.compat import py_35_plus
from warnings import catch_warnings
from ..rmtree import rmtree
if PY3:
    some_bytes = '\xa3'.encode('utf-8')
    some_text = '\xa3'
else:
    some_bytes = '\xc2\xa3'
    some_text = '\xc2\xa3'.decode('utf-8')

class DemoTempDirectory:

    def test_return_path(self):
        pass

    def test_ignore(self):
        pass

    def test_ignore_regex(self):
        pass


class TestTempDirectory:

    def test_cleanup(self):
        pass

    def test_cleanup_all(self):
        pass

    def test_with_statement(self):
        pass

    def test_listdir_sort(self):
        pass


class TempDirectoryTests(TestCase):

    def test_write_with_slash_at_start(self):
        with TempDirectory() as d:
            with ShouldRaise(ValueError('Attempt to read or write outside the temporary Directory')):
                d.write('/some/folder', 'stuff')

    def test_makedir_with_slash_at_start(self):
        with TempDirectory() as d:
            with ShouldRaise(ValueError('Attempt to read or write outside the temporary Directory')):
                d.makedir('/some/folder')

    def test_read_with_slash_at_start(self):
        with TempDirectory() as d:
            with ShouldRaise(ValueError('Attempt to read or write outside the temporary Directory')):
                d.read('/some/folder')

    def test_listdir_with_slash_at_start(self):
        with TempDirectory() as d:
            with ShouldRaise(ValueError('Attempt to read or write outside the temporary Directory')):
                d.listdir('/some/folder')

    def test_compare_with_slash_at_start(self):
        with TempDirectory() as d:
            with ShouldRaise(ValueError('Attempt to read or write outside the temporary Directory')):
                d.compare((), path='/some/folder')

    def test_read_with_slash_at_start_ok(self):
        with TempDirectory() as d:
            path = d.write('foo', 'bar')
            compare(d.read(path), 'bar')

    def test_dont_cleanup_with_path(self):
        d = mkdtemp()
        fp = os.path.join(d, 'test')
        with open(fp, 'w') as f:
            f.write('foo')
        try:
            td = TempDirectory(path=d)
            self.assertEqual(d, td.path)
            td.cleanup()
            self.assertEqual(os.listdir(d), ['test'])
            with open(fp) as f:
                self.assertEqual(f.read(), 'foo')
        finally:
            rmtree(d)

    def test_dont_create_with_path(self):
        d = mkdtemp()
        rmtree(d)
        td = TempDirectory(path=d)
        self.assertEqual(d, td.path)
        self.failIf(os.path.exists(d))

    def test_deprecated_check(self):
        with TempDirectory() as d:
            d.write('x', '')
            d.check('x')

    def test_deprecated_check_dir(self):
        with TempDirectory() as d:
            d.write('foo/x', '')
            d.check_dir('foo', 'x')

    def test_deprecated_check_all(self):
        with TempDirectory() as d:
            d.write('a/b/c', '')
            d.check_all('', 'a/', 'a/b/', 'a/b/c')
            d.check_all('a', 'b/', 'b/c')

    def test_compare_sort(self):
        with TempDirectory() as d:
            d.write('ga', '')
            d.write('foo1', '')
            d.write('Foo2', '')
            d.write('g.o', '')
            d.compare(['Foo2',
             'foo1',
             'g.o',
             'ga'])

    def test_compare_path_tuple(self):
        with TempDirectory() as d:
            d.write('a/b/c', '')
            d.compare(path=('a', 'b'), expected=['c'])

    def test_recursive_ignore(self):
        with TempDirectory(ignore=['.svn']) as d:
            d.write('.svn/rubbish', '')
            d.write('a/.svn/rubbish', '')
            d.write('a/b/.svn', '')
            d.write('a/b/c', '')
            d.write('a/d/.svn/rubbish', '')
            d.compare(['a/',
             'a/b/',
             'a/b/c',
             'a/d/'])

    def test_files_only(self):
        with TempDirectory() as d:
            d.write('a/b/c', '')
            d.compare(['a/b/c'], files_only=True)

    def test_path(self):
        with TempDirectory() as d:
            expected1 = d.makedir('foo')
            expected2 = d.write('baz/bob', '')
            expected3 = d.getpath('a/b/c')
            actual1 = d.getpath('foo')
            actual2 = d.getpath('baz/bob')
            actual3 = d.getpath(('a', 'b', 'c'))
        self.assertEqual(expected1, actual1)
        self.assertEqual(expected2, actual2)
        self.assertEqual(expected3, actual3)

    def test_atexit(self):
        from mock import call
        m = Mock()
        with Replacer() as r:
            r.replace('testfixtures.TempDirectory.atexit_setup', False)
            r.replace('atexit.register', m.register)
            d = TempDirectory()
            expected = [call.register(d.atexit)]
            compare(expected, m.mock_calls)
            with catch_warnings(record=True) as w:
                d.atexit()
                self.assertTrue(len(w), 1)
                compare(str(w[0].message), 'TempDirectory instances not cleaned up by shutdown:\n' + d.path)
            d.cleanup()
            compare(set(), TempDirectory.instances)
            d.atexit()

    def test_read_decode(self):
        with TempDirectory() as d:
            with open(os.path.join(d.path, 'test.file'), 'wb') as f:
                f.write('\xc2\xa3')
            compare(d.read('test.file', 'utf8'), some_text)

    def test_read_no_decode(self):
        with TempDirectory() as d:
            with open(os.path.join(d.path, 'test.file'), 'wb') as f:
                f.write('\xc2\xa3')
            compare(d.read('test.file'), '\xc2\xa3')

    def test_write_bytes(self):
        with TempDirectory() as d:
            d.write('test.file', '\xc2\xa3')
            with open(os.path.join(d.path, 'test.file'), 'rb') as f:
                compare(f.read(), '\xc2\xa3')

    def test_write_unicode(self):
        with TempDirectory() as d:
            d.write('test.file', some_text, 'utf8')
            with open(os.path.join(d.path, 'test.file'), 'rb') as f:
                compare(f.read(), '\xc2\xa3')

    def test_write_unicode_bad(self):
        if py_35_plus:
            expected = TypeError("a bytes-like object is required, not 'str'")
        elif PY3:
            expected = TypeError("'str' does not support the buffer interface")
        else:
            expected = UnicodeDecodeError('ascii', '\xa3', 0, 1, 'ordinal not in range(128)')
        with TempDirectory() as d:
            with ShouldRaise(expected):
                d.write('test.file', Unicode('\xa3'))

    def test_just_empty_non_recursive(self):
        with TempDirectory() as d:
            d.makedir('foo/bar')
            d.makedir('foo/baz')
            d.compare(path='foo', expected=['bar', 'baz'], recursive=False)

    def test_just_empty_dirs(self):
        with TempDirectory() as d:
            d.makedir('foo/bar')
            d.makedir('foo/baz')
            d.compare(['foo/', 'foo/bar/', 'foo/baz/'])

    def test_symlink(self):
        with TempDirectory() as d:
            d.write('foo/bar.txt', 'x')
            os.symlink(d.getpath('foo'), d.getpath('baz'))
            d.compare(['baz/', 'foo/', 'foo/bar.txt'])

    def test_follow_symlinks(self):
        with TempDirectory() as d:
            d.write('foo/bar.txt', 'x')
            os.symlink(d.getpath('foo'), d.getpath('baz'))
            d.compare(['baz/',
             'baz/bar.txt',
             'foo/',
             'foo/bar.txt'], followlinks=True)


def setUp(test):
    test.globs['temp_dir'] = TempDirectory()


def tearDown(test):
    TempDirectory.cleanup_all()


def test_suite():
    return TestSuite((DocTestSuite(setUp=setUp, tearDown=tearDown, optionflags=ELLIPSIS), makeSuite(TempDirectoryTests)))
