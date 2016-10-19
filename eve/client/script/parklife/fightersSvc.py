#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\parklife\fightersSvc.py
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import ROLE_GML
from eve.client.script.parklife import states
from eve.client.script.ui.inflight.squadrons.fighterDebugWindow import FighterDebugWindow
from eve.client.script.ui.services.menuSvcExtras import movementFunctions
from eveexceptions import UserError
from fighters.abilityAttributes import GetDogmaEffectIDForAbilityID
from carbonui.const import YESNO, ID_YES
import geo2
from eve.client.script.ui.inflight.squadrons.shipFighterState import ShipFighterState
from eve.common.script.mgt import fighterConst
from eve.common.script.mgt.fighterConst import TUBE_STATE_RECALLING, TUBE_STATE_INSPACE, TUBE_STATE_READY
import evetypes
from fighters import GetAbilityIDForSlot, GetAbilityNameIDForSlot, DEFAULT_CONTROLLER_ORBIT_DISTANCE
from inventorycommon.const import categoryFighter
import carbonui.const as uiconst

class FightersSvc(Service):
    __dependencies__ = ['michelle', 'consider', 'crimewatchSvc']
    __guid__ = 'svc.fighters'
    __servicename__ = 'fighters'
    __displayname__ = 'Fighters service'
    __neocommenuitem__ = (('Fighter debugger', None), 'ShowDebugWindow', ROLE_GML)
    __notifyevents__ = ['OnStateChange']
    shipFighterState = None

    def Run(self, memStream = None):
        self.LogInfo('Starting fighters service')
        self.shipFighterState = ShipFighterState(self)

    def ShowDebugWindow(self):
        wnd = FighterDebugWindow.GetIfOpen()
        if wnd:
            wnd.Maximize()
        else:
            FighterDebugWindow.Open()

    def FightersMenu(self):

        def SpawnFighterInBay(fighterTypeID):
            self.LogInfo('Spawning fighter via /fit', fighterTypeID, evetypes.GetEnglishName(fighterTypeID))
            sm.RemoteSvc('slash').SlashCmd('/fit me %d %d' % (fighterTypeID, 1))

        groupMenu = []
        for fighterGroupID in evetypes.GetGroupIDsByCategory(categoryFighter):
            groupName = evetypes.GetGroupNameByGroup(fighterGroupID)
            typeMenu = []
            for fighterTypeID in evetypes.GetTypeIDsByGroup(fighterGroupID):
                fighterName = evetypes.GetEnglishName(fighterTypeID)
                typeMenu.append((fighterName, SpawnFighterInBay, (fighterTypeID,)))

            typeMenu.sort()
            groupMenu.append((groupName, typeMenu))

        groupMenu.sort()
        return [('NEW FIGHTERS', groupMenu)]

    def CmdReturnAndOrbit(self, fighterIDs):
        self.CmdMovementOrbit(fighterIDs, session.shipid, DEFAULT_CONTROLLER_ORBIT_DISTANCE)

    def CmdMovementOrbit(self, fighterIDs, targetID, followRange):
        self._ExecuteMovementCommandOnFighters(fighterConst.MOVEMENT_COMMAND_ORBIT, fighterIDs, targetID, followRange)

    def CmdMovementFollow(self, fighterIDs, targetID, followRange):
        self._ExecuteMovementCommandOnFighters(fighterConst.MOVEMENT_COMMAND_FOLLOW, fighterIDs, targetID, followRange)

    def CmdMovementStop(self, fighterIDs):
        self._ExecuteMovementCommandOnFighters(fighterConst.MOVEMENT_COMMAND_STOP, fighterIDs)

    def CmdGotoPoint(self, fighterIDs, point):
        self._ExecuteMovementCommandOnFighters(fighterConst.MOVEMENT_COMMAND_GOTO_POINT, fighterIDs, point)

    def _ExecuteMovementCommandOnFighters(self, command, fighterIDs, *args, **kwargs):
        if fighterIDs:
            sm.RemoteSvc('fighterMgr').ExecuteMovementCommandOnFighters(fighterIDs, command, *args, **kwargs)

    def GetFightersForShip(self):
        return sm.RemoteSvc('fighterMgr').GetFightersForShip()

    def LoadFightersToTube(self, fighterID, tubeFlagID):
        return sm.RemoteSvc('fighterMgr').LoadFightersToTube(fighterID, tubeFlagID)

    def UnloadTubeToFighterBay(self, tubeFlagID):
        fighterInTube = self.shipFighterState.GetFightersInTube(tubeFlagID)
        if fighterInTube is not None:
            return sm.RemoteSvc('fighterMgr').UnloadTubeToFighterBay(tubeFlagID)

    def LaunchFightersFromTubes(self, tubeFlagIDs):
        tubeFlagIDs = [ tubeFlagID for tubeFlagID in tubeFlagIDs if self.shipFighterState.GetTubeStatus(tubeFlagID).statusID == TUBE_STATE_READY ]
        if not tubeFlagIDs:
            return
        errorsByTubeID = sm.RemoteSvc('fighterMgr').LaunchFightersFromTubes(tubeFlagIDs)
        for tubeID, error in errorsByTubeID.iteritems():
            if error:
                sm.GetService('gameui').OnRemoteMessage(*error.args)

    def RecallFightersToTubes(self, fighterIDs):
        fighterTubesByID = {}
        for fighterID in fighterIDs:
            fighterInSpace = self.shipFighterState.GetFighterInSpaceByID(fighterID)
            if fighterInSpace is None:
                continue
            tubeStatus = self.shipFighterState.GetTubeStatus(fighterInSpace.tubeFlagID)
            if tubeStatus.statusID != TUBE_STATE_INSPACE:
                continue
            fighterTubesByID[fighterID] = fighterInSpace.tubeFlagID

        if not fighterTubesByID:
            return
        errorsByFighterID = sm.RemoteSvc('fighterMgr').RecallFightersToTubes(fighterTubesByID.keys())
        for fighterID, error in errorsByFighterID.iteritems():
            if error:
                sm.GetService('gameui').OnRemoteMessage(*error.args)
            else:
                tubeFlagID = fighterTubesByID[fighterID]
                self.shipFighterState.OnFighterTubeTaskStatus(tubeFlagID, TUBE_STATE_RECALLING, None, None)

    def _CheckSafetyLevelForAbility(self, fighterID, abilitySlotID, targetID = None):
        fighterInSpace = self.shipFighterState.GetFighterInSpaceByID(fighterID)
        if fighterInSpace is None:
            raise ValueError('Cannot activate ability for unknown fighter')
        abilityID = GetAbilityIDForSlot(fighterInSpace.typeID, abilitySlotID)
        effectID = GetDogmaEffectIDForAbilityID(abilityID)
        effect = cfg.dgmeffects.Get(effectID)
        requiredSafetyLevel = self.crimewatchSvc.GetRequiredSafetyLevelForEffect(effect, targetID)
        if not self.consider.SafetyCheckPasses(requiredSafetyLevel):
            abilityNameID = GetAbilityNameIDForSlot(fighterInSpace.typeID, abilitySlotID)
            raise UserError('CannotActivateAbilityViolatesSafety', {'fighterTypeID': fighterInSpace.typeID,
             'abilityNameID': abilityNameID})

    def ActivateAbilitySlotsOnTarget(self, fighterIDs, abilitySlotID, targetID):
        if not targetID:
            fighterInSpace = self.shipFighterState.GetFighterInSpaceByID(fighterIDs[0])
            abilityNameID = GetAbilityNameIDForSlot(fighterInSpace.typeID, abilitySlotID)
            raise UserError('CannotActivateAbilityRequiresTarget', {'fighterTypeID': fighterInSpace.typeID,
             'abilityNameID': abilityNameID})
        [ self._CheckSafetyLevelForAbility(fighterID, abilitySlotID) for fighterID in fighterIDs ]
        errorsByFighterID = self._ActivateAbilitySlots(fighterIDs, abilitySlotID, targetID)
        for fighterID, error in errorsByFighterID.iteritems():
            if not error:
                self.shipFighterState.OnAbilityActivatedAtTarget(fighterID, abilitySlotID, targetID)

    def ActivateAbilitySlotsOnSelf(self, fighterIDs, abilitySlotID):
        [ self._CheckSafetyLevelForAbility(fighterID, abilitySlotID) for fighterID in fighterIDs ]
        self._ActivateAbilitySlots(fighterIDs, abilitySlotID)

    def ActivateAbilitySlotsAtPoint(self, fighterIDs, abilitySlotID, selectedPoint):
        [ self._CheckSafetyLevelForAbility(fighterID, abilitySlotID) for fighterID in fighterIDs ]
        self._ActivateAbilitySlots(fighterIDs, abilitySlotID, selectedPoint)

    def _ActivateAbilitySlots(self, fighterIDs, abilitySlotID, *abilityArgs, **abilityKwargs):
        if not fighterIDs:
            return
        fighterMgr = sm.RemoteSvc('fighterMgr')
        errorsByFighterID = fighterMgr.CmdActivateAbilitySlots(fighterIDs, abilitySlotID, *abilityArgs, **abilityKwargs)
        for fighterID, error in errorsByFighterID.iteritems():
            if error:
                sm.GetService('gameui').OnRemoteMessage(*error.args)
            else:
                self.shipFighterState.OnAbilityActivationPending(fighterID, abilitySlotID)

        return errorsByFighterID

    def DeactivateAbilitySlots(self, fighterIDs, abilitySlotID):
        if not fighterIDs:
            return
        fighterMgr = sm.RemoteSvc('fighterMgr')
        errorsByFighterID = fighterMgr.CmdDeactivateAbilitySlots(fighterIDs, abilitySlotID)
        for fighterID, error in errorsByFighterID.iteritems():
            if error:
                sm.GetService('gameui').OnRemoteMessage(*error.args)
            else:
                self.shipFighterState.OnAbilityDeactivationPending(fighterID, abilitySlotID)

    def LaunchAllFighters(self):
        tubeIDsToLaunch = self.shipFighterState.fightersInLaunchTubes.keys()
        self.LaunchFightersFromTubes(tubeIDsToLaunch)

    def RecallAllFightersToTubes(self):
        fighterIDsInSpace = self.shipFighterState.GetAllFighterIDsInSpace()
        self.RecallFightersToTubes(fighterIDsInSpace)

    def RecallAllFightersAndOrbit(self):
        fighterIDsInSpace = self.shipFighterState.GetAllFighterIDsInSpace()
        self.CmdReturnAndOrbit(fighterIDsInSpace)

    def AbandonFighter(self, fighterID):
        if eve.Message('ConfirmAbandonFighter', {}, YESNO) != ID_YES:
            return
        return sm.RemoteSvc('fighterMgr').CmdAbandonFighter(fighterID)

    def ScoopAbandonedFighterFromSpace(self, fighterID, toFlagID):
        return sm.RemoteSvc('fighterMgr').CmdScoopAbandonedFighterFromSpace(fighterID, toFlagID)

    def OnStateChange(self, itemID, flag, status, *args):
        if flag == states.selected and status:
            if itemID in self.shipFighterState.GetAllFighterIDsInSpace() or itemID == session.shipid:
                if not uicore.uilib.Key(uiconst.VK_CONTROL):
                    movementFunctions.DeselectAllForNavigation()
                movementFunctions.SelectForNavigation(itemID)
