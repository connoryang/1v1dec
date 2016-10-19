#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\shipfitting\fittingDogmaLocationUtil.py
import math
from collections import defaultdict
from math import sqrt, log, exp
import evetypes
from carbonui.util.bunch import Bunch
from utillib import KeyVal
DAMAGE_ATTRIBUTES = (const.attributeEmDamage,
 const.attributeExplosiveDamage,
 const.attributeKineticDamage,
 const.attributeThermalDamage)

def GetFittingItemDragData(itemID, dogmaLocation):
    dogmaItem = dogmaLocation.dogmaItems[itemID]
    data = Bunch()
    data.__guid__ = 'listentry.InvItem'
    data.item = KeyVal(itemID=dogmaItem.itemID, typeID=dogmaItem.typeID, groupID=dogmaItem.groupID, categoryID=dogmaItem.categoryID, flagID=dogmaItem.flagID, ownerID=dogmaItem.ownerID, locationID=dogmaItem.locationID, stacksize=dogmaLocation.GetAttributeValue(itemID, const.attributeQuantity))
    data.rec = data.item
    data.itemID = itemID
    data.viewMode = 'icons'
    return [data]


def GetFittedItemsByFlag(dogmaLocation, typeHasEffectFunc):
    chargesByFlag = {}
    turretsByFlag = {}
    launchersByFlag = {}
    IsTurret = lambda typeID: typeHasEffectFunc(typeID, const.effectTurretFitted)
    IsLauncher = lambda typeID: typeHasEffectFunc(typeID, const.effectLauncherFitted)
    for module in dogmaLocation.GetFittedItemsToShip().itervalues():
        if IsTurret(module.typeID):
            if not dogmaLocation.IsModuleIncludedInCalculation(module):
                continue
            turretsByFlag[module.flagID] = module.itemID
        elif IsLauncher(module.typeID):
            if not dogmaLocation.IsModuleIncludedInCalculation(module):
                continue
            launchersByFlag[module.flagID] = module.itemID
        elif module.categoryID == const.categoryCharge:
            chargesByFlag[module.flagID] = module.itemID

    return (chargesByFlag, launchersByFlag, turretsByFlag)


def GetAlphaStrike(dogmaLocation, typeHasEffectFunc):
    chargesByFlag, launchersByFlag, turretsByFlag = GetFittedItemsByFlag(dogmaLocation, typeHasEffectFunc)
    GAV = dogmaLocation.GetAttributeValue
    alpha = 0.0
    ownerID = session.charid
    for flagID, itemID in launchersByFlag.iteritems():
        chargeKey = chargesByFlag.get(flagID)
        damagePerShot = _GetLauncherDamagePerShot(dogmaLocation, chargeKey, ownerID, GAV)
        alpha += damagePerShot

    for flagID, itemID in turretsByFlag.iteritems():
        chargeKey = chargesByFlag.get(flagID)
        damagePerShot = _GetTurretDamagePerShot(dogmaLocation, chargeKey, itemID, GAV)
        alpha += damagePerShot

    return alpha


def _GetTurretDps(GAV, chargesByFlag, dogmaLocation, turretsByFlag):
    turretDps = 0
    turretDpsWithReload = 0
    for flagID, itemID in turretsByFlag.iteritems():
        chargeKey = chargesByFlag.get(flagID)
        thisTurretDps, thisTurretDpsWithReload = GetTurretDps(dogmaLocation, chargeKey, itemID, GAV)
        turretDps += thisTurretDps
        turretDpsWithReload += thisTurretDpsWithReload

    return (turretDps, turretDpsWithReload)


def _GetMissileDps(GAV, chargesByFlag, dogmaLocation, launchersByFlag, shipDogmaItem):
    missileDps = 0
    missilDpsWithReload = 0
    for flagID, itemID in launchersByFlag.iteritems():
        chargeKey = chargesByFlag.get(flagID)
        if chargeKey is None:
            continue
        ownerID = session.charid
        thisLauncherDps, thisLauncherDpsWithReload = GetLauncherDps(dogmaLocation, chargeKey, itemID, ownerID, GAV)
        missileDps += thisLauncherDps
        missilDpsWithReload += thisLauncherDpsWithReload

    return (missileDps, missilDpsWithReload)


