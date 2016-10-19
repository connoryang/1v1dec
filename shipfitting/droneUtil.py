#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\shipfitting\droneUtil.py
from shipfitting.fittingDogmaLocationUtil import GetDamageFromItem

def GatherDroneInfo(shipDogmaItem, dogmaLocation, activeDrones):
    droneInfo = {}
    for droneID, qty in activeDrones.iteritems():
        damage = GetDamageFromItem(dogmaLocation, droneID, isDrone=True)
        if damage == 0:
            continue
        damage *= qty
        damageMultiplier = dogmaLocation.GetAttributeValue(droneID, const.attributeDamageMultiplier)
        if damageMultiplier == 0:
            continue
        duration = dogmaLocation.GetAttributeValue(droneID, const.attributeRateOfFire)
        droneDps = damage * damageMultiplier / duration
        droneBandwidth = dogmaLocation.GetAttributeValue(droneID, const.attributeDroneBandwidthUsed)
        droneBandwidth *= qty
        droneDogmaItem = dogmaLocation.dogmaItems[droneID]
        droneInfo[droneID] = (droneDogmaItem.typeID, droneBandwidth, droneDps)

    return droneInfo


def GetSimpleGetDroneDamageOutput(drones, bwLeft, dronesLeft):
    totalDps = 0
    for droneID, droneInfo in drones.iteritems():
        typeID, bwNeeded, dps = droneInfo
        qty = 1
        noOfDrones = min(int(bwLeft) / int(bwNeeded), qty, dronesLeft)
        if noOfDrones == 0:
            break
        totalDps += qty * dps
        dronesLeft -= qty
        bwLeft -= qty * bwNeeded

    return totalDps


def GetOptimalDroneDamage(shipID, dogmaLocation, activeDrones):
    shipDogmaItem = dogmaLocation.dogmaItems[shipID]
    droneInfo = GatherDroneInfo(shipDogmaItem, dogmaLocation, activeDrones)
    dogmaLocation.LogInfo('Gathered drone info and found', len(droneInfo), 'types of drones')
    bandwidth = dogmaLocation.GetAttributeValue(shipID, const.attributeDroneBandwidth)
    maxDrones = dogmaLocation.GetAttributeValue(session.charid, const.attributeMaxActiveDrones)
    dps = GetSimpleGetDroneDamageOutput(droneInfo, bandwidth, maxDrones)
    return (dps * 1000, {})


def GetDroneRanges(shipID, dogmaLocation, activeDrones):
    maxRangeOfAll = 0
    minRangeOfAll = 0
    for droneID in activeDrones:
        maxRange = dogmaLocation.GetAttributeValue(droneID, const.attributeMaxRange)
        maxRangeOfAll = max(maxRangeOfAll, maxRange)
        if not minRangeOfAll:
            minRangeOfAll = maxRange
        else:
            minRangeOfAll = min(minRangeOfAll, maxRange)

    return (minRangeOfAll, maxRangeOfAll)


def GetDroneBandwidth(shipID, dogmaLocation, activeDrones):
    shipBandwidth = dogmaLocation.GetAttributeValue(shipID, const.attributeDroneBandwidth)
    bandwidthUsed = 0
    for droneID, qty in activeDrones.iteritems():
        bandwidthUsed += qty * dogmaLocation.GetAttributeValue(droneID, const.attributeDroneBandwidthUsed)

    return (bandwidthUsed, shipBandwidth)
