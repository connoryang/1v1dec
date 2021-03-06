#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\perception.py
import collections
PERCEPTION_EDITOR_NAME = 'Perception Editor'
PERCEPTION_SCHEMA = 'zperception'
_PERCEPTION_PREFIX = PERCEPTION_SCHEMA + '.'
PERCEPTION_SENSES_TABLE_NAME = 'senses'
PERCEPTION_SENSES_TABLE_FULL_PATH = _PERCEPTION_PREFIX + PERCEPTION_SENSES_TABLE_NAME
PERCEPTION_STIMTYPES_TABLE_NAME = 'stimTypes'
PERCEPTION_STIMTYPES_TABLE_FULL_PATH = _PERCEPTION_PREFIX + PERCEPTION_STIMTYPES_TABLE_NAME
PERCEPTION_SUBJECTS_TABLE_NAME = 'subjects'
PERCEPTION_SUBJECTS_TABLE_FULL_PATH = _PERCEPTION_PREFIX + PERCEPTION_SUBJECTS_TABLE_NAME
PERCEPTION_TARGETS_TABLE_NAME = 'targets'
PERCEPTION_TARGETS_TABLE_FULL_PATH = _PERCEPTION_PREFIX + PERCEPTION_TARGETS_TABLE_NAME
PERCEPTION_SENSE_GROUPS_TABLE_NAME = 'senseGroups'
PERCEPTION_SENSE_GROUPS_TABLE_FULL_PATH = _PERCEPTION_PREFIX + PERCEPTION_SENSE_GROUPS_TABLE_NAME
PERCEPTION_FILTER_GROUPS_TABLE_NAME = 'filterGroups'
PERCEPTION_FILTER_GROUPS_TABLE_FULL_PATH = _PERCEPTION_PREFIX + PERCEPTION_FILTER_GROUPS_TABLE_NAME
PERCEPTION_DECAY_GROUPS_TABLE_NAME = 'decayGroups'
PERCEPTION_DECAY_GROUPS_TABLE_FULL_PATH = _PERCEPTION_PREFIX + PERCEPTION_DECAY_GROUPS_TABLE_NAME
PERCEPTION_BEHAVIOR_SENSES_TABLE_NAME = 'behaviorSenses'
PERCEPTION_BEHAVIOR_SENSES_TABLE_FULL_PATH = _PERCEPTION_PREFIX + PERCEPTION_BEHAVIOR_SENSES_TABLE_NAME
PERCEPTION_BEHAVIOR_FILTERS_TABLE_NAME = 'behaviorFilters'
PERCEPTION_BEHAVIOR_FILTERS_TABLE_FULL_PATH = _PERCEPTION_PREFIX + PERCEPTION_BEHAVIOR_FILTERS_TABLE_NAME
PERCEPTION_BEHAVIOR_DECAYS_TABLE_NAME = 'behaviorDecays'
PERCEPTION_BEHAVIOR_DECAYS_TABLE_FULL_PATH = _PERCEPTION_PREFIX + PERCEPTION_BEHAVIOR_DECAYS_TABLE_NAME
SELECT_PERCEPTION_SENSE = 'SelectPerceptionSense'
SELECT_PERCEPTION_STIMTYPE = 'SelectPerceptionStimType'
SELECT_PERCEPTION_SUBJECT = 'SelectPerceptionSubject'
SELECT_PERCEPTION_TARGET = 'SelectPerceptionTarget'
SELECT_PERCEPTION_SENSE_GROUP = 'SelectPerceptionSenseGroup'
SELECT_PERCEPTION_FILTER_GROUP = 'SelectPerceptionFilterGroup'
SELECT_PERCEPTION_DECAY_GROUP = 'SelectPerceptionDecayGroup'
SELECT_PERCEPTION_BEHAVIOR_SENSE = 'SelectPerceptionBehaviorSense'
SELECT_PERCEPTION_BEHAVIOR_FILTER = 'SelectPerceptionBehaviorFilter'
SELECT_PERCEPTION_BEHAVIOR_DECAY = 'SelectPerceptionBehaviorDecay'
PERCEPTION_SENSE_LOS_VALUES = {0: 'LOS',
 1: 'NLOS'}
