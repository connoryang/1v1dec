#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\testfixtures\tests\sample2.py
from testfixtures.tests.sample1 import X, z
try:
    from guppy import hpy
    guppy = True
except ImportError:
    guppy = False

def dump(path):
    if guppy:
        hpy().heap().stat.dump(path)
