#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\structures\services.py
import structures
import inventorycommon.const
SERVICE_DOCKING = 1
SERVICE_FITTING = 2
SERVICE_OFFICES = 3
SERVICE_REPROCESSING = 4
SERVICE_MARKET = 5
SERVICE_MEDICAL = 6
SERVICE_MISSION = 7
SERVICE_REPAIR = 8
SERVICE_INSURANCE = 9
SERVICE_JUMP_CLONE = 10
SERVICE_LOYALTY_STORE = 11
SERVICE_FACTION_WARFARE = 12
SERVICE_SECURITY_OFFICE = 13
SERVICE_MANUFACTURING_UNKNOWN = 20
SERVICE_MANUFACTURING_CAPITAL = 21
SERVICE_MANUFACTURING_COMPONENT = 22
SERVICE_MANUFACTURING_EQUIPMENT = 23
SERVICE_MANUFACTURING_SHIP = 24
SERVICE_BLUEPRINT_UNKNOWN = 30
SERVICE_BLUEPRINT_INVENTION = 31
SERVICE_BLUEPRINT_RELIC_INVENTION = 32
SERVICE_BLUEPRINT_RESEARCH_TIME = 33
SERVICE_BLUEPRINT_RESEARCH_MATERIAL = 34
SERVICE_BLUEPRINT_COPYING = 35
SERVICES_BY_NAME = {name:value for name, value in locals().items() if name.startswith('SERVICE_')}
SERVICES = set(SERVICES_BY_NAME.values())
SERVICE_LABELS = {SERVICE_DOCKING: 'UI/StructureSettings/ServiceDocking',
 SERVICE_FITTING: 'UI/StructureSettings/ServiceFitting',
 SERVICE_OFFICES: 'UI/StructureSettings/ServiceCorpOffices',
 SERVICE_REPROCESSING: 'UI/StructureSettings/ServiceReprocessing',
 SERVICE_MARKET: 'UI/StructureSettings/ServiceMarket',
 SERVICE_MEDICAL: 'UI/StructureSettings/ServiceCloneBay',
 SERVICE_MISSION: 'UI/Station/Lobby/Agents',
 SERVICE_REPAIR: 'UI/Station/Repairshop',
 SERVICE_INSURANCE: 'UI/Station/Insurance',
 SERVICE_JUMP_CLONE: 'UI/StructureSettings/ServiceCloneBay',
 SERVICE_LOYALTY_STORE: 'UI/Station/LPStore',
 SERVICE_FACTION_WARFARE: 'UI/Station/MilitiaOffice',
 SERVICE_SECURITY_OFFICE: 'UI/Station/SecurityOffice',
 SERVICE_MANUFACTURING_UNKNOWN: 'UI/StructureSettings/ServiceManufacturing',
 SERVICE_MANUFACTURING_CAPITAL: 'UI/StructureSettings/ServiceManufacturing',
 SERVICE_MANUFACTURING_COMPONENT: 'UI/StructureSettings/ServiceManufacturing',
 SERVICE_MANUFACTURING_EQUIPMENT: 'UI/StructureSettings/ServiceManufacturing',
 SERVICE_MANUFACTURING_SHIP: 'UI/StructureSettings/ServiceManufacturing',
 SERVICE_BLUEPRINT_UNKNOWN: 'UI/StructureSettings/ServiceResearch',
 SERVICE_BLUEPRINT_INVENTION: 'UI/StructureSettings/ServiceResearch',
 SERVICE_BLUEPRINT_RELIC_INVENTION: 'UI/StructureSettings/ServiceResearch',
 SERVICE_BLUEPRINT_RESEARCH_TIME: 'UI/StructureSettings/ServiceResearch',
 SERVICE_BLUEPRINT_RESEARCH_MATERIAL: 'UI/StructureSettings/ServiceResearch',
 SERVICE_BLUEPRINT_COPYING: 'UI/StructureSettings/ServiceResearch'}
MANUFACTURING_SERVICES = [ value for name, value in SERVICES_BY_NAME.items() if name.startswith('SERVICE_MANUFACTURING_') and name != 'SERVICE_MANUFACTURING_UNKNOWN' ]
BLUEPRINT_SERVICES = [ value for name, value in SERVICES_BY_NAME.items() if name.startswith('SERVICE_BLUEPRINT_') and name != 'SERVICE_BLUEPRINT_UNKNOWN' ]
SERVICES_ACCESS_SETTINGS = {SERVICE_FITTING: structures.SETTING_HOUSING_CAN_DOCK,
 SERVICE_DOCKING: structures.SETTING_HOUSING_CAN_DOCK,
 SERVICE_REPROCESSING: structures.SETTING_REPROCESSING_TAX,
 SERVICE_MARKET: structures.SETTING_MARKET_TAX,
 SERVICE_MEDICAL: structures.SETTING_CLONINGBAY_TAX}
ONLINE_SERVICES = {SERVICE_FITTING, SERVICE_DOCKING, SERVICE_OFFICES}
SERVICE_ICONS = {SERVICE_DOCKING: 'res:/UI/Texture/classes/ProfileSettings/docking.png',
 SERVICE_FITTING: 'res:/UI/Texture/classes/ProfileSettings/fitting.png',
 SERVICE_OFFICES: 'res:/UI/Texture/classes/ProfileSettings/corpOffice.png',
 SERVICE_REPROCESSING: 'res:/UI/Texture/classes/ProfileSettings/reprocess.png',
 SERVICE_MARKET: 'res:/UI/Texture/classes/ProfileSettings/market.png',
 SERVICE_MEDICAL: 'res:/UI/Texture/classes/ProfileSettings/cloneBay.png',
 SERVICE_JUMP_CLONE: 'res:/UI/Texture/classes/ProfileSettings/cloneBay.png'}

def GetServiceID(typeID):
    return MODULES_TO_SERVICES[typeID]


def IsStructureServiceModule(typeID):
    return typeID in MODULES_TO_SERVICES


MODULES_TO_SERVICES = {inventorycommon.const.typeMarketHub: SERVICE_MARKET,
 inventorycommon.const.typeCorporationOffices: SERVICE_OFFICES,
 inventorycommon.const.typeCloningCenter: SERVICE_MEDICAL,
 inventorycommon.const.typeCorporationInsurance: SERVICE_INSURANCE,
 inventorycommon.const.typeLoyaltyPointStore: SERVICE_LOYALTY_STORE,
 inventorycommon.const.typeStandupReprocessingFacility: SERVICE_REPROCESSING}
SERVICE_STATE_ONLINE = 1
SERVICE_STATE_OFFLINE = 2
SERVICE_STATE_CLEANUP = 3
