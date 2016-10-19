#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\structureBrowser\browserUIConst.py
OWNER_ANY = 0
OWNER_NPC = 1
OWNER_CORP = 2
OWNER_ALLIANCE = 3
UI_SETTING_STRUCTUREBROWSER_SERVICEFILTERS_DISABLED = 'structurebrowser_DisableServiceFilter'
UI_SETTING_STRUCTUREBROWSER_SERVICESETTING = 'structurebrowser_%s'
UI_SETTING_STRUCTUREBROWSER_FILTERS = 'structurebrowser_filters_%s'
ALL_STRUCTURES = -1
CITADEL_MEDIUM = 0
CITADEL_LARGE = 1
CITADEL_XLARGE = 2
CITADEL_TYPEIDS = {CITADEL_MEDIUM: (35832, [35832]),
 CITADEL_LARGE: (35833, [35833]),
 CITADEL_XLARGE: (35834, [35834, 40340])}
CITADEL_GROUPING_BY_TYPEID = {x:key for key, value in CITADEL_TYPEIDS.iteritems() for x in value[1]}
ALL_PROFILES = -1
ALL_SERVICES = -1
IGNORE_RANGE = -1
