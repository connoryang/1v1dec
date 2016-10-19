#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\testfixtures\components.py
import atexit
import warnings
from zope.component import getSiteManager
from zope.component.registry import Components

class TestComponents:
    instances = set()
    atexit_setup = False

    def __init__(self):
        self.registry = Components('Testing')
        self.old = getSiteManager.sethook(lambda : self.registry)
        self.instances.add(self)
        if not self.__class__.atexit_setup:
            atexit.register(self.atexit)
            self.__class__.atexit_setup = True

    def uninstall(self):
        getSiteManager.sethook(self.old)
        self.instances.remove(self)

    @classmethod
    def atexit(cls):
        if cls.instances:
            warnings.warn('TestComponents instances not uninstalled by shutdown!')
