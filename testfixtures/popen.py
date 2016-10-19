#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\testfixtures\popen.py
from mock import Mock
from subprocess import Popen
from tempfile import TemporaryFile
from testfixtures.compat import basestring

class MockPopen(object):

    def __init__(self):
        self.commands = {}
        self.mock = mock = Mock()
        self.mock.Popen.side_effect = self.Popen
        mock.Popen_instance = Mock(spec=Popen)
        inst = mock.Popen.return_value = mock.Popen_instance
        inst.communicate.side_effect = self.communicate
        inst.wait.side_effect = self.wait
        inst.send_signal.side_effect = self.send_signal
        inst.terminate.side_effect = self.terminate
        inst.kill.side_effect = self.kill
        inst.poll.side_effect = self.poll

    def set_command(self, command, stdout = '', stderr = '', returncode = 0, pid = 1234, poll_count = 3):
        self.commands[command] = (stdout,
         stderr,
         returncode,
         pid,
         poll_count)

    def __call__(self, *args, **kw):
        return self.mock.Popen(*args, **kw)

    def Popen(self, args, bufsize = 0, executable = None, stdin = None, stdout = None, stderr = None, preexec_fn = None, close_fds = False, shell = False, cwd = None, env = None, universal_newlines = False, startupinfo = None, creationflags = 0):
        if isinstance(args, basestring):
            cmd = args
        else:
            cmd = ' '.join(args)
        if cmd not in self.commands:
            raise KeyError('Nothing specified for command %r' % cmd)
        self.stdout, self.stderr, self.returncode, pid, poll = self.commands[cmd]
        self.poll_count = poll
        for name in ('stdout', 'stderr'):
            f = TemporaryFile()
            f.write(getattr(self, name))
            f.flush()
            f.seek(0)
            setattr(self.mock.Popen_instance, name, f)

        self.mock.Popen_instance.pid = pid
        self.mock.Popen_instance.returncode = None
        return self.mock.Popen_instance

    def wait(self):
        self.mock.Popen_instance.returncode = self.returncode
        return self.returncode

    def communicate(self, input = None):
        self.wait()
        return (self.stdout, self.stderr)

    def poll(self):
        while self.poll_count and self.mock.Popen_instance.returncode is None:
            self.poll_count -= 1
            return

        return self.wait()

    def send_signal(self, signal):
        pass

    def terminate(self):
        pass

    def kill(self):
        pass
