#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\squadrons\shipFighterState.py
from collections import namedtuple, defaultdict
from eve.client.script.ui.services.menuSvcExtras import movementFunctions
from fighters import ABILITY_SLOT_IDS, GetAbilityIDForSlot
from fighters.client import ConvertAbilityFailureReason
import gametime
import signals
import logging
from eve.common.script.mgt.fighterConst import TUBE_STATE_READY, TUBE_STATE_EMPTY, TUBE_STATE_LANDING, TUBE_STATE_REFUELLING
logger = logging.getLogger('ShipFighterState')
FighterInSpaceTuple = namedtuple('FighterInSpaceTuple', ['itemID',
 'typeID',
 'tubeFlagID',
 'squadronSize'])
FighterInTubeTuple = namedtuple('FighterInTubeTuple', ['itemID',
 'typeID',
 'tubeFlagID',
 'squadronSize'])
TubeStatusTuple = namedtuple('TubeStatusTuple', ['statusID', 'startTime', 'endTime'])
AbilityActivationStatusTuple = namedtuple('AbilityActivationStatusTuple', ['isPending',
 'startTime',
 'durationMs',
 'isDeactivating'])
EMPTY_TUBE = TubeStatusTuple(statusID=TUBE_STATE_EMPTY, startTime=None, endTime=None)

