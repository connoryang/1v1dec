#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\testfixtures\tempdirectory.py
import atexit
import os
import warnings
from re import compile
from tempfile import mkdtemp
from testfixtures.comparison import compare
from testfixtures.compat import basestring
from testfixtures.utils import wrap
from .rmtree import rmtree

class TempDirectory():
    instances = set()
    atexit_setup = False
    path = None

    def __init__(self, ignore = (), create = True, path = None):
        self.ignore = []
        for regex in ignore:
            self.ignore.append(compile(regex))

        self.path = path
        self.dont_remove = bool(path)
        if create:
            self.create()

    @classmethod
    def atexit(cls):
        if cls.instances:
            warnings.warn('TempDirectory instances not cleaned up by shutdown:\n%s' % '\n'.join((i.path for i in cls.instances)))

    def create(self):
        if self.path:
            return self
        self.path = mkdtemp()
        self.instances.add(self)
        if not self.__class__.atexit_setup:
            atexit.register(self.atexit)
            self.__class__.atexit_setup = True
        return self

    def cleanup(self):
        if self.path and os.path.exists(self.path) and not self.dont_remove:
            rmtree(self.path)
            del self.path
        if self in self.instances:
            self.instances.remove(self)

    @classmethod
    def cleanup_all(cls):
        for i in tuple(cls.instances):
            i.cleanup()

    def actual(self, path = None, recursive = False, files_only = False, followlinks = False):
        path = self._join(path) if path else self.path
        result = []
        if recursive:
            for dirpath, dirnames, filenames in os.walk(path, followlinks=followlinks):
                dirpath = '/'.join(dirpath[len(path) + 1:].split(os.sep))
                if dirpath:
                    dirpath += '/'
                for dirname in dirnames:
                    if not files_only:
                        result.append(dirpath + dirname + '/')

                for name in sorted(filenames):
                    result.append(dirpath + name)

        else:
            for n in os.listdir(path):
                result.append(n)

        filtered = []
        for path in sorted(result):
            ignore = False
            for regex in self.ignore:
                if regex.search(path):
                    ignore = True
                    break

            if ignore:
                continue
            filtered.append(path)

        return filtered

    def listdir(self, path = None, recursive = False):
        actual = self.actual(path, recursive)
        if not actual:
            print 'No files or directories found.'
        for n in actual:
            print n

    def compare(self, expected, path = None, files_only = False, recursive = True, followlinks = False):
        compare(expected, actual=tuple(self.actual(path, recursive, files_only, followlinks)), recursive=False)

    def check(self, *expected):
        compare(expected, tuple(self.actual()), recursive=False)

    def check_dir(self, dir, *expected):
        compare(expected, tuple(self.actual(dir)), recursive=False)

    def check_all(self, dir, *expected):
        compare(expected, tuple(self.actual(dir, recursive=True)), recursive=False)

    def _join(self, name):
        if isinstance(name, basestring):
            name = name.split('/')
        relative = os.sep.join(name)
        if relative.startswith('/'):
            if relative.startswith(self.path):
                return relative
            raise ValueError('Attempt to read or write outside the temporary Directory')
        return os.path.join(self.path, relative)

    def makedir(self, dirpath):
        thepath = self._join(dirpath)
        os.makedirs(thepath)
        return thepath

    def write(self, filepath, data, encoding = None):
        if isinstance(filepath, basestring):
            filepath = filepath.split('/')
        if len(filepath) > 1:
            dirpath = self._join(filepath[:-1])
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)
        thepath = self._join(filepath)
        if encoding is not None:
            data = data.encode(encoding)
        with open(thepath, 'wb') as f:
            f.write(data)
        return thepath

    def getpath(self, path):
        return self._join(path)

    def read(self, filepath, encoding = None):
        with open(self._join(filepath), 'rb') as f:
            data = f.read()
        if encoding is not None:
            return data.decode(encoding)
        return data

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.cleanup()


def tempdir(*args, **kw):
    kw['create'] = False
    l = TempDirectory(*args, **kw)
    return wrap(l.create, l.cleanup)
