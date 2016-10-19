#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\raven\versioning.py
from __future__ import absolute_import
import os.path
try:
    import pkg_resources
except ImportError:
    pkg_resources = None

from raven._compat import text_type
from .exceptions import InvalidGitRepository
__all__ = ('fetch_git_sha', 'fetch_package_version')

def fetch_git_sha(path, head = None):
    if not head:
        head_path = os.path.join(path, '.git', 'HEAD')
        if not os.path.exists(head_path):
            raise InvalidGitRepository('Cannot identify HEAD for git repository at %s' % (path,))
        with open(head_path, 'r') as fp:
            head = text_type(fp.read()).strip()
        if head.startswith('ref: '):
            head = head[5:]
            revision_file = os.path.join(path, '.git', *head.split('/'))
        else:
            return head
    else:
        revision_file = os.path.join(path, '.git', 'refs', 'heads', head)
    if not os.path.exists(revision_file):
        if not os.path.exists(os.path.join(path, '.git')):
            raise InvalidGitRepository('%s does not seem to be the root of a git repository' % (path,))
        packed_file = os.path.join(path, '.git', 'packed-refs')
        if os.path.exists(packed_file):
            with open(packed_file, 'r') as fh:
                for line in fh:
                    line = line.rstrip()
                    if not line:
                        continue
                    if line[:1] in ('#', '^'):
                        continue
                    try:
                        revision, ref = line.split(' ', 1)
                    except ValueError:
                        continue

                    if ref == head:
                        return text_type(revision)

        raise InvalidGitRepository('Unable to find ref to head "%s" in repository' % (head,))
    fh = open(revision_file, 'r')
    try:
        return text_type(fh.read()).strip()
    finally:
        fh.close()


def fetch_package_version(dist_name):
    if pkg_resources is None:
        raise NotImplementedError('pkg_resources is not available on this Python install')
    dist = pkg_resources.get_distribution(dist_name)
    return dist.version