class ShipFighterState(object):
    __notifyevents__ = ['OnSessionChanged',
     'OnFighterTubeContentUpdate',
     'OnFighterTubeContentEmpty',
     'OnFighterAddedToController',
     'OnFighterRemovedFromController',
     'OnFighterTubeTaskStatus',
     'OnFighterAbilitySlotActivated',
     'OnFighterAbilitySlotDeactivated',
     'OnInSpaceSquadronSizeChanged',
     'OnEwarStart',
     'OnEwarEnd']
    fightersSvc = None
    fightersInLaunchTubes = None
    fightersInSpaceByID = None
    fightersInSpaceByTube = None
    statusByTube = None
    activeAbilities = None
    abilityChargeCounts = None
    abilityTargetTracker = None
    incomingEwarByFighterID = None
    signalOnFighterTubeStateUpdate = None
    signalOnFighterTubeContentUpdate = None
    signalOnFighterInSpaceUpdate = None
    signalOnAbilityActivationStatusUpdate = None
    signalOnIncomingEwarStarted = None
    signalOnIncomingEwarEnded = None

    def __init__(self, fightersSvc):
        self.fightersSvc = fightersSvc
        sm.RegisterNotify(self)
        self.fightersInLaunchTubes = {}
        self.fightersInSpaceByID = {}
        self.fightersInSpaceByTube = {}
        self.statusByTube = {}
        self.activeAbilities = {}
        self.abilityChargeCounts = {}
        self.abilityCooldowns = {}
        self.incomingEwarByFighterID = defaultdict(dict)
        self.abilityTargetTracker = AbilityTargetTracker()
        if session.shipid:
            self._UpdateStateForShip()
        self.signalOnFighterTubeStateUpdate = signals.Signal()
        self.signalOnFighterTubeContentUpdate = signals.Signal()
        self.signalOnFighterInSpaceUpdate = signals.Signal()
        self.signalOnAbilityActivationStatusUpdate = signals.Signal()
        self.signalOnIncomingEwarStarted = signals.Signal()
        self.signalOnIncomingEwarEnded = signals.Signal()

    def OnSessionChanged(self, isRemote, sess, change):
        if 'shipid' in change:
            self._UpdateStateForShip()
        if 'locationid' in change:
            for tubeFlagID, tubeStatus in self.statusByTube.iteritems():
                if self.GetFightersInTube(tubeFlagID):
                    self._SetTubeStatus(tubeFlagID, TUBE_STATE_READY, None, None)
                else:
                    self._SetTubeStatus(tubeFlagID, TUBE_STATE_EMPTY, None, None)
                self.signalOnFighterTubeStateUpdate(tubeFlagID)

            self.abilityTargetTracker.FlushAllTargets()

    def OnFighterTubeContentUpdate(self, tubeFlagID, fighterID, fighterTypeID, squadronSize):
        fighterInTube = FighterInTubeTuple(fighterID, fighterTypeID, tubeFlagID, squadronSize)
        self.fightersInLaunchTubes[tubeFlagID] = fighterInTube
        self.signalOnFighterTubeContentUpdate(tubeFlagID)

    def OnFighterTubeContentEmpty(self, tubeFlagID):
        del self.fightersInLaunchTubes[tubeFlagID]
        self.signalOnFighterTubeContentUpdate(tubeFlagID)

    def _UpdateAbilitySlotStates(self, fighterID, abilitySlotStates):
        chargeStates, cooldownStates = abilitySlotStates
        for abilitySlotID, chargeCount in chargeStates.iteritems():
            self.abilityChargeCounts[fighterID, abilitySlotID] = chargeCount

        for abilitySlotID, cooldown in cooldownStates.iteritems():
            self.abilityCooldowns[fighterID, abilitySlotID] = cooldown

    def OnFighterAddedToController(self, fighterID, fighterTypeID, tubeFlagID, squadronSize, abilitySlotStates):
        logger.debug('OnFighterAddedToController %s', (fighterID,
         fighterTypeID,
         tubeFlagID,
         squadronSize,
         abilitySlotStates))
        fighterInSpace = FighterInSpaceTuple(fighterID, fighterTypeID, tubeFlagID, squadronSize)
        self.fightersInSpaceByID[fighterID] = fighterInSpace
        self.fightersInSpaceByTube[tubeFlagID] = fighterInSpace
        self._UpdateAbilitySlotStates(fighterID, abilitySlotStates)
        self.signalOnFighterInSpaceUpdate(fighterID, tubeFlagID)

    def OnFighterRemovedFromController(self, fighterID, tubeFlagID):
        logger.debug('OnFighterRemovedFromController %s', (fighterID, tubeFlagID))
        self.fightersInSpaceByID.pop(fighterID)
        self.fightersInSpaceByTube.pop(tubeFlagID)
        self.incomingEwarByFighterID.pop(fighterID, None)
        self._DiscardActivatedAbilitiesForFighter(fighterID)
        for abilitySlotID in ABILITY_SLOT_IDS:
            self.abilityChargeCounts.pop((fighterID, abilitySlotID), None)
            self.abilityCooldowns.pop((fighterID, abilitySlotID), None)

        self.abilityTargetTracker.RemoveFighter(fighterID)
        self.signalOnFighterInSpaceUpdate(fighterID, tubeFlagID)
        if self.GetTubeStatus(tubeFlagID).statusID not in (TUBE_STATE_LANDING, TUBE_STATE_REFUELLING):
            self._SetTubeStatus(tubeFlagID, TUBE_STATE_EMPTY, None, None)
            self.signalOnFighterTubeStateUpdate(tubeFlagID)

    def _DiscardActivatedAbilitiesForFighter(self, fighterID):
        for abilitySlotID in ABILITY_SLOT_IDS:
            self.activeAbilities.pop((fighterID, abilitySlotID), None)

    def OnFighterTubeTaskStatus(self, tubeFlagID, statusID, statusStartTime, statusEndTime, userError = None):
        logger.debug('OnFighterTubeTaskStatus %s', (tubeFlagID,
         statusID,
         statusStartTime,
         statusEndTime,
         userError))
        if userError is not None:
            sm.GetService('gameui').OnRemoteMessage(*userError.args)
        self._SetTubeStatus(tubeFlagID, statusID, statusStartTime, statusEndTime)
        self.signalOnFighterTubeStateUpdate(tubeFlagID)

    def OnAbilityActivationPending(self, fighterID, abilitySlotID):
        self.activeAbilities[fighterID, abilitySlotID] = AbilityActivationStatusTuple(True, None, None, False)
        self.signalOnAbilityActivationStatusUpdate(fighterID, abilitySlotID)

    def OnFighterAbilitySlotActivated(self, fighterID, abilitySlotID, remainingChargeCount, startTime, durationMs, cooldown):
        logger.debug('OnFighterAbilitySlotActivated %s', (fighterID,
         abilitySlotID,
         remainingChargeCount,
         startTime,
         durationMs,
         cooldown))
        self.activeAbilities[fighterID, abilitySlotID] = AbilityActivationStatusTuple(False, startTime, durationMs, False)
        if remainingChargeCount is None:
            self.abilityChargeCounts.pop((fighterID, abilitySlotID), None)
        else:
            self.abilityChargeCounts[fighterID, abilitySlotID] = remainingChargeCount
        if cooldown is None:
            self.abilityCooldowns.pop((fighterID, abilitySlotID), None)
        else:
            self.abilityCooldowns[fighterID, abilitySlotID] = cooldown
        self.signalOnAbilityActivationStatusUpdate(fighterID, abilitySlotID)

    def OnAbilityDeactivationPending(self, fighterID, abilitySlotID):
        currentActivationStatus = self.activeAbilities.pop((fighterID, abilitySlotID), None)
        if currentActivationStatus:
            newActivationStatus = currentActivationStatus._replace(isDeactivating=True)
            self.activeAbilities[fighterID, abilitySlotID] = newActivationStatus
            self.signalOnAbilityActivationStatusUpdate(fighterID, abilitySlotID)

    def OnFighterAbilitySlotDeactivated(self, fighterID, abilitySlotID, failureReason):
        logger.debug('OnFighterAbilitySlotDeactivated %s', (fighterID, abilitySlotID, failureReason))
        self.activeAbilities.pop((fighterID, abilitySlotID), None)
        self.abilityTargetTracker.RemoveAbilityTarget(fighterID, abilitySlotID)
        self.signalOnAbilityActivationStatusUpdate(fighterID, abilitySlotID)
        if failureReason is not None:
            self._ShowAbilityFailureReason(fighterID, abilitySlotID, failureReason)

    def _ShowAbilityFailureReason(self, fighterID, abilitySlotID, failureReasonUserError):
        failureReasonUserError = ConvertAbilityFailureReason(fighterID, abilitySlotID, failureReasonUserError)
        sm.GetService('gameui').OnRemoteMessage(*failureReasonUserError.args)

    def OnInSpaceSquadronSizeChanged(self, fighterID, squadronSize):
        logger.debug('OnInSpaceSquadronSizeChanged %s', (fighterID, squadronSize))
        fighterInSpace = self.fightersInSpaceByID.get(fighterID, None)
        if fighterInSpace is None:
            return
        newFighterInSpace = fighterInSpace._replace(squadronSize=squadronSize)
        self.fightersInSpaceByID[fighterID] = newFighterInSpace
        self.fightersInSpaceByTube[fighterInSpace.tubeFlagID] = newFighterInSpace
        self.signalOnFighterInSpaceUpdate(fighterID, fighterInSpace.tubeFlagID)

    def _UpdateStateForShip(self):
        self.fightersInLaunchTubes.clear()
        self.fightersInSpaceByID.clear()
        self.fightersInSpaceByTube.clear()
        self.statusByTube.clear()
        self.activeAbilities.clear()
        self.abilityChargeCounts.clear()
        self.abilityCooldowns.clear()
        self.incomingEwarByFighterID.clear()
        self.abilityTargetTracker.FlushAllTargets()
        fightersInTubes, fightersInSpace = self.fightersSvc.GetFightersForShip()
        for tubeFlagID, fighterItemID, fighterTypeID, squadronSize in fightersInTubes:
            fighterInTube = FighterInTubeTuple(fighterItemID, fighterTypeID, tubeFlagID, squadronSize)
            self.fightersInLaunchTubes[tubeFlagID] = fighterInTube
            self._SetTubeStatus(tubeFlagID, TUBE_STATE_READY, None, None)
            self.signalOnFighterInSpaceUpdate(fighterItemID, tubeFlagID)

        for tubeFlagID, fighterItemID, fighterTypeID, squadronSize in fightersInSpace:
            fighterInSpace = FighterInSpaceTuple(fighterItemID, fighterTypeID, tubeFlagID, squadronSize)
            self.fightersInSpaceByID[fighterItemID] = fighterInSpace
            self.fightersInSpaceByTube[tubeFlagID] = fighterInSpace

    def _SetTubeStatus(self, tubeFlagID, statusID, startTime, endTime):
        self.statusByTube[tubeFlagID] = TubeStatusTuple(statusID=statusID, startTime=startTime, endTime=endTime)

    def GetFightersInTube(self, tubeFlagID):
        return self.fightersInLaunchTubes.get(tubeFlagID)

    def GetFightersInSpace(self, tubeFlagID):
        return self.fightersInSpaceByTube.get(tubeFlagID)

    def GetFighterInSpaceByID(self, fighterID):
        return self.fightersInSpaceByID.get(fighterID)

    def GetAllFighterIDsInSpace(self):
        return self.fightersInSpaceByID.keys()

    def GetTubeStatus(self, tubeFlagID):
        return self.statusByTube.get(tubeFlagID, EMPTY_TUBE)

    def IsMyFighterInSpace(self, itemID):
        return itemID in self.GetAllFighterIDsInSpace()

    def IsAllAbilitiesInSlotActiveOrInCooldown(self, abilitySlotID):
        for fighterID in self.GetSelectedFightersInSpace():
            if self.GetAbilityIDForSlot(fighterID, abilitySlotID) is None:
                continue
            if not self.IsAbilityActive(fighterID, abilitySlotID) and self.GetAbilityCooldown(fighterID, abilitySlotID) is None:
                return False

        return True

    def GetAbilityIDForSlot(self, fighterID, abilitySlotID):
        fighter = self.GetFighterInSpaceByID(fighterID)
        if fighter:
            return GetAbilityIDForSlot(fighter.typeID, abilitySlotID)

    def GetSelectedFightersInSpace(self):
        return movementFunctions.GetFightersSelectedForNavigation()

    def IsAbilityActive(self, fighterID, abilitySlotID):
        return (fighterID, abilitySlotID) in self.activeAbilities

    def GetAbilityChargeCount(self, fighterID, abilitySlotID):
        return self.abilityChargeCounts.get((fighterID, abilitySlotID), None)

    def GetAbilityCooldown(self, fighterID, abilitySlotID):
        cooldown = self.abilityCooldowns.get((fighterID, abilitySlotID), None)
        if cooldown is not None:
            startTime, endTime = cooldown
            if startTime <= gametime.GetSimTime() < endTime:
                return (startTime, endTime)

    def GetAbilityActivationStatus(self, fighterID, abilitySlotID):
        return self.activeAbilities.get((fighterID, abilitySlotID), None)

    def OnAbilityActivatedAtTarget(self, fighterID, abilitySlotID, targetID):
        self.abilityTargetTracker.RegisterAbilityTarget(fighterID, abilitySlotID, targetID)

    def GetAbilityTargetsForFighter(self, fighterID):
        return self.abilityTargetTracker.GetAbilityTargetsForFighter(fighterID)

    def ConnectFighterTargetUpdatedHandler(self, handler):
        return self.abilityTargetTracker.signalOnAbilityTargetsUpdate.connect(handler)

    def DisconnectFighterTargetUpdatedHandler(self, handler):
        return self.abilityTargetTracker.signalOnAbilityTargetsUpdate.disconnect(handler)

    def OnEwarStart(self, sourceBallID, sourceModuleID, targetBallID, jammingType):
        if targetBallID not in self.fightersInSpaceByID:
            return
        logger.debug('ShipFighterState.OnEwarStart %s', (sourceBallID,
         sourceModuleID,
         targetBallID,
         jammingType))
        self.incomingEwarByFighterID[targetBallID][sourceModuleID] = (sourceBallID, jammingType)
        self.signalOnIncomingEwarStarted(targetBallID, sourceBallID, sourceModuleID, jammingType)

    def OnEwarEnd(self, sourceBallID, sourceModuleID, targetBallID, jammingType):
        fighterEwar = self.incomingEwarByFighterID.get(targetBallID, None)
        if fighterEwar is None:
            return
        ewar = fighterEwar.pop(sourceModuleID, None)
        if ewar is None:
            return
        logger.debug('ShipFighterState.OnEwarEnd %s', (sourceBallID,
         sourceModuleID,
         targetBallID,
         jammingType))
        self.signalOnIncomingEwarEnded(targetBallID, sourceBallID, sourceModuleID, jammingType)

    def GetIncomingFighterEwar(self, fighterID):
        ewarByModuleID = self.incomingEwarByFighterID.get(fighterID, None)
        if ewarByModuleID is None:
            return []
        return [ (sourceModuleID, sourceBallID, jammingType) for sourceModuleID, (sourceBallID, jammingType) in ewarByModuleID.iteritems() ]


