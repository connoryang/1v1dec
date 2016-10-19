#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\testfixtures\tests\test_popen_docs.py
from subprocess import Popen, PIPE

def my_func():
    process = Popen('svn ls -R foo', stdout=PIPE, stderr=PIPE, shell=True)
    out, err = process.communicate()
    if process.returncode:
        raise RuntimeError('something bad happened')
    return out


dotted_path = 'testfixtures.tests.test_popen_docs.Popen'
from unittest import TestCase
from mock import call
from testfixtures import Replacer, ShouldRaise, compare
from testfixtures.popen import MockPopen

class TestMyFunc(TestCase):

    def setUp(self):
        self.Popen = MockPopen()
        self.r = Replacer()
        self.r.replace(dotted_path, self.Popen)
        self.addCleanup(self.r.restore)

    def test_example(self):
        self.Popen.set_command('svn ls -R foo', stdout='o', stderr='e')
        compare(my_func(), 'o')
        compare([call.Popen('svn ls -R foo', shell=True, stderr=PIPE, stdout=PIPE), call.Popen_instance.communicate()], Popen.mock.method_calls)

    def test_example_bad_returncode(self):
        Popen.set_command('svn ls -R foo', stdout='o', stderr='e', returncode=1)
        with ShouldRaise(RuntimeError('something bad happened')):
            my_func()

    def test_communicate_with_input(self):
        Popen = MockPopen()
        Popen.set_command('a command')
        process = Popen('a command', stdout=PIPE, stderr=PIPE, shell=True)
        out, err = process.communicate('foo')
        compare([call.Popen('a command', shell=True, stderr=-1, stdout=-1), call.Popen_instance.communicate('foo')], Popen.mock.method_calls)

    def test_read_from_stdout_and_stderr(self):
        Popen = MockPopen()
        Popen.set_command('a command', stdout='foo', stderr='bar')
        process = Popen('a command', stdout=PIPE, stderr=PIPE, shell=True)
        compare(process.stdout.read(), 'foo')
        compare(process.stderr.read(), 'bar')
        compare([call.Popen('a command', shell=True, stderr=PIPE, stdout=PIPE)], Popen.mock.method_calls)

    def test_wait_and_return_code(self):
        Popen = MockPopen()
        Popen.set_command('a command', returncode=3)
        process = Popen('a command')
        compare(process.returncode, None)
        compare(process.wait(), 3)
        compare(process.returncode, 3)
        compare([call.Popen('a command'), call.Popen_instance.wait()], Popen.mock.method_calls)

    def test_send_signal(self):
        Popen = MockPopen()
        Popen.set_command('a command')
        process = Popen('a command', stdout=PIPE, stderr=PIPE, shell=True)
        process.send_signal(0)
        compare([call.Popen('a command', shell=True, stderr=-1, stdout=-1), call.Popen_instance.send_signal(0)], Popen.mock.method_calls)

    def test_poll_until_result(self):
        Popen = MockPopen()
        Popen.set_command('a command', returncode=3, poll_count=2)
        process = Popen('a command')
        while process.poll() is None:
            pass

        compare(process.returncode, 3)
        compare([call.Popen('a command'),
         call.Popen_instance.poll(),
         call.Popen_instance.poll(),
         call.Popen_instance.poll()], Popen.mock.method_calls)
