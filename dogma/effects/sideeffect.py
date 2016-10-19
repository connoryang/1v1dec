#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\effects\sideeffect.py
from dogma.effects import Effect

def GetSideEffectClassByTypeString(effectType):
    if effectType == 'EffectStopper':
        return _GetEffectStopper


def _GetEffectStopper(effectDict):
    return EffectStopper(effectDict['effectID'])


class EffectStopper(Effect):

    def __init__(self, effectID):
        self.effectID = effectID

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        dogmaLM.StopEffect(self.effectID, targetID, forced=True)
