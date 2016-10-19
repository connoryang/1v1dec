#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\script\dogma\pythonEffects\microJumpPortalDrive.py
from dogma.const import attributeDisallowTethering, dgmAssModAdd
from dogma.effects import Effect
from eve.common.script.dogma.pythonEffects.microJumpDrive import RemoveSignatureRadiusBonusPercentModifier, AddSignatureRadiusBonusPercentModifier

def AddDisallowTetheringModifier(dogmaLM, itemID, shipID):
    dogmaLM.AddModifier(dgmAssModAdd, shipID, attributeDisallowTethering, itemID, attributeDisallowTethering)


def RemoveDisallowTetheringModifier(dogmaLM, itemID, shipID):
    dogmaLM.RemoveModifier(dgmAssModAdd, shipID, attributeDisallowTethering, itemID, attributeDisallowTethering)


class BaseMicroJumpPortalDrive(Effect):
    __guid__ = 'dogmaXP.MicroJumpPortalDrive'
    __effectIDs__ = ['effectMicroJumpPortalDrive']
    effectIDList = None

    def PreStartChecks(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        pass

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        AddDisallowTetheringModifier(dogmaLM, itemID, shipID)
        AddSignatureRadiusBonusPercentModifier(dogmaLM, itemID, shipID)

    def Stop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        RemoveSignatureRadiusBonusPercentModifier(dogmaLM, itemID, shipID)
        RemoveDisallowTetheringModifier(dogmaLM, itemID, shipID)

    def RestrictedStop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        RemoveSignatureRadiusBonusPercentModifier(dogmaLM, itemID, shipID)
        RemoveDisallowTetheringModifier(dogmaLM, itemID, shipID)