class AbilityTargetTracker(object):
    targetsByFighterSlot = None
    signalOnAbilityTargetsUpdate = None

    def __init__(self):
        self.targetsByFighterSlot = defaultdict(dict)
        self.signalOnAbilityTargetsUpdate = signals.Signal()

    def RegisterAbilityTarget(self, fighterID, abilitySlotID, targetID):
        self.targetsByFighterSlot[fighterID][abilitySlotID] = targetID
        self.signalOnAbilityTargetsUpdate(fighterID, abilitySlotID, targetID)

    def GetAbilityTargetsForFighter(self, fighterID):
        return set(self.targetsByFighterSlot.get(fighterID, {}).itervalues())

    def GetFighterAbilitiesForTarget(self, targetID):
        abilitiesOnTarget = []
        for fighterID, fighterAbilities in self.targetsByFighterSlot.iteritems():
            for abilitySlotID, abilityTargetID in fighterAbilities.iteritems():
                if abilityTargetID == targetID:
                    abilitiesOnTarget.append((fighterID, abilitySlotID))

        return abilitiesOnTarget

    def RemoveFighter(self, fighterID):
        fighterAbilities = self.targetsByFighterSlot.pop(fighterID, None)
        if fighterAbilities:
            for abilitySlotID, targetID in fighterAbilities.iteritems():
                self.signalOnAbilityTargetsUpdate(fighterID, abilitySlotID, targetID)

    def RemoveAbilityTarget(self, fighterID, abilitySlotID):
        fighterAbilities = self.targetsByFighterSlot.get(fighterID, None)
        if fighterAbilities:
            targetID = fighterAbilities.pop(abilitySlotID, None)
            if targetID:
                self.signalOnAbilityTargetsUpdate(fighterID, abilitySlotID, targetID)

    def FlushAllTargets(self):
        for fighterID in self.targetsByFighterSlot.keys():
            self.RemoveFighter(fighterID)


def GetShipFighterState():
    return sm.GetService('fighters').shipFighterState