def GetTurretAndMissileDps(shipID, dogmaLocation, typeHasEffectFunc):
    shipDogmaItem = dogmaLocation.dogmaItems[shipID]
    GAV = dogmaLocation.GetAttributeValue
    if getattr(dogmaLocation, 'godma', False):
        godmaShipItem = dogmaLocation.godma.GetItem(shipID)
        if godmaShipItem is not None:
            GAV = dogmaLocation.GetGodmaAttributeValue
    chargesByFlag, launchersByFlag, turretsByFlag = GetFittedItemsByFlag(dogmaLocation, typeHasEffectFunc)
    turretDps, turretDpsWithReload = _GetTurretDps(GAV, chargesByFlag, dogmaLocation, turretsByFlag)
    missileDps, missileDpsWithReload = _GetMissileDps(GAV, chargesByFlag, dogmaLocation, launchersByFlag, shipDogmaItem)
    dpsInfo = KeyVal(turretDps=turretDps, turretDpsWithReload=turretDpsWithReload, missileDps=missileDps, missileDpsWithReload=missileDpsWithReload)
    return dpsInfo


def GetLauncherDps(dogmaLocation, chargeKey, itemID, ownerID, GAV, damageMultiplier = None):
    damagePerShot = _GetLauncherDamagePerShot(dogmaLocation, chargeKey, ownerID, GAV, damageMultiplier)
    duration = GAV(itemID, const.attributeRateOfFire)
    missileDps = damagePerShot / duration
    missileDpsWithReload = _GetDpsWithReload(chargeKey, itemID, GAV, damagePerShot, duration)
    return (missileDps * 1000, missileDpsWithReload * 1000)


def _GetLauncherDamagePerShot(dogmaLocation, chargeKey, ownerID, GAV, damageMultiplier = None):
    if chargeKey is None:
        return 0
    if damageMultiplier is None:
        damageMultiplier = GAV(ownerID, const.attributeMissileDamageMultiplier)
    damage = GetDamageFromItem(dogmaLocation, chargeKey)
    damagePerShot = damage * damageMultiplier
    return damagePerShot


def GetTurretDps(dogmaLocation, chargeKey, itemID, GAV, *args):
    turretDps = 0.0
    turretDpsWithReload = 0.0
    damagePerShot = _GetTurretDamagePerShot(dogmaLocation, chargeKey, itemID, GAV)
    if abs(damagePerShot) > 0:
        duration = GAV(itemID, const.attributeRateOfFire)
        if abs(duration) > 0:
            turretDps = damagePerShot / duration
            turretDpsWithReload = _GetDpsWithReload(chargeKey, itemID, GAV, damagePerShot, duration)
    return (turretDps * 1000, turretDpsWithReload * 1000)


def _GetTurretDamagePerShot(dogmaLocation, chargeKey, itemID, GAV):
    if chargeKey is not None:
        damage = GetDamageFromItem(dogmaLocation, chargeKey)
    else:
        damage = GetDamageFromItem(dogmaLocation, itemID)
    if damage > 0:
        damageMultiplier = GAV(itemID, const.attributeDamageMultiplier)
        damage *= damageMultiplier
    return damage


def _GetDpsWithReload(chargeKey, itemID, GAV, damagePerShot, duration):
    if chargeKey is None:
        return damagePerShot / duration
    reloadTime = GAV(itemID, const.attributeReloadTime)
    numShotBeforeReload = GetNumChargesFullyLoaded(chargeKey, itemID, GAV)
    missileDpsWithReload = numShotBeforeReload * damagePerShot / (numShotBeforeReload * duration + reloadTime)
    return missileDpsWithReload


def GetNumChargesFullyLoaded(chargeKey, itemID, GAV):
    launcherCapacity = GAV(itemID, const.attributeCapacity)
    chargeVolume = GAV(chargeKey, const.attributeVolume)
    numShotBeforeReload = int(launcherCapacity / float(chargeVolume))
    return numShotBeforeReload


