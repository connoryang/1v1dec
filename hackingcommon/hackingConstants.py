#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\hackingcommon\hackingConstants.py
GAMETYPE_HACKING = 0
GAMETYPE_ARCHEOLOGY = 1
GAMETYPE_MULTICORE = 2
TYPE_NONE = -1
TYPE_SEGMENT = 0
TYPE_VIRUS = 1
TYPE_CORE = 2
TYPE_DEFENSESOFTWARE = 3
TYPE_UTILITYELEMENT = 4
TYPE_UTILITYELEMENTTILE = 5
TYPE_DATACACHE = 6
SUBTYPE_NONE = -1
SUBTYPE_UE_SELFREPAIR = 0
SUBTYPE_UE_KERNALROT = 1
SUBTYPE_UE_SECONDARYVECTOR = 2
SUBTYPE_UE_POLYMORPHICSHIELD = 3
UE_SUBTYPES_APPLIED_TO_VIRUS = (SUBTYPE_UE_SELFREPAIR, SUBTYPE_UE_POLYMORPHICSHIELD)
UE_SUBTYPES_APPLIED_TO_TARGET = (SUBTYPE_UE_KERNALROT, SUBTYPE_UE_SECONDARYVECTOR)
SUBTYPE_CORE_HIGH = 10
SUBTYPE_CORE_LOW = 11
SUBTYPE_CORE_MEDIUM = 12
SUBTYPE_DS_ANTIVIRUS = 100
SUBTYPE_DS_FIREWALL = 101
SUBTYPE_DS_HONEYPOT_STRENGTH = 102
SUBTYPE_DS_HONEYPOT_HEALING = 103
SUBTYPE_DS_DISRUPTOR = 104
SUBTYPE_DS_IDS = 200
SUBTYPE_DS_BITCHINATOR = 300
SUBTYPE_DS_DELETER = 301
SUBTYPE_DS_FLYTRAP = 302
SUBTYPE_DS_MARCHINGCUBES = 303
SUBTYPE_DS_REPLICATOR = 304
SUBTYPE_DS_RESETTER = 305
EVENT_NONE = -1
EVENT_GAME_LOST = 0
EVENT_GAME_WON = 1
EVENT_GAME_START = 2
EVENT_VIRUS_CREATED = 3
EVENT_OBJECT_KILLED = 4
EVENT_GAME_STYLE = 5
EVENT_ACK = 6
EVENT_TILE_FLIPPED = 100
EVENT_TILE_CREATED = 101
EVENT_TILE_BLOCKED = 102
EVENT_TILE_REACHABLE = 103
EVENT_UE_PICKEDUP = 200
EVENT_UE_REMOVED = 201
EVENT_UE_INUSE = 202
EVENT_DATACACHE_OPEN = 300
EVENT_ATTACK = 301
EVENT_KERNALROT = 302
EVENT_SELFREPAIR = 303
EVENT_SECONDARYVECTOR = 304
EVENT_POLYMORPHICSHIELDHIT = 305
EVENT_HONEYPOT_STRENGTH = 306
EVENT_HONEYPOT_HEALING = 307
EVENT_DISTANCEINDICATOR = 308
EVENT_CORE_CONTENTS = 400
EVENT_UNLOCK_CORE_CONTENTS = 401
UE_NOTUSED = 0
UE_DESTROYED = 1
UE_INUSE = 2
OFF_GRID_COORDINATE = (-1, -1)
hackingStateSecure = 0
hackingStateBeingHacked = 1
hackingStateHacked = 2
