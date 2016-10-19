#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\script\util\structuresCommon.py
import util
import const
import structures
STATION_SERVICE_MAPPING = {const.stationServiceBountyMissions: structures.SERVICE_MISSION,
 const.stationServiceAssassinationMissions: structures.SERVICE_MISSION,
 const.stationServiceCourierMission: structures.SERVICE_MISSION,
 const.stationServiceInterbus: None,
 const.stationServiceReprocessingPlant: structures.SERVICE_REPROCESSING,
 const.stationServiceRefinery: structures.SERVICE_REPROCESSING,
 const.stationServiceMarket: structures.SERVICE_MARKET,
 const.stationServiceBlackMarket: None,
 const.stationServiceStockExchange: None,
 const.stationServiceCloning: structures.SERVICE_MEDICAL,
 const.stationServiceSurgery: structures.SERVICE_MEDICAL,
 const.stationServiceDNATherapy: structures.SERVICE_MEDICAL,
 const.stationServiceRepairFacilities: structures.SERVICE_REPAIR,
 const.stationServiceFactory: structures.SERVICE_MANUFACTURING_SHIP,
 const.stationServiceLaboratory: structures.SERVICE_MANUFACTURING_SHIP,
 const.stationServiceGambling: None,
 const.stationServiceFitting: structures.SERVICE_FITTING,
 const.stationServiceNews: None,
 const.stationServiceStorage: None,
 const.stationServiceInsurance: structures.SERVICE_INSURANCE,
 const.stationServiceDocking: structures.SERVICE_DOCKING,
 const.stationServiceOfficeRental: structures.SERVICE_OFFICES,
 const.stationServiceJumpCloneFacility: structures.SERVICE_JUMP_CLONE,
 const.stationServiceLoyaltyPointStore: structures.SERVICE_LOYALTY_STORE,
 const.stationServiceNavyOffices: structures.SERVICE_FACTION_WARFARE,
 const.stationServiceSecurityOffice: structures.SERVICE_SECURITY_OFFICE,
 const.stationServiceCombatSimulator: None}
MANUFACTURING_SERVICE_CATEGORIES = {const.categoryCelestial: structures.SERVICE_MANUFACTURING_EQUIPMENT,
 const.categoryMaterial: structures.SERVICE_MANUFACTURING_EQUIPMENT,
 const.categoryAccessories: structures.SERVICE_MANUFACTURING_EQUIPMENT,
 const.categoryModule: structures.SERVICE_MANUFACTURING_EQUIPMENT,
 const.categoryCharge: structures.SERVICE_MANUFACTURING_EQUIPMENT,
 const.categoryDrone: structures.SERVICE_MANUFACTURING_EQUIPMENT,
 const.categoryImplant: structures.SERVICE_MANUFACTURING_EQUIPMENT,
 const.categoryDeployable: structures.SERVICE_MANUFACTURING_EQUIPMENT,
 const.categoryStarbase: structures.SERVICE_MANUFACTURING_EQUIPMENT,
 const.categoryInfrastructureUpgrade: structures.SERVICE_MANUFACTURING_EQUIPMENT,
 const.categorySovereigntyStructure: structures.SERVICE_MANUFACTURING_EQUIPMENT,
 const.categoryOrbital: structures.SERVICE_MANUFACTURING_EQUIPMENT,
 const.categoryCommodity: structures.SERVICE_MANUFACTURING_COMPONENT,
 const.categorySubSystem: structures.SERVICE_MANUFACTURING_COMPONENT}