PERCEPTION_STIMTYPE_CREATEFLAG_VALUES = {0: 'Once',
 1: 'OnTick'}
PERCEPTION_ENTITY_TYPE_PC = 'PC'
PERCEPTION_ENTITY_TYPE_NPC = 'NPC'
PERCEPTION_ENTITY_TYPE_OBJECT = 'OBJECT'
PERCEPTION_ENTITY_PC_TYPEID = 1
PERCEPTION_ENTITY_NPC_TYPEID = 2
PERCEPTION_ENTITY_OBJECT_TYPEID = 3
PERCEPTION_ENTITY_TYPE_TO_ID = {PERCEPTION_ENTITY_TYPE_PC: PERCEPTION_ENTITY_PC_TYPEID,
 PERCEPTION_ENTITY_TYPE_NPC: PERCEPTION_ENTITY_NPC_TYPEID,
 PERCEPTION_ENTITY_TYPE_OBJECT: PERCEPTION_ENTITY_OBJECT_TYPEID}
PERCEPTION_CONFIDENCE_VALUE_TYPE = collections.namedtuple('PERCEPTION_CONFIDENCE_VALUE_TYPE', 'confidenceID, confidenceName')
PERCEPTION_CONFIDENCE_VALUES = [PERCEPTION_CONFIDENCE_VALUE_TYPE(confidenceID=1, confidenceName='Highest'),
 PERCEPTION_CONFIDENCE_VALUE_TYPE(confidenceID=2, confidenceName='High'),
 PERCEPTION_CONFIDENCE_VALUE_TYPE(confidenceID=3, confidenceName='Average'),
 PERCEPTION_CONFIDENCE_VALUE_TYPE(confidenceID=4, confidenceName='Low'),
 PERCEPTION_CONFIDENCE_VALUE_TYPE(confidenceID=5, confidenceName='Lowest')]
PERCEPTION_CONFIDENCE_DICT = {1: PERCEPTION_CONFIDENCE_VALUES[0],
 2: PERCEPTION_CONFIDENCE_VALUES[1],
 3: PERCEPTION_CONFIDENCE_VALUES[2],
 4: PERCEPTION_CONFIDENCE_VALUES[3],
 5: PERCEPTION_CONFIDENCE_VALUES[4]}
PERCEPTION_CLIENTSERVER_FLAG_CLIENT = 1
PERCEPTION_CLIENTSERVER_FLAG_SERVER = 2
PERCEPTION_CLIENTSERVER_FLAG_BOTH = PERCEPTION_CLIENTSERVER_FLAG_CLIENT | PERCEPTION_CLIENTSERVER_FLAG_SERVER
PERCEPTION_CLIENTSERVER_FLAGS = {PERCEPTION_CLIENTSERVER_FLAG_CLIENT: 'Client only',
 PERCEPTION_CLIENTSERVER_FLAG_SERVER: 'Server only',
 PERCEPTION_CLIENTSERVER_FLAG_BOTH: 'Client and Server'}
PERCEPTION_COMPONENT_ENTITY_TYPE = 'entityType'
PERCEPTION_COMPONENT_SENSE_GROUP = 'behaviorSensesID'
PERCEPTION_COMPONENT_FILTER_GROUP = 'behaviorFiltersID'
PERCEPTION_COMPONENT_DECAY_GROUP = 'behaviorDecaysID'
PERCEPTION_COMPONENT_SENSOR_BONENAME = 'sensorBoneName'
PERCEPTION_COMPONENT_SENSOR_OFFSET = 'sensorOffset'
PERCEPTION_COMPONENT_DROP_STIMTYPE = 'dropStimType'
PERCEPTION_COMPONENT_DROP_RANGE = 'dropStimRange'
PERCEPTION_COMPONENT_TAGS = 'tags'
PERCEPTION_COMPONENT_CLIENTSERVER = 'clientServer'
PERCEPTION_PROCEDURAL_TAGS = ('FRIEND', '~FRIEND')
