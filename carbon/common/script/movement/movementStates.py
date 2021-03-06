#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\movement\movementStates.py
import GameWorld
import math
import blue
import yaml
import log
STATIC_MOVEMENT_STATES_FILE = 'res:/Animation/movementStates.yaml'

def BuildRotationRange(degrees, tolerance):
    radians = math.pi * degrees / 180.0
    rotRange = math.pi * tolerance / 180.0
    rotLow = radians - rotRange
    if rotLow < 0:
        rotLow += 2 * math.pi
    rotHigh = radians + rotRange
    if rotHigh > 2 * math.pi:
        rotHigh -= 2 * math.pi
    return (rotLow, rotHigh)


class MovementStates:
    __guid__ = 'movement.MovementStates'

    def __init__(self):
        self.metaStates = []
        self.LoadStates()

    def LoadStates(self):
        self.LoadStaticStatesFromYAML()
        self.ConvertKeyStates()
        self.DefineMetaStates()
        metaIndex = 0
        for metaState in self.metaStates:
            staticStates = metaState.get(const.movement.METASTATE_STATIC_STATES, None)
            if staticStates is not None:
                GameWorld.GetPDMManagerSingleton().SetStaticStates(metaIndex, *staticStates)
                staticIndex = 0
                for staticState in staticStates:
                    transitionList = staticState.get(const.movement.STATICSTATE_TRANSITIONS, None)
                    if transitionList is not None:
                        GameWorld.GetPDMManagerSingleton().SetTransitions(metaIndex, staticIndex, *transitionList)
                    staticIndex += 1

            metaIndex += 1

    def LoadStaticStatesFromYAML(self):
        stateFile = blue.ResFile()
        stateFile.Open(STATIC_MOVEMENT_STATES_FILE)
        self.metaStates = yaml.load(stateFile, Loader=yaml.CLoader)
        stateFile.close()
        metaIndex = 0
        for metaState in self.metaStates:
            metaState[const.movement.METASTATE_STATIC_STATE_MAPPING] = {}
            metaState[const.movement.METASTATE_INDEX] = metaIndex
            metaState[const.movement.METASTATE_ENABLED] = metaState.get(const.movement.METASTATE_STARTS_ENABLED, True)
            index = 0
            for staticState in metaState.get(const.movement.METASTATE_STATIC_STATES, []):
                metaState[const.movement.METASTATE_STATIC_STATE_MAPPING][staticState[const.movement.STATICSTATE_NAME]] = index
                index += 1
                for transition in staticState.get(const.movement.STATICSTATE_TRANSITIONS, []):
                    transition.setdefault(const.movement.TRANSITION_FROM_STATE, None)
                    transition.setdefault(const.movement.TRANSITION_BLEND_TIME, 0.0)
                    transition.setdefault(const.movement.TRANSITION_MAX_INTERRUPT_PERCENT, 1.0)
                    transition.setdefault(const.movement.TRANSITION_EXEC_ROTATION, 0.0)
                    transition[const.movement.TRANSITION_EXEC_ROTATION] = math.pi * transition[const.movement.TRANSITION_EXEC_ROTATION] / 180.0
                    if transition.get(const.movement.TRANSITION_TARGET_ROTATION, None) is not None and transition.get(const.movement.TRANSITION_TOLERANCE, None):
                        transition[const.movement.TRANSITION_ROTATION_RANGE] = BuildRotationRange(transition[const.movement.TRANSITION_TARGET_ROTATION], transition[const.movement.TRANSITION_TOLERANCE])
                    else:
                        transition[const.movement.TRANSITION_ROTATION_RANGE] = None

            for staticState in metaState.get(const.movement.METASTATE_STATIC_STATES, []):
                for transition in staticState.get(const.movement.STATICSTATE_TRANSITIONS, []):
                    if transition[const.movement.TRANSITION_FROM_STATE] is not None:
                        transition[const.movement.TRANSITION_FROM_STATE] = metaState[const.movement.METASTATE_STATIC_STATE_MAPPING][transition[const.movement.TRANSITION_FROM_STATE]]

                chainTo = staticState.get(const.movement.METASTATE_CHAIN_TO, None)
                if chainTo is not None:
                    chainMeta = metaIndex
                    chainStatic = -1
                    if ':' in chainTo:
                        keys = chainTo.split(':')
                        chainMeta = self.FindMetaStateIndex(keys[0])
                        chainStatic = self.FindStaticStateIndex(chainMeta, keys[1])
                    else:
                        chainStatic = self.FindStaticStateIndex(chainMeta, chainTo)
                    if chainMeta != -1 and chainStatic != -1:
                        staticState[const.movement.METASTATE_CHAIN_TO_METAINDEX] = chainMeta
                        staticState[const.movement.METASTATE_CHAIN_TO_STATICINDEX] = chainStatic

            metaIndex += 1

    def ConvertKeyStates(self):
        for metaState in self.metaStates:
            metaState[const.movement.METASTATE_KEYMAP] = {}
            for x in (0, 1, -1):
                for z in (0, 1, -1):
                    for m in (0, 1):
                        metaState[const.movement.METASTATE_KEYMAP][x, z, m] = 0

            if const.movement.METASTATE_KEYMAPLIST in metaState:
                for keymap in metaState[const.movement.METASTATE_KEYMAPLIST]:
                    if const.movement.KEYMAP_INPUT in keymap and const.movement.KEYMAP_STATE in keymap:
                        stateIndex = metaState[const.movement.METASTATE_STATIC_STATE_MAPPING][keymap[const.movement.KEYMAP_STATE]]
                        hashTuple = tuple(keymap[const.movement.KEYMAP_INPUT])
                        metaState[const.movement.METASTATE_KEYMAP][hashTuple] = stateIndex

    def DefineMetaStates(self):
        pass

    def FindMetaStateIndex(self, name):
        index = 0
        for metaState in self.metaStates:
            if name == metaState[const.movement.METASTATE_NAME]:
                return index
            index += 1

        return -1

    def FindStaticStateIndex(self, metaIndex, name):
        index = 0
        for staticState in self.metaStates[metaIndex].get(const.movement.METASTATE_STATIC_STATES, []):
            if name == staticState[const.movement.STATICSTATE_NAME]:
                return index
            index += 1

        return -1

    def CheckPreconditions(self, ent, metastate):
        if metastate.get('precondProc', None) is None:
            return True
        for condition in metastate['precondProc']:
            if False == condition(ent):
                return False

        return True

    def FindCurrentMetaState(self, ent):
        metaStateIndex = len(self.metaStates) - 1
        metaState = None
        while metaStateIndex >= 0:
            metaState = self.metaStates[metaStateIndex]
            if metaState[const.movement.METASTATE_ENABLED]:
                if self.CheckPreconditions(ent, metaState):
                    return metaStateIndex
            metaStateIndex -= 1

        log.LogError('ERROR: NO valid Movement metastate found!')
        self.metaState = None
        return -1
