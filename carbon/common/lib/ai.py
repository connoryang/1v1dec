#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\ai.py
AI_SCHEMA = 'zai'
_AI_PREFIX = AI_SCHEMA + '.'
DECISION_NODE_TYPES = DECISION_NODE_NONE, DECISION_NODE_ROOT, DECISION_NODE_IF, DECISION_NODE_TASK = [None] + range(3)
DECISON_NODE_TYPE_NAMES = {DECISION_NODE_NONE: '<NONE>',
 DECISION_NODE_ROOT: 'root node',
 DECISION_NODE_IF: 'if node',
 DECISION_NODE_TASK: 'task node'}
PRIORITY_DEFAULT_VALUE = 0
DECISION_BRAIN_INDEX = 0
DECISION_HATE_INDEX = 1
DECISION_MAX_INSTANCES = 2
DECISION_TYPE_NAMES = ['Brain', 'Hate']
