#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\script\util\inventoryFlagsCommon.py
import dogma.const
from eveexceptions.const import UE_TYPEID, UE_CATID, UE_GROUPID
import evetypes
import inventorycommon.const
inventoryFlagData = {inventorycommon.const.flagCargo: {'name': 'UI/Ship/CargoHold',
                                   'attribute': dogma.const.attributeCapacity,
                                   'allowCategories': None,
                                   'allowGroups': None,
                                   'blockGroups': None,
                                   'allowTypes': None,
                                   'blockTypes': None},
 inventorycommon.const.flagDroneBay: {'name': 'UI/Ship/DroneBay',
                                      'attribute': dogma.const.attributeDroneCapacity,
                                      'allowCategories': (inventorycommon.const.categoryDrone,),
                                      'allowGroups': None,
                                      'blockGroups': None,
                                      'allowTypes': None,
                                      'blockTypes': None},
 inventorycommon.const.flagFighterBay: {'name': 'UI/Ship/FighterBay',
                                        'attribute': dogma.const.attributeFighterCapacity,
                                        'allowCategories': (inventorycommon.const.categoryFighter,),
                                        'allowGroups': None,
                                        'blockGroups': None,
                                        'allowTypes': None,
                                        'blockTypes': None},
 inventorycommon.const.flagShipHangar: {'name': 'UI/Ship/ShipMaintenanceBay',
                                        'attribute': dogma.const.attributeShipMaintenanceBayCapacity,
                                        'allowCategories': (inventorycommon.const.categoryShip,),
                                        'allowGroups': None,
                                        'blockGroups': (inventorycommon.const.groupCapsule,),
                                        'allowTypes': None,
                                        'blockTypes': None},
 inventorycommon.const.flagFleetHangar: {'name': 'UI/Ship/FleetHangar',
                                         'attribute': dogma.const.attributeFleetHangarCapacity,
                                         'allowCategories': None,
                                         'allowGroups': None,
                                         'blockGroups': None,
                                         'allowTypes': None,
                                         'blockTypes': None},
 inventorycommon.const.flagSpecializedFuelBay: {'name': 'UI/Ship/FuelBay',
                                                'attribute': dogma.const.attributeSpecialFuelBayCapacity,
                                                'allowCategories': None,
                                                'blockCategories': None,
                                                'allowGroups': (inventorycommon.const.groupIceProduct,),
                                                'blockGroups': None,
                                                'allowTypes': None,
                                                'blockTypes': None},
 inventorycommon.const.flagSpecializedOreHold: {'name': 'UI/Ship/OreHold',
                                                'attribute': dogma.const.attributeSpecialOreHoldCapacity,
                                                'allowCategories': (inventorycommon.const.categoryAsteroid,),
                                                'blockCategories': None,
                                                'allowGroups': (inventorycommon.const.groupHarvestableCloud,),
                                                'blockGroups': None,
                                                'allowTypes': None,
                                                'blockTypes': None},
 inventorycommon.const.flagSpecializedGasHold: {'name': 'UI/Ship/GasHold',
                                                'attribute': dogma.const.attributeSpecialGasHoldCapacity,
                                                'allowCategories': None,
                                                'blockCategories': None,
                                                'allowGroups': (inventorycommon.const.groupHarvestableCloud,),
                                                'blockGroups': None,
                                                'allowTypes': None,
                                                'blockTypes': None},
 inventorycommon.const.flagSpecializedMineralHold: {'name': 'UI/Ship/MineralHold',
                                                    'attribute': dogma.const.attributeSpecialMineralHoldCapacity,
                                                    'allowCategories': None,
                                                    'blockCategories': None,
                                                    'allowGroups': (inventorycommon.const.groupMineral,),
                                                    'blockGroups': None,
                                                    'allowTypes': None,
                                                    'blockTypes': None},
 inventorycommon.const.flagSpecializedSalvageHold: {'name': 'UI/Ship/SalvageHold',
                                                    'attribute': dogma.const.attributeSpecialSalvageHoldCapacity,
                                                    'allowCategories': None,
                                                    'blockCategories': None,
                                                    'allowGroups': (inventorycommon.const.groupAncientSalvage, inventorycommon.const.groupSalvagedMaterials, inventorycommon.const.groupRefinables),
                                                    'blockGroups': None,
                                                    'allowTypes': None,
                                                    'blockTypes': None},
 inventorycommon.const.flagSpecializedShipHold: {'name': 'UI/Ship/ShipHold',
                                                 'attribute': dogma.const.attributeSpecialShipHoldCapacity,
                                                 'allowCategories': (inventorycommon.const.categoryShip,),
                                                 'blockCategories': None,
                                                 'allowGroups': None,
                                                 'blockGroups': None,
                                                 'allowTypes': None,
                                                 'blockTypes': None},
 inventorycommon.const.flagSpecializedSmallShipHold: {'name': 'UI/Ship/SmallShipHold',
                                                      'attribute': dogma.const.attributeSpecialSmallShipHoldCapacity,
                                                      'allowCategories': None,
                                                      'blockCategories': None,
                                                      'allowGroups': (inventorycommon.const.groupFrigate,
                                                                      inventorycommon.const.groupAssaultShip,
                                                                      inventorycommon.const.groupDestroyer,
                                                                      inventorycommon.const.groupInterdictor,
                                                                      inventorycommon.const.groupInterceptor,
                                                                      inventorycommon.const.groupCovertOps,
                                                                      inventorycommon.const.groupElectronicAttackShips,
                                                                      inventorycommon.const.groupStealthBomber,
                                                                      inventorycommon.const.groupExpeditionFrigate,
                                                                      inventorycommon.const.groupTacticalDestroyer,
                                                                      inventorycommon.const.groupLogisticsFrigate,
                                                                      inventorycommon.const.groupCommandDestroyer),
                                                      'blockGroups': None,
                                                      'allowTypes': None,
                                                      'blockTypes': None},
 inventorycommon.const.flagSpecializedMediumShipHold: {'name': 'UI/Ship/MediumShipHold',
                                                       'attribute': dogma.const.attributeSpecialMediumShipHoldCapacity,
                                                       'allowCategories': None,
                                                       'blockCategories': None,
                                                       'allowGroups': (inventorycommon.const.groupCruiser,
                                                                       inventorycommon.const.groupCombatReconShip,
                                                                       inventorycommon.const.groupCommandShip,
                                                                       inventorycommon.const.groupHeavyAssaultShip,
                                                                       inventorycommon.const.groupHeavyInterdictors,
                                                                       inventorycommon.const.groupLogistics,
                                                                       inventorycommon.const.groupStrategicCruiser,
                                                                       inventorycommon.const.groupBattlecruiser,
                                                                       inventorycommon.const.groupAttackBattlecruiser,
                                                                       inventorycommon.const.groupForceReconShip),
                                                       'blockGroups': None,
                                                       'allowTypes': None,
                                                       'blockTypes': None},
 inventorycommon.const.flagSpecializedLargeShipHold: {'name': 'UI/Ship/LargeShipHold',
                                                      'attribute': dogma.const.attributeSpecialLargeShipHoldCapacity,
                                                      'allowCategories': None,
                                                      'blockCategories': None,
                                                      'allowGroups': (inventorycommon.const.groupBattleship, inventorycommon.const.groupBlackOps, inventorycommon.const.groupMarauders),
                                                      'blockGroups': None,
                                                      'allowTypes': None,
                                                      'blockTypes': None},
 inventorycommon.const.flagSpecializedIndustrialShipHold: {'name': 'UI/Ship/IndustrialShipHold',
                                                           'attribute': dogma.const.attributeSpecialIndustrialShipHoldCapacity,
                                                           'allowCategories': None,
                                                           'blockCategories': None,
                                                           'allowGroups': (inventorycommon.const.groupBlockadeRunner,
                                                                           inventorycommon.const.groupExhumer,
                                                                           inventorycommon.const.groupIndustrial,
                                                                           inventorycommon.const.groupMiningBarge,
                                                                           inventorycommon.const.groupTransportShip,
                                                                           inventorycommon.const.groupExpeditionFrigate),
                                                           'blockGroups': None,
                                                           'allowTypes': None,
                                                           'blockTypes': None},
 inventorycommon.const.flagSpecializedAmmoHold: {'name': 'UI/Ship/AmmoHold',
                                                 'attribute': dogma.const.attributeSpecialAmmoHoldCapacity,
                                                 'allowCategories': (inventorycommon.const.categoryCharge,),
                                                 'blockCategories': None,
                                                 'allowGroups': None,
                                                 'blockGroups': None,
                                                 'allowTypes': None,
                                                 'blockTypes': None},
 inventorycommon.const.flagSpecializedCommandCenterHold: {'name': 'UI/Ship/CommandCenterHold',
                                                          'attribute': dogma.const.attributeSpecialCommandCenterHoldCapacity,
                                                          'allowCategories': None,
                                                          'blockCategories': None,
                                                          'allowGroups': (inventorycommon.const.groupCommandPins,),
                                                          'blockGroups': None,
                                                          'allowTypes': None,
                                                          'blockTypes': None},
 inventorycommon.const.flagSpecializedPlanetaryCommoditiesHold: {'name': 'UI/Ship/PlanetaryCommoditiesHold',
                                                                 'attribute': dogma.const.attributeSpecialPlanetaryCommoditiesHoldCapacity,
                                                                 'allowCategories': (inventorycommon.const.categoryPlanetaryCommodities, inventorycommon.const.categoryPlanetaryResources),
                                                                 'blockCategories': None,
                                                                 'allowGroups': None,
                                                                 'blockGroups': None,
                                                                 'allowTypes': (inventorycommon.const.typeWater, inventorycommon.const.typeOxygen),
                                                                 'blockTypes': None},
 inventorycommon.const.flagSpecializedMaterialBay: {'name': 'UI/Ship/MaterialBay',
                                                    'attribute': dogma.const.attributeSpecialMaterialBayCapacity,
                                                    'allowCategories': (inventorycommon.const.categoryPlanetaryCommodities, inventorycommon.const.categoryCommodity, inventorycommon.const.categoryMaterial),
                                                    'blockCategories': None,
                                                    'allowGroups': None,
                                                    'blockGroups': None,
                                                    'allowTypes': None,
                                                    'blockTypes': None},
 inventorycommon.const.flagQuafeBay: {'name': 'UI/Ship/QuafeBay',
                                      'attribute': dogma.const.attributeSpecialQuafeHoldCapacity,
                                      'allowCategories': None,
                                      'blockCategories': None,
                                      'allowGroups': None,
                                      'blockGroups': None,
                                      'allowTypes': (inventorycommon.const.typeLargeCratesOfQuafe,
                                                     inventorycommon.const.typeQuafe,
                                                     inventorycommon.const.typeQuafeUltra,
                                                     inventorycommon.const.typeQuafeUltraSpecialEdition,
                                                     inventorycommon.const.typeQuafeZero,
                                                     inventorycommon.const.typeSpikedQuafe),
                                      'blockTypes': None}}

