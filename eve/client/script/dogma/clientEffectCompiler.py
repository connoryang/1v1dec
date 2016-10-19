#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\dogma\clientEffectCompiler.py
from eve.common.script.sys.rowset import Rowset
from eve.common.script.dogma.baseEffectCompiler import BaseEffectCompiler

class EffectDict(dict):

    def __init__(self, effectCompiler, *args):
        dict.__init__(self, *args)
        exec "dogma = sm.GetService('dogma')" in globals(), globals()
        self.effectCompiler = effectCompiler

    def __getitem__(self, effectID):
        try:
            return dict.__getitem__(self, effectID)
        except KeyError:
            effect = sm.GetService('clientDogmaStaticSvc').effects[effectID]
            flags = self.effectCompiler.ParseExpressionForInfluences(effect.preExpression)
            self.effectCompiler.flagsByEffect[effectID] = flags
            codez = self.effectCompiler.ParseEffect(effectID)
            d = {}
            exec 'from dogma.effects import Effect' in globals(), globals()
            exec "dogma = sm.GetService('dogma')"
            exec codez in globals(), globals()
            self[effectID] = globals().get('Effect_%d' % effectID)()
            return self[effectID]


class ClientEffectCompiler(BaseEffectCompiler):
    __guid__ = 'svc.clientEffectCompiler'
    __startupdependencies__ = ['dogma']

    def Run(self, *args):
        self.dogma = sm.GetService('dogma')
        BaseEffectCompiler.Run(self, *args)
        self.effects = EffectDict(self)
        self.SetupEffects()
        self.flagsByEffect = {}

    def GetDogmaStaticMgr(self):
        return sm.GetService('clientDogmaStaticSvc')