MANUFACTURING_SERVICE_GROUPS = {const.groupBooster: structures.SERVICE_MANUFACTURING_EQUIPMENT,
 const.groupCapitalConstructionComponents: structures.SERVICE_MANUFACTURING_COMPONENT,
 const.groupAdvancedCapitalConstructionComponents: structures.SERVICE_MANUFACTURING_COMPONENT,
 const.groupFreighter: structures.SERVICE_MANUFACTURING_CAPITAL,
 const.groupJumpFreighter: structures.SERVICE_MANUFACTURING_CAPITAL,
 const.groupDreadnought: structures.SERVICE_MANUFACTURING_CAPITAL,
 const.groupCarrier: structures.SERVICE_MANUFACTURING_CAPITAL,
 const.groupCapitalIndustrialShip: structures.SERVICE_MANUFACTURING_CAPITAL,
 const.groupTitan: structures.SERVICE_MANUFACTURING_CAPITAL,
 const.groupSupercarrier: structures.SERVICE_MANUFACTURING_CAPITAL,
 const.groupFrigate: structures.SERVICE_MANUFACTURING_SHIP,
 const.groupCruiser: structures.SERVICE_MANUFACTURING_SHIP,
 const.groupBattleship: structures.SERVICE_MANUFACTURING_SHIP,
 const.groupIndustrial: structures.SERVICE_MANUFACTURING_SHIP,
 const.groupShuttle: structures.SERVICE_MANUFACTURING_SHIP,
 const.groupAssaultShip: structures.SERVICE_MANUFACTURING_SHIP,
 const.groupHeavyAssaultShip: structures.SERVICE_MANUFACTURING_SHIP,
 const.groupTransportShip: structures.SERVICE_MANUFACTURING_SHIP,
 const.groupEliteBattleship: structures.SERVICE_MANUFACTURING_SHIP,
 const.groupBattlecruiser: structures.SERVICE_MANUFACTURING_SHIP,
 const.groupDestroyer: structures.SERVICE_MANUFACTURING_SHIP,
 const.groupMiningBarge: structures.SERVICE_MANUFACTURING_SHIP,
 const.groupCommandShip: structures.SERVICE_MANUFACTURING_SHIP,
 const.groupInterdictor: structures.SERVICE_MANUFACTURING_SHIP,
 const.groupExhumer: structures.SERVICE_MANUFACTURING_SHIP,
 const.groupCovertOps: structures.SERVICE_MANUFACTURING_SHIP,
 const.groupInterceptor: structures.SERVICE_MANUFACTURING_SHIP,
 const.groupLogistics: structures.SERVICE_MANUFACTURING_SHIP,
 const.groupForceReconShip: structures.SERVICE_MANUFACTURING_SHIP,
 const.groupStealthBomber: structures.SERVICE_MANUFACTURING_SHIP,
 const.groupElectronicAttackShips: structures.SERVICE_MANUFACTURING_SHIP,
 const.groupHeavyInterdictors: structures.SERVICE_MANUFACTURING_SHIP,
 const.groupBlackOps: structures.SERVICE_MANUFACTURING_SHIP,
 const.groupMarauders: structures.SERVICE_MANUFACTURING_SHIP,
 const.groupCombatReconShip: structures.SERVICE_MANUFACTURING_SHIP,
 const.groupIndustrialCommandShip: structures.SERVICE_MANUFACTURING_SHIP,
 const.groupAttackBattlecruiser: structures.SERVICE_MANUFACTURING_SHIP,
 const.groupBlockadeRunner: structures.SERVICE_MANUFACTURING_SHIP,
 const.groupExpeditionFrigate: structures.SERVICE_MANUFACTURING_SHIP,
 const.groupLogisticsFrigate: structures.SERVICE_MANUFACTURING_SHIP,
 const.groupCommandDestroyer: structures.SERVICE_MANUFACTURING_SHIP,
 const.groupStrategicCruiser: structures.SERVICE_MANUFACTURING_SHIP,
 const.groupTacticalDestroyer: structures.SERVICE_MANUFACTURING_SHIP}

@util.Memoized
def GetServicesFromMask(serviceMask):
    if serviceMask is None:
        return set()
    structureServices = set()
    for i in xrange(64):
        p = 2 ** i
        if serviceMask & p > 0:
            structureServices.add(STATION_SERVICE_MAPPING.get(p))

    structureServices.discard(None)
    return structureServices


@util.Memoized
def GetStationServicesFromMask(serviceMask):
    if serviceMask is None:
        return set()
    stationServices = set()
    for i in xrange(64):
        p = 2 ** i
        if serviceMask & p > 0:
            stationServices.add(p)

    stationServices.discard(None)
    return stationServices


def GetStationService(serviceID):
    return STATION_SERVICE_MAPPING.get(serviceID)


def GetManufacturingService(groupID = None, categoryID = None):
    return MANUFACTURING_SERVICE_GROUPS.get(groupID, MANUFACTURING_SERVICE_CATEGORIES.get(categoryID))
