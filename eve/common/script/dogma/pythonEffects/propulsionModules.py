#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\script\dogma\pythonEffects\propulsionModules.py
import dogma.const as dogmaconst
from dogma.effects import Effect
from dogma.attributes.attribute import LiteralAttribute
SPEED_BOOST_FACTOR_CALC = 0.01

class Afterburner(Effect):
    __guid__ = 'dogmaXP.Afterburner'
    __effectIDs__ = ['effectModuleBonusAfterburner']
    MODIFIER_CHANGES = [(dogmaconst.dgmAssModAdd, dogmaconst.attributeMass, dogmaconst.attributeMassAddition)]

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        self.AddModifiers(dogmaLM, shipID, itemID)
        speedFactor = dogmaLM.GetAttributeValue(itemID, dogmaconst.attributeSpeedFactor)
        speedBoostFactor = dogmaLM.GetAttributeValue(itemID, dogmaconst.attributeSpeedBoostFactor)
        shipMass = dogmaLM.GetAttributeValue(shipID, dogmaconst.attributeMass)
        speedMultiplier = 1 + SPEED_BOOST_FACTOR_CALC * speedFactor * speedBoostFactor / shipMass
        env.afterburner_speedMultiplierAttribute = LiteralAttribute(speedMultiplier)
        dogmaLM.AddModifierWithSource(dogmaconst.dgmAssPostMul, shipID, dogmaconst.attributeMaxVelocity, env.afterburner_speedMultiplierAttribute)

    def Stop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        self.RemoveModifiers(dogmaLM, shipID, itemID)
        dogmaLM.RemoveModifierWithSource(dogmaconst.dgmAssPostMul, shipID, dogmaconst.attributeMaxVelocity, env.afterburner_speedMultiplierAttribute)


class Microwarpdrive(Afterburner):
    __guid__ = 'dogmaXP.Microwarpdrive'
    __effectIDs__ = ['effectModuleBonusMicrowarpdrive']
    Afterburner.MODIFIER_CHANGES += [(dogmaconst.dgmAssPostPercent, dogmaconst.attributeSignatureRadius, dogmaconst.attributeSignatureRadiusBonus)]
