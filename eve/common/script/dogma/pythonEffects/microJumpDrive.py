#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\script\dogma\pythonEffects\microJumpDrive.py
from dogma.const import dgmAssPostPercent, attributeSignatureRadius, attributeSignatureRadiusBonusPercent
from dogma.effects import Effect

def AddSignatureRadiusBonusPercentModifier(dogmaLM, itemID, shipID):
    dogmaLM.AddModifier(dgmAssPostPercent, shipID, attributeSignatureRadius, itemID, attributeSignatureRadiusBonusPercent)


def RemoveSignatureRadiusBonusPercentModifier(dogmaLM, itemID, shipID):
    dogmaLM.RemoveModifier(dgmAssPostPercent, shipID, attributeSignatureRadius, itemID, attributeSignatureRadiusBonusPercent)


class BaseMicroJumpDrive(Effect):
    __guid__ = 'dogmaXP.MicroJumpDrive'
    __effectIDs__ = ['effectMicroJumpDrive', 'effectFighterMicroJumpDrive']
    effectIDList = None

    def PreStartChecks(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        pass

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        AddSignatureRadiusBonusPercentModifier(dogmaLM, itemID, shipID)

    def Stop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        RemoveSignatureRadiusBonusPercentModifier(dogmaLM, itemID, shipID)

    def RestrictedStop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        RemoveSignatureRadiusBonusPercentModifier(dogmaLM, itemID, shipID)