def GetDamageFromItem(dogmaLocation, itemID, isDrone = False):
    accDamage = 0
    for attributeID in DAMAGE_ATTRIBUTES:
        if isDrone:
            d = dogmaLocation.GetAttributeValue(itemID, attributeID)
        else:
            d = dogmaLocation.GetAccurateAttributeValue(itemID, attributeID)
        accDamage += d

    return accDamage


def CapacitorSimulator(dogmaLocation, shipID):
    dogmaItem = dogmaLocation.dogmaItems[shipID]
    capacitorCapacity = dogmaLocation.GetAttributeValue(shipID, const.attributeCapacitorCapacity)
    rechargeTime = dogmaLocation.GetAttributeValue(shipID, const.attributeRechargeRate)
    modules = []
    totalCapNeed = 0
    modulesByFlag = {}
    chargesByFlag = {}
    for moduleID, module in dogmaItem.GetFittedItems().iteritems():
        if module.categoryID == const.categoryCharge:
            chargesByFlag[module.flagID] = module
        else:
            modulesByFlag[module.flagID] = module

    for flagID, module in modulesByFlag.iteritems():
        moduleID = module.itemID
        if not dogmaLocation.IsModuleIncludedInCalculation(module):
            continue
        try:
            defaultEffectID = dogmaLocation.dogmaStaticMgr.GetDefaultEffect(module.typeID)
        except KeyError:
            defaultEffectID = None

        if defaultEffectID is None:
            continue
        defaultEffect = dogmaLocation.dogmaStaticMgr.effects[defaultEffectID]
        durationAttributeID = defaultEffect.durationAttributeID
        dischargeAttributeID = defaultEffect.dischargeAttributeID
        if durationAttributeID is None:
            continue
        duration = dogmaLocation.GetAttributeValue(moduleID, durationAttributeID)
        reloadInfo = None
        moduleGroupID = evetypes.GetGroupID(module.typeID)
        if moduleGroupID == const.groupCapacitorBooster:
            charges = chargesByFlag.get(flagID, None)
            if not charges:
                continue
            avgCapInjectedEachCycle, capInjectedPerCycle, reloadInfo = _GetAvgInjectedEachCycle(dogmaLocation, moduleID, charges, duration)
            avgCapNeed = -avgCapInjectedEachCycle
            capNeed = -capInjectedPerCycle
        elif dischargeAttributeID is None:
            continue
        else:
            avgCapNeed = capNeed = dogmaLocation.GetAttributeValue(moduleID, dischargeAttributeID)
        k = KeyVal(capNeeded=capNeed, durationValue=long(duration * const.dgmTauConstant), nextRun=0, cyclesSinceReload=0, reloadInfo=reloadInfo)
        modules.append(k)
        totalCapNeed += avgCapNeed / duration

    rechargeRateAverage = capacitorCapacity / rechargeTime
    peakRechargeRate = 2.5 * rechargeRateAverage
    tau = rechargeTime / 5
    totalCapNeed = max(0, totalCapNeed)
    TTL = None
    runSimulation = totalCapNeed > peakRechargeRate
    if runSimulation or totalCapNeed / peakRechargeRate > 0.9:
        TTL = RunSimulation(capacitorCapacity, rechargeTime, modules)
        if TTL >= const.DAY:
            TTL = None
    if TTL is not None:
        loadBalance = 0
    else:
        c = 2 * capacitorCapacity / tau
        k = totalCapNeed / c
        exponent = (1 - sqrt(1 - 4 * k)) / 2
        if exponent == 0:
            loadBalance = 1
        else:
            t = -log(exponent) * tau
            loadBalance = (1 - exp(-t / tau)) ** 2
    return (peakRechargeRate,
     totalCapNeed,
     loadBalance,
     TTL)


def _GetReloadInfo(dogmaLocation, moduleID, charges):
    GAV = dogmaLocation.GetAttributeValue
    reloadTime = GAV(moduleID, const.attributeReloadTime)
    moduleCapacity = GAV(moduleID, const.attributeCapacity)
    chargeVolume = GAV(charges.itemID, const.attributeVolume)
    maxChargesInModule = int(moduleCapacity / float(chargeVolume))
    moduleRechargeInfo = KeyVal(reloadTime=reloadTime, maxChargesInModule=maxChargesInModule)
    return moduleRechargeInfo


