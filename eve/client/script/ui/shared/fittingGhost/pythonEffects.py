#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\pythonEffects.py
from dogma import const as dogmaConst
from dogma.effects import Effect
from eve.client.script.environment.effects.GenericEffect import GenericEffect

class Attack(Effect):
    __guid__ = 'testAttack'
    __effectIDs__ = ['effectTargetAttack',
     'effectTargetAttackForStructures',
     'effectProjectileFired',
     'effectProjectileFiredForEntities']

    def __init__(self, *args):
        pass


class OnlineEffect(Effect):
    __guid__ = 'OnlineEffect'
    __effectIDs__ = ['effectOnline']
    __modifier_only__ = 0

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        dogma = sm.GetService('dogma')
        cpuOutput = dogmaLM.GetAttributeValue(shipID, dogmaConst.attributeCpuOutput)
        cpuLoad = dogmaLM.GetAttributeValue(shipID, dogmaConst.attributeCpuLoad)
        cpu = dogmaLM.GetAttributeValue(itemID, dogmaConst.attributeCpu)
        if self.HasEnoughCpuLeft(cpu, cpuLoad, cpuOutput):
            powerOutput = dogmaLM.GetAttributeValue(shipID, dogmaConst.attributePowerOutput)
            powerLoad = dogmaLM.GetAttributeValue(shipID, dogmaConst.attributePowerLoad)
            power = dogmaLM.GetAttributeValue(itemID, dogmaConst.attributePower)
            if self.HasEnoughPowerLeft(power, powerLoad, powerOutput):
                dogmaLM.SetAttributeValue(itemID, dogmaConst.attributeIsOnline, 1)
                dogmaLM.AddModifier(dogmaConst.dgmAssModAdd, shipID, dogmaConst.attributeCpuLoad, itemID, dogmaConst.attributeCpu)
                dogmaLM.AddModifier(dogmaConst.dgmAssModAdd, shipID, dogmaConst.attributePowerLoad, itemID, dogmaConst.attributePower)
            else:
                dogma.UserError(env, 'NotEnoughPower', None)
        else:
            dogma.UserError(env, 'NotEnoughCpu', None)

    def HasEnoughCpuLeft(self, cpu, cpuLoad, cpuOutput):
        if self.ShouldIgnoreCpuPowerRestrictions():
            return True
        hasEnoughPowerLeft = cpuOutput >= cpuLoad + cpu
        return hasEnoughPowerLeft

    def HasEnoughPowerLeft(self, power, powerLoad, powerOutput):
        if self.ShouldIgnoreCpuPowerRestrictions():
            return True
        if power == 0:
            return True
        return powerOutput >= powerLoad + power

    def ShouldIgnoreCpuPowerRestrictions(self):
        return True

    def Stop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        dogmaLM.RemoveModifier(dogmaConst.dgmAssModAdd, shipID, const.attributeCpuLoad, itemID, const.attributeCpu)
        dogmaLM.RemoveModifier(dogmaConst.dgmAssModAdd, shipID, const.attributePowerLoad, itemID, const.attributePower)
        dogmaLM.SetAttributeValue(itemID, const.attributeIsOnline, 0)

    def RestrictedStop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        dogmaLM.RemoveModifier(dogmaConst.dgmAssModAdd, shipID, const.attributeCpuLoad, itemID, const.attributeCpu)
        dogmaLM.RemoveModifier(dogmaConst.dgmAssModAdd, shipID, const.attributePowerLoad, itemID, const.attributePower)
        dogmaLM.SetAttributeValue(itemID, const.attributeIsOnline, 0)


class Powerboost(Effect):
    __guid__ = 'dogmaXP.Effect_48'
    __effectIDs__ = [48]
    isPythonEffect = True

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        weaponID = env.itemID
        shipID = env.shipID
        item = dogmaLM.dogmaItems[weaponID]
        chargeKey = dogmaLM.GetSubLocation(shipID, item.flagID)
        if chargeKey is None:
            raise UserError('NoCharges', {'launcher': (const.UE_TYPEID, item.typeID)})
        chargeQuantity = dogmaLM.GetAttributeValue(chargeKey, const.attributeQuantity)
        if chargeQuantity is None or chargeQuantity < 1:
            raise UserError('NoCharges', {'launcher': (const.UE_TYPEID, item.typeID)})
        capacitorBonus = dogmaLM.GetAttributeValue(chargeKey, const.attributeCapacitorBonus)
        if capacitorBonus != 0:
            new, old = dogmaLM.IncreaseItemAttributeEx(env.shipID, const.attributeCharge, capacitorBonus, alsoReturnOldValue=True)
        return 1

    def Stop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        return 1

    def RestrictedStop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        return 1


class Mine(Effect):
    __guid__ = 'dogmaXP.Mining'
    __effectIDs__ = ['effectMining', 'effectMiningLaser', 'effectMiningClouds']

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, asteroidID):
        durationAttributeID = cfg.dgmeffects.Get(env.effectID).durationAttributeID
        duration = dogmaLM.GetAttributeValue(itemID, durationAttributeID)
        env.miningDuration = duration
        import blue
        env.startedEffect = blue.os.GetSimTime()

    def GetClamp(self, env, preferredDuration):
        import blue
        timePassed = blue.os.GetSimTime() - env.startedEffect
        millisecondsPassed = timePassed / 10000L
        return float(millisecondsPassed) / preferredDuration


class FakeCargoScan(Effect):
    __guid__ = 'dogmaXP.Effect_47'
    __effectIDs__ = [47]
    isPythonEffect = True


class FakePointDefense(Effect):
    __guid__ = 'dogmaXP.Effect_6443'
    __effectIDs__ = [6443]
    isPythonEffect = False


class FakeTargetHostile(Effect):
    __guid__ = 'dogmaXP.Effect_55'
    __effectIDs__ = [55]
    isPythonEffect = True


class FakeEmpWave(Effect):
    __guid__ = 'dogmaXP.Effect_38'
    __effectIDs__ = [38]
    isPythonEffect = True


class FakeSurveyScan(Effect):
    __guid__ = 'dogmaXP.Effect_81'
    __effectIDs__ = [81]
    isPythonEffect = True
