#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\testfixtures\outputcapture.py
import sys
from testfixtures.comparison import compare
from testfixtures.compat import StringIO

class OutputCapture(object):
    original_stdout = None
    original_stderr = None

    def __init__(self, separate = False):
        self.separate = separate

    def __enter__(self):
        self.output = StringIO()
        self.stdout = StringIO()
        self.stderr = StringIO()
        self.enable()
        return self

    def __exit__(self, *args):
        self.disable()

    def disable(self):
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr

    def enable(self):
        if self.original_stdout is None:
            self.original_stdout = sys.stdout
            self.original_stderr = sys.stderr
        if self.separate:
            sys.stdout = self.stdout
            sys.stderr = self.stderr
        else:
            sys.stdout = sys.stderr = self.output

    @property
    def captured(self):
        return self.output.getvalue()

    def compare(self, expected = '', stdout = '', stderr = ''):
        for prefix, _expected, captured in ((None, expected, self.captured), ('stdout', stdout, self.stdout.getvalue()), ('stderr', stderr, self.stderr.getvalue())):
            compare(_expected.strip(), actual=captured.strip(), prefix=prefix)