def ShouldAllowAdd(flag, categoryID, groupID, typeID):
    if flag not in inventoryFlagData:
        return
    flagData = inventoryFlagData[flag]
    errorTuple = None
    useAllow = True
    if flagData['allowCategories'] is not None:
        if categoryID in flagData['allowCategories']:
            useAllow = False
        else:
            errorTuple = (UE_CATID, categoryID)
    if useAllow:
        if flagData['allowGroups'] is not None:
            if groupID in flagData['allowGroups']:
                errorTuple = None
                useAllow = False
            else:
                errorTuple = (UE_GROUPID, groupID)
                useAllow = True
    elif flagData['blockGroups'] is not None:
        if groupID in flagData['blockGroups']:
            errorTuple = (UE_GROUPID, groupID)
            useAllow = True
        else:
            errorTuple = None
            useAllow = False
    if useAllow:
        if flagData['allowTypes'] is not None:
            if typeID in flagData['allowTypes']:
                errorTuple = None
            else:
                errorTuple = (UE_TYPEID, typeID)
    elif flagData['blockTypes'] is not None:
        if typeID in flagData['blockTypes']:
            errorTuple = (UE_TYPEID, typeID)
        else:
            errorTuple = None
    return errorTuple


autoConsumeTypes = {}
autoConsumeGroups = {inventorycommon.const.groupIceProduct: (inventorycommon.const.flagSpecializedFuelBay,)}
autoConsumeCategories = {}

def GetBaysToCheck(typeID, priorityBays = []):
    baysToCheck = list(priorityBays)
    if baysToCheck is None:
        baysToCheck = []
    if typeID in autoConsumeTypes:
        baysToCheck.extend(autoConsumeTypes[typeID])
    else:
        groupID = evetypes.GetGroupID(typeID)
        if groupID in autoConsumeGroups:
            baysToCheck.extend(autoConsumeGroups[groupID])
        else:
            categoryID = evetypes.GetCategoryID(typeID)
            if categoryID in autoConsumeCategories:
                baysToCheck.extend(autoConsumeCategories[categoryID])
    if inventorycommon.const.flagCargo not in baysToCheck:
        baysToCheck.append(inventorycommon.const.flagCargo)
    return baysToCheck


import carbon.common.script.util.autoexport as autoexport
exports = autoexport.AutoExports('inventoryFlagsCommon', locals())
