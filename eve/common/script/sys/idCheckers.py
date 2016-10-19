#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\script\sys\idCheckers.py
import eve.common.lib.appConst as const

def IsRegion(itemID):
    return itemID >= 10000000 and itemID < 20000000


def IsConstellation(itemID):
    return itemID >= 20000000 and itemID < 30000000


def IsSolarSystem(itemID):
    return itemID >= 30000000 and itemID < 40000000


def IsCelestial(itemID):
    return itemID >= 40000000 and itemID < 50000000


def IsStation(itemID):
    return itemID >= 60000000 and itemID < 64000000


def IsNPCCorporation(ownerID):
    return ownerID < 2000000 and ownerID >= 1000000


def IsDustCharacter(characterID):
    if const.minDustCharacter < characterID < const.maxDustCharacter:
        return True
    return False


def IsDustType(typeID):
    return typeID > const.minDustTypeID


def IsNewbieSystem(itemID):
    default = [30002547,
     30001392,
     30002715,
     30003489,
     30005305,
     30004971,
     30001672,
     30002505,
     30000141,
     30003410,
     30005042,
     30001407]
    return itemID in default
