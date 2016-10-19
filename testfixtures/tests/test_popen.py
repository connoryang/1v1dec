#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\testfixtures\tests\test_popen.py
from subprocess import PIPE
from unittest import TestCase
from mock import call
from testfixtures import ShouldRaise, compare
from testfixtures.popen import MockPopen
from testfixtures.compat import PY2
import signal

class Tests(TestCase):

    def test_command_min_args(self):
        Popen = MockPopen()
        Popen.set_command('a command')
        process = Popen('a command', stdout=PIPE, stderr=PIPE)
        compare(process.pid, 1234)
        compare(None, process.returncode)
        out, err = process.communicate()
        compare(out, '')
        compare(err, '')
        compare(process.returncode, 0)
        compare([call.Popen('a command', stderr=-1, stdout=-1), call.Popen_instance.communicate()], Popen.mock.method_calls)

    def test_command_max_args(self):
        Popen = MockPopen()
        Popen.set_command('a command', 'out', 'err', 1, 345)
        process = Popen('a command', stdout=PIPE, stderr=PIPE)
        compare(process.pid, 345)
        compare(None, process.returncode)
        out, err = process.communicate()
        compare(out, 'out')
        compare(err, 'err')
        compare(process.returncode, 1)
        compare([call.Popen('a command', stderr=-1, stdout=-1), call.Popen_instance.communicate()], Popen.mock.method_calls)

    def test_command_is_sequence(self):
        Popen = MockPopen()
        Popen.set_command('a command')
        process = Popen(['a', 'command'], stdout=PIPE, stderr=PIPE)
        compare(process.wait(), 0)
        compare([call.Popen(['a', 'command'], stderr=-1, stdout=-1), call.Popen_instance.wait()], Popen.mock.method_calls)

    def test_communicate_with_input(self):
        Popen = MockPopen()
        Popen.set_command('a command')
        process = Popen('a command', stdout=PIPE, stderr=PIPE, shell=True)
        out, err = process.communicate('foo')
        compare([call.Popen('a command', shell=True, stderr=-1, stdout=-1), call.Popen_instance.communicate('foo')], Popen.mock.method_calls)

    def test_read_from_stdout(self):
        Popen = MockPopen()
        Popen.set_command('a command', stdout='foo')
        process = Popen('a command', stdout=PIPE, stderr=PIPE, shell=True)
        self.assertTrue(isinstance(process.stdout.fileno(), int))
        compare(process.stdout.read(), 'foo')
        compare([call.Popen('a command', shell=True, stderr=-1, stdout=-1)], Popen.mock.method_calls)

    def test_read_from_stderr(self):
        Popen = MockPopen()
        Popen.set_command('a command', stderr='foo')
        process = Popen('a command', stdout=PIPE, stderr=PIPE, shell=True)
        self.assertTrue(isinstance(process.stdout.fileno(), int))
        compare(process.stderr.read(), 'foo')
        compare([call.Popen('a command', shell=True, stderr=-1, stdout=-1)], Popen.mock.method_calls)

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

    def test_multiple_uses(self):
        Popen = MockPopen()
        Popen.set_command('a command', 'a')
        Popen.set_command('b command', 'b')
        process = Popen('a command', stdout=PIPE, stderr=PIPE, shell=True)
        out, err = process.communicate('foo')
        compare(out, 'a')
        process = Popen(['b', 'command'], stdout=PIPE, stderr=PIPE, shell=True)
        out, err = process.communicate('foo')
        compare(out, 'b')
        compare([call.Popen('a command', shell=True, stderr=-1, stdout=-1),
         call.Popen_instance.communicate('foo'),
         call.Popen(['b', 'command'], shell=True, stderr=-1, stdout=-1),
         call.Popen_instance.communicate('foo')], Popen.mock.method_calls)

    def test_send_signal(self):
        Popen = MockPopen()
        Popen.set_command('a command')
        process = Popen('a command', stdout=PIPE, stderr=PIPE, shell=True)
        process.send_signal(0)
        compare([call.Popen('a command', shell=True, stderr=-1, stdout=-1), call.Popen_instance.send_signal(0)], Popen.mock.method_calls)

    def test_terminate(self):
        Popen = MockPopen()
        Popen.set_command('a command')
        process = Popen('a command', stdout=PIPE, stderr=PIPE, shell=True)
        process.terminate()
        compare([call.Popen('a command', shell=True, stderr=-1, stdout=-1), call.Popen_instance.terminate()], Popen.mock.method_calls)

    def test_kill(self):
        Popen = MockPopen()
        Popen.set_command('a command')
        process = Popen('a command', stdout=PIPE, stderr=PIPE, shell=True)
        process.kill()
        compare([call.Popen('a command', shell=True, stderr=-1, stdout=-1), call.Popen_instance.kill()], Popen.mock.method_calls)

    def test_all_signals(self):
        Popen = MockPopen()
        Popen.set_command('a command')
        process = Popen('a command')
        process.send_signal(signal.SIGINT)
        process.terminate()
        process.kill()
        compare([call.Popen('a command'),
         call.Popen_instance.send_signal(signal.SIGINT),
         call.Popen_instance.terminate(),
         call.Popen_instance.kill()], Popen.mock.method_calls)

    def test_poll_no_setup(self):
        Popen = MockPopen()
        Popen.set_command('a command')
        process = Popen('a command', stdout=PIPE, stderr=PIPE, shell=True)
        compare(process.poll(), None)
        compare(process.poll(), None)
        compare(process.wait(), 0)
        compare(process.poll(), 0)
        compare([call.Popen('a command', shell=True, stderr=-1, stdout=-1),
         call.Popen_instance.poll(),
         call.Popen_instance.poll(),
         call.Popen_instance.wait(),
         call.Popen_instance.poll()], Popen.mock.method_calls)

    def test_poll_setup(self):
        Popen = MockPopen()
        Popen.set_command('a command', poll_count=1)
        process = Popen('a command', stdout=PIPE, stderr=PIPE, shell=True)
        compare(process.poll(), None)
        compare(process.poll(), 0)
        compare(process.wait(), 0)
        compare(process.poll(), 0)
        compare([call.Popen('a command', shell=True, stderr=-1, stdout=-1),
         call.Popen_instance.poll(),
         call.Popen_instance.poll(),
         call.Popen_instance.wait(),
         call.Popen_instance.poll()], Popen.mock.method_calls)

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

    def test_command_not_specified(self):
        Popen = MockPopen()
        with ShouldRaise(KeyError("Nothing specified for command 'a command'")):
            Popen('a command', stdout=PIPE, stderr=PIPE, shell=True)

    def test_invalid_parameters(self):
        Popen = MockPopen()
        with ShouldRaise(TypeError("Popen() got an unexpected keyword argument 'foo'")):
            Popen(foo='bar')

    def test_invalid_method_or_attr(self):
        Popen = MockPopen()
        Popen.set_command('command')
        process = Popen('command')
        with ShouldRaise(AttributeError("Mock object has no attribute 'foo'")):
            process.foo()

    def test_invalid_attribute(self):
        Popen = MockPopen()
        Popen.set_command('command')
        process = Popen('command')
        with ShouldRaise(AttributeError("Mock object has no attribute 'foo'")):
            process.foo

    def test_invalid_communicate_call(self):
        Popen = MockPopen()
        Popen.set_command('bar')
        process = Popen('bar')
        with ShouldRaise(TypeError("communicate() got an unexpected keyword argument 'foo'")):
            process.communicate(foo='bar')

    def test_invalid_wait_call(self):
        Popen = MockPopen()
        Popen.set_command('bar')
        process = Popen('bar')
        with ShouldRaise(TypeError("wait() got an unexpected keyword argument 'foo'")):
            process.wait(foo='bar')

    def test_invalid_send_signal(self):
        Popen = MockPopen()
        Popen.set_command('bar')
        process = Popen('bar')
        with ShouldRaise(TypeError("send_signal() got an unexpected keyword argument 'foo'")):
            process.send_signal(foo='bar')

    def test_invalid_terminate(self):
        Popen = MockPopen()
        Popen.set_command('bar')
        process = Popen('bar')
        with ShouldRaise(TypeError("terminate() got an unexpected keyword argument 'foo'")):
            process.terminate(foo='bar')

    def test_invalid_kill(self):
        Popen = MockPopen()
        Popen.set_command('bar')
        process = Popen('bar')
        if PY2:
            text = 'kill() takes exactly 1 argument (2 given)'
        else:
            text = 'kill() takes 1 positional argument but 2 were given'
        with ShouldRaise(TypeError(text)):
            process.kill('moo')

    def test_invalid_poll(self):
        Popen = MockPopen()
        Popen.set_command('bar')
        process = Popen('bar')
        if PY2:
            text = 'poll() takes exactly 1 argument (2 given)'
        else:
            text = 'poll() takes 1 positional argument but 2 were given'
        with ShouldRaise(TypeError(text)):
            process.poll('moo')
