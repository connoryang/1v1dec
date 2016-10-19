#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\script\dogma\pythonEffects\emergencyHullEnergizer.py
import dogma.const as dogmaconst
from dogma.effects import Effect

class BaseEmergencyHullEnergizer(Effect):
    __guid__ = 'dogmaXP.EmergencyHullEnergizer'
    __effectIDs__ = ['effectEmergencyHullEnergizer']
    resistanceAttributes = {dogmaconst.attributeEmDamageResonance: dogmaconst.attributeHullEmDamageResonance,
     dogmaconst.attributeThermalDamageResonance: dogmaconst.attributeHullThermalDamageResonance,
     dogmaconst.attributeKineticDamageResonance: dogmaconst.attributeHullKineticDamageResonance,
     dogmaconst.attributeExplosiveDamageResonance: dogmaconst.attributeHullExplosiveDamageResonance}

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        self.DamageModule(dogmaLM, itemID)
        for shipAttribute, itemAttribute in self.resistanceAttributes.iteritems():
            dogmaLM.AddModifier(dogmaconst.dgmAssPostMul, shipID, shipAttribute, itemID, itemAttribute)

    def DamageModule(self, dogmaLM, itemID):
        pass

    def Stop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        for shipAttribute, itemAttribute in self.resistanceAttributes.iteritems():
            dogmaLM.RemoveModifier(dogmaconst.dgmAssPostMul, shipID, shipAttribute, itemID, itemAttribute)

        self.TakeModuleOffline(dogmaLM, itemID, shipID, charID)

    def TakeModuleOffline(self, dogmaLM, itemID, shipID, charID):
        pass

    RestrictedStop = Stop
