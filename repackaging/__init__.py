#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\repackaging\__init__.py
import evetypes
import dogma.const as dogmaconst
import inventorycommon.const as invconst
from eveexceptions import UserError
from inventorycommon.util import IsShipFittingFlag, IsRigFlag, IsJunkLocation, IsNPC
REPACKABLE_CATEGORIES = (invconst.categoryStarbase,
 invconst.categoryShip,
 invconst.categoryDrone,
 invconst.categoryModule,
 invconst.categorySubSystem,
 invconst.categorySovereigntyStructure,
 invconst.categoryDeployable,
 invconst.categoryStructure,
 invconst.categoryStructureModule)
REPACKABLE_GROUPS = (invconst.groupCargoContainer,
 invconst.groupSecureCargoContainer,
 invconst.groupAuditLogSecureContainer,
 invconst.groupFreightContainer,
 invconst.groupTool,
 invconst.groupMobileWarpDisruptor)

def CheckCanRepackage(item, dogma = None):
    if not item.singleton:
        raise UserError('RepackageItemNotSingleton')
    if IsNPC(item.ownerID):
        raise UserError('NotAvailableForNpcCorp')
    if not CanRepackageType(item.typeID):
        raise UserError('CanNotUnassembleInThisItemLoc')
    if not CanRepackageLocation(item.locationID, item.flagID):
        raise UserError('CanNotUnassembleInThisItemLoc')
    if dogma and dogma.TypeHasAttribute(item.typeID, dogmaconst.attributeArmorHP):
        if dogma.GetAttributeValue(item.itemID, dogmaconst.attributeArmorDamage):
            raise UserError('CantRepackageDamagedItem')
    if dogma and dogma.TypeHasAttribute(item.typeID, dogmaconst.attributeHp):
        if dogma.GetAttributeValue(item.itemID, dogmaconst.attributeDamage):
            raise UserError('CantRepackageDamagedItem')


def CanRepackageLocation(locationID, flagID):
    if IsShipFittingFlag(flagID):
        return False
    if IsJunkLocation(locationID):
        return False
    return True


def CanRepackageType(typeID):
    if evetypes.GetCategoryID(typeID) in REPACKABLE_CATEGORIES:
        return True
    if evetypes.GetGroupID(typeID) in REPACKABLE_GROUPS:
        return True
    return False


def GetContentForRepackaging(contents):
    moved = []
    destroyed = []
    for item in contents:
        _CheckItem(item)
        if _ItemDestroyed(item):
            destroyed.append(item)
        elif _ItemPrioritized(item):
            moved.insert(0, item)
        else:
            moved.append(item)

    return (destroyed, moved)


def _CheckItem(item):
    if item.flagID == invconst.flagPilot:
        raise UserError('PeopleAboardShip')


def _ItemDestroyed(item):
    if item.flagID == invconst.flagHiddenModifers:
        return True
    return IsRigFlag(item.flagID)


def _ItemPrioritized(item):
    return item.categoryID == invconst.categoryCharge and IsShipFittingFlag(item.flagID)