def _GetAvgInjectedEachCycle(dogmaLocation, moduleID, charges, duration):
    moduleRechargeInfo = _GetReloadInfo(dogmaLocation, moduleID, charges)
    capInjectedPerCycle = dogmaLocation.GetAttributeValue(charges.itemID, const.attributeCapacitorBonus)
    injectedInOneLoad = moduleRechargeInfo.maxChargesInModule * capInjectedPerCycle
    durationOfFullLoad = moduleRechargeInfo.maxChargesInModule * duration
    avgCapInjectedEachCycle = injectedInOneLoad / (durationOfFullLoad + moduleRechargeInfo.reloadTime) * duration
    return (avgCapInjectedEachCycle, capInjectedPerCycle, moduleRechargeInfo)


def RunSimulation(capacitorCapacity, rechargeRate, modules):
    capacitor = capacitorCapacity
    tauThingy = float(const.dgmTauConstant) * (rechargeRate / 5.0)
    currentTime = nextTime = 0L
    while capacitor > 0.0 and nextTime < const.DAY:
        capacitor = (1.0 + (math.sqrt(capacitor / capacitorCapacity) - 1.0) * math.exp((currentTime - nextTime) / tauThingy)) ** 2 * capacitorCapacity
        currentTime = nextTime
        nextTime = const.DAY
        for data in modules:
            if data.nextRun == currentTime:
                capacitor -= data.capNeeded
                data.cyclesSinceReload += 1
                if data.reloadInfo:
                    if data.cyclesSinceReload >= data.reloadInfo.maxChargesInModule:
                        data.nextRun += data.reloadInfo.reloadTime * const.SEC
                        data.cyclesSinceReload = 0
                data.nextRun += data.durationValue
            nextTime = min(nextTime, data.nextRun)

    if capacitor > 0.0:
        return const.DAY
    return currentTime


LN_025 = math.log(0.25)

def GetAlignTime(dogmaLocation):
    shipID = dogmaLocation.GetCurrentShipID()
    agility = dogmaLocation.GetAttributeValue(shipID, const.attributeAgility)
    mass = dogmaLocation.GetAttributeValue(shipID, const.attributeMass)
    alignTime = -LN_025 * agility * mass / 1000000
    return alignTime


def GetFuelUsage(dogmaLocation):
    ship = dogmaLocation.GetShip()
    totalFuelPerHour = 0
    for itemID, dogmaItem in ship.GetFittedItems().iteritems():
        fuelPerHour = dogmaLocation.GetAttributeValue(itemID, const.attributeServiceModuleFuelAmount)
        if fuelPerHour and dogmaItem.IsOnline():
            totalFuelPerHour += fuelPerHour

    return totalFuelPerHour * 24


class SelectedDroneTracker(object):

    def __init__(self):
        self.selectedDronesDict = defaultdict(int)

    def RegisterDroneAsActive(self, droneID, qty = 1, raiseError = True):
        numDronesSelected = sum(self.selectedDronesDict.itervalues())
        if numDronesSelected >= 5:
            if raiseError:
                raise UserError('CustomNotify', {'notify': 'Can only have 5 drone active at a time'})
            else:
                return
        self.selectedDronesDict[droneID] += qty

    def UnregisterDroneFromActive(self, droneID, qty = 1):
        if droneID in self.selectedDronesDict:
            self.selectedDronesDict[droneID] -= qty
            if self.selectedDronesDict[droneID] <= 0:
                self.selectedDronesDict.pop(droneID)

    def GetSelectedDrones(self):
        return self.selectedDronesDict.copy()

    def SetDroneActivityState(self, droneID, setActive, qty = 1):
        if setActive:
            self.RegisterDroneAsActive(droneID, qty=qty)
        else:
            self.UnregisterDroneFromActive(droneID, qty=qty)

    def Clear(self):
        self.selectedDronesDict.clear()
