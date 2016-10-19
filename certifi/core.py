#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\certifi\core.py
import os
import warnings
try:
    from blue import pyos, paths
except ImportError:
    pyos = None
    paths = None

class DeprecatedBundleWarning(DeprecationWarning):
    pass


def where():
    return old_where()


def get_root():
    root = os.path.split(__file__)[0]
    if pyos:
        if pyos.packaged:
            root = paths.ResolvePath(u'bin:/') + 'certifi/'
    return root


def new_where():
    return os.path.join(get_root(), 'cacert.pem')


def old_where():
    warnings.warn('The weak security bundle is being deprecated.', DeprecatedBundleWarning)
    return os.path.join(get_root(), 'weak.pem')


if __name__ == '__main__':
    print where()
