#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\testfixtures\rmtree.py
import errno
import os
import shutil
import sys
import time
import warnings
if sys.platform.startswith('win'):

    def _waitfor(func, pathname, waitall = False):
        func(pathname)
        if waitall:
            dirname = pathname
        else:
            dirname, name = os.path.split(pathname)
            dirname = dirname or '.'
        timeout = 0.001
        while timeout < 1.0:
            L = os.listdir(dirname)
            if not (L if waitall else name in L):
                return
            time.sleep(timeout)
            timeout *= 2

        warnings.warn('tests may fail, delete still pending for ' + pathname, RuntimeWarning, stacklevel=4)


    def _rmtree(path):

        def _rmtree_inner(path):
            for name in os.listdir(path):
                fullname = os.path.join(path, name)
                if os.path.isdir(fullname):
                    _waitfor(_rmtree_inner, fullname, waitall=True)
                    os.rmdir(fullname)
                else:
                    os.unlink(fullname)

        _waitfor(_rmtree_inner, path, waitall=True)
        _waitfor(os.rmdir, path)


else:
    _rmtree = shutil.rmtree

def rmtree(path):
    try:
        _rmtree(path)
    except OSError as e:
        if e.errno not in (errno.ENOENT, errno.ESRCH):
            raise
