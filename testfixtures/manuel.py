#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\testfixtures\manuel.py
from __future__ import absolute_import
import os
import re
import textwrap
from manuel import Manuel
from testfixtures import diff
FILEBLOCK_START = re.compile('^\\.\\.\\s*topic::?\\s*(.+)\\b', re.MULTILINE)
FILEBLOCK_END = re.compile('(\\n\\Z|\\n(?=\\S))')
CLASS = re.compile('\\s+:class:\\s*(read|write)-file')

class FileBlock(object):

    def __init__(self, path, content, action):
        self.path, self.content, self.action = path, content, action


class FileResult(object):
    passed = True
    expected = None
    actual = None


class Files(Manuel):

    def __init__(self, name):
        self.name = name
        Manuel.__init__(self, parsers=[self.parse], evaluaters=[self.evaluate], formatters=[self.format])

    def parse(self, document):
        for region in document.find_regions(FILEBLOCK_START, FILEBLOCK_END):
            lines = region.source.splitlines()
            class_ = CLASS.match(lines[1])
            if not class_:
                continue
            index = 3
            if lines[index].strip() == '::':
                index += 1
            source = textwrap.dedent('\n'.join(lines[index:])).lstrip()
            if source[-1] != '\n':
                source += '\n'
            region.parsed = FileBlock(region.start_match.group(1), source, class_.group(1))
            document.claim_region(region)

    def evaluate(self, region, document, globs):
        if not isinstance(region.parsed, FileBlock):
            return
        block = region.parsed
        dir = globs[self.name]
        result = region.evaluated = FileResult()
        if block.action == 'read':
            actual = dir.read(block.path, 'ascii').replace(os.linesep, '\n')
            if actual != block.content:
                result.passed = False
                result.path = block.path
                result.expected = block.content
                result.actual = actual
        if block.action == 'write':
            dir.write(block.path, block.content, 'ascii')

    def format(self, document):
        for region in document:
            result = region.evaluated
            if not isinstance(result, FileResult):
                continue
            if not result.passed:
                region.formatted = diff(result.expected, result.actual, 'File "%s", line %i:' % (document.location, region.lineno), 'Reading from "%s":' % result.path)
