#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\packages\chardet\chardetect.py
from __future__ import absolute_import, print_function, unicode_literals
import argparse
import sys
from io import open
from chardet import __version__
from chardet.universaldetector import UniversalDetector

def description_of(lines, name = u'stdin'):
    u = UniversalDetector()
    for line in lines:
        u.feed(line)

    u.close()
    result = u.result
    if result[u'encoding']:
        return u'{0}: {1} with confidence {2}'.format(name, result[u'encoding'], result[u'confidence'])
    else:
        return u'{0}: no result'.format(name)


def main(argv = None):
    parser = argparse.ArgumentParser(description=u'Takes one or more file paths and reports their detected                      encodings', formatter_class=argparse.ArgumentDefaultsHelpFormatter, conflict_handler=u'resolve')
    parser.add_argument(u'input', help=u'File whose encoding we would like to determine.', type=argparse.FileType(u'rb'), nargs=u'*', default=[sys.stdin])
    parser.add_argument(u'--version', action=u'version', version=u'%(prog)s {0}'.format(__version__))
    args = parser.parse_args(argv)
    for f in args.input:
        if f.isatty():
            print(u'You are running chardetect interactively. Press ' + u'CTRL-D twice at the start of a blank line to signal the ' + u'end of your input. If you want help, run chardetect ' + u'--help\n', file=sys.stderr)
        print(description_of(f, f.name))


if __name__ == u'__main__':
    main()
