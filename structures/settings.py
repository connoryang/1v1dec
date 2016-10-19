#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\structures\settings.py
CATEGORY_HULL_DEFENSE = 1003
CATEGORY_HULL_DOCKING = 1004
CATEGORY_MODULE_MARKET = 1008
CATEGORY_HULL_CORPOFFICE = 1009
CATEGORY_MODULE_REPROCESSING = 1010
CATEGORY_MODULE_CLONINGBAY = 1011
SETTING_REPROCESSING_TAX = 3
SETTING_MARKET_TAX = 4
SETTING_DEFENSE_CAN_CONTROL_STRUCTURE = 17
SETTING_HOUSING_CAN_DOCK = 19
SETTING_CORP_RENT_OFFICE = 20
SETTING_CLONINGBAY_TAX = 23
CATEGORIES_BY_NAME = {name:value for name, value in locals().items() if name.startswith('CATEGORY_')}
SETTINGS_BY_NAME = {name:value for name, value in locals().items() if name.startswith('SETTING_')}
SETTINGS_TYPE_NONE = 1
SETTINGS_TYPE_BOOL = 2
SETTINGS_TYPE_INT = 3
SETTINGS_TYPE_FLOAT = 4
SETTINGS_TYPE_PERCENTAGE = 5
SETTINGS_TYPE_ISK = 6
SETTINGS_BY_CATEGORY = {CATEGORY_HULL_DEFENSE: (SETTING_DEFENSE_CAN_CONTROL_STRUCTURE,),
 CATEGORY_HULL_DOCKING: (SETTING_HOUSING_CAN_DOCK,),
 CATEGORY_HULL_CORPOFFICE: (SETTING_CORP_RENT_OFFICE,),
 CATEGORY_MODULE_MARKET: (SETTING_MARKET_TAX,),
 CATEGORY_MODULE_CLONINGBAY: (SETTING_CLONINGBAY_TAX,),
 CATEGORY_MODULE_REPROCESSING: (SETTING_REPROCESSING_TAX,)}
CATEGORY_LABELS = {CATEGORY_HULL_DEFENSE: 'UI/StructureSettings/ServiceDefense',
 CATEGORY_HULL_DOCKING: 'UI/StructureSettings/ServiceDocking',
 CATEGORY_HULL_CORPOFFICE: 'UI/StructureSettings/ServiceCorpOffices',
 CATEGORY_MODULE_MARKET: 'UI/StructureSettings/ServiceMarket',
 CATEGORY_MODULE_CLONINGBAY: 'UI/StructureSettings/ServiceCloneBay',
 CATEGORY_MODULE_REPROCESSING: 'UI/StructureSettings/ServiceReprocessing'}
CATEGORY_TEXTURES = {CATEGORY_HULL_DEFENSE: 'res:/UI/Texture/classes/ProfileSettings/defense.png',
 CATEGORY_HULL_DOCKING: 'res:/UI/Texture/classes/ProfileSettings/docking.png',
 CATEGORY_HULL_CORPOFFICE: 'res:/UI/Texture/classes/ProfileSettings/corpOffice.png',
 CATEGORY_MODULE_MARKET: 'res:/UI/Texture/classes/ProfileSettings/market.png',
 CATEGORY_MODULE_CLONINGBAY: 'res:/UI/Texture/classes/ProfileSettings/cloneBay.png',
 CATEGORY_MODULE_REPROCESSING: 'res:/UI/Texture/classes/ProfileSettings/reprocess.png'}

class StructureSettingObject(object):

    def __init__(self, settingID, labelPath, descLabelPath, cantAccessError, valueType, hasGroups, valueRange = None, columnLabelPath = None):
        self.settingID = settingID
        self.labelPath = labelPath
        self.descLabelPath = descLabelPath
        self.cantAccessError = cantAccessError
        self.valueType = valueType
        self.hasGroups = hasGroups
        self.valueRange = valueRange
        self.columnLabelPath = columnLabelPath


MAX_CLONEBAY_COST = 100000000
MAX_CORPOFFICE_COST = 1000000000
MAX_TAX_PERCENTAGE = 50
ALL_SETTING_OBJECTS = [StructureSettingObject(SETTING_MARKET_TAX, 'UI/StructureSettings/MarketTax', 'UI/StructureSettings/SpecifyAllowedGroupsAndRate', 'StructureMarketDenied', SETTINGS_TYPE_PERCENTAGE, hasGroups=True, valueRange=(0, MAX_TAX_PERCENTAGE)),
 StructureSettingObject(SETTING_DEFENSE_CAN_CONTROL_STRUCTURE, 'UI/StructureSettings/CanControlStructure', 'UI/StructureSettings/CanControlStructureDesc', 'StructureDefenseDenied', SETTINGS_TYPE_NONE, hasGroups=True),
 StructureSettingObject(SETTING_HOUSING_CAN_DOCK, 'UI/StructureSettings/DockingAccess', 'UI/StructureSettings/DockingAccessDesc', 'StructureDockingDenied', SETTINGS_TYPE_NONE, hasGroups=True),
 StructureSettingObject(SETTING_CORP_RENT_OFFICE, 'UI/StructureSettings/CorpOffice', 'UI/StructureSettings/CorpOfficeDesc', 'StructureCorpOfficesDenied', SETTINGS_TYPE_ISK, hasGroups=True, valueRange=(0, MAX_CORPOFFICE_COST)),
 StructureSettingObject(SETTING_CLONINGBAY_TAX, 'UI/StructureSettings/CloneBayTax', 'UI/StructureSettings/CloneBayTaxDesc', 'StructureCloneBayDenied', SETTINGS_TYPE_ISK, hasGroups=True, valueRange=(0, MAX_CLONEBAY_COST)),
 StructureSettingObject(SETTING_REPROCESSING_TAX, 'UI/StructureSettings/ReprocessingTax', 'UI/StructureSettings/ReprocessingTaxDesc', 'StructureReprocessingDenied', SETTINGS_TYPE_PERCENTAGE, hasGroups=True, valueRange=(0, MAX_TAX_PERCENTAGE))]
CATEGORIES_HULL = [ value for name, value in CATEGORIES_BY_NAME.iteritems() if name.startswith('CATEGORY_HULL_') ]
CATEGORIES_MODULES = [ value for name, value in CATEGORIES_BY_NAME.iteritems() if name.startswith('CATEGORY_MODULE_') ]
SETTINGS_NAMES = {value:name for name, value in SETTINGS_BY_NAME.iteritems()}
SETTINGS_CATEGORY = {setting:service for service, settings in SETTINGS_BY_CATEGORY.iteritems() for setting in settings}
SETTING_OBJECT_BY_SETTINGID = {s.settingID:s for s in ALL_SETTING_OBJECTS}
SETTINGS_VALUE_HAS_GROUPS = [ s.settingID for s in ALL_SETTING_OBJECTS if s.hasGroups ]
SETTINGS_VALUE_TYPE = {s.settingID:s.valueType for s in ALL_SETTING_OBJECTS}
SETTINGS_LABELS = {s.settingID:s.labelPath for s in ALL_SETTING_OBJECTS}
SETTINGS_LABELS_DESC = {s.settingID:s.descLabelPath for s in ALL_SETTING_OBJECTS}
SETTING_ACCESS_ERRORS_BY_SETTING = {s.settingID:s.cantAccessError for s in ALL_SETTING_OBJECTS}
SETTINGS = tuple(SETTINGS_BY_NAME.values())

def GetAccessErrorLabel(settingID):
    return SETTING_ACCESS_ERRORS_BY_SETTING.get(settingID, 'StructureGenericSettingDenied')
