#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\parklife\tactical.py
import dogma.effects
from dogma.const import falloffEffectivnessModuleGroups
from eve.client.script.parklife import tacticalConst
from eve.client.script.ui.view.viewStateConst import ViewState
import evecamera
import evetypes
import service
import uicontrols
import util
import blue
from eveDrones.droneDamageTracker import InBayDroneDamageTracker
import uix
import uiutil
import carbonui.const as uiconst
import uthread
import states as state
import sys
import form
from collections import OrderedDict
import localization
import telemetry
import log
import tacticalOverlay
BRACKETBORDER = 17
OVERVIEW_CONFIGNAME = 0
OVERVIEW_GROUPDATA = 1
BRACKETS_CONFIGNAME = 2
BRACKETS_GROUPDATA = 3
INVISIBLE_TYPES = [const.typeUnlitModularEffectBeacon]

@util.Memoized
def GetCacheByLabel(key):
    return localization.GetByLabel(key)


class TacticalSvc(service.Service):
    __guid__ = 'svc.tactical'
    __update_on_reload__ = 0
    __notifyevents__ = ['DoBallsAdded',
     'DoBallRemove',
     'OnTacticalPresetChange',
     'OnStateChange',
     'OnStateSetupChange',
     'ProcessSessionChange',
     'OnSessionChanged',
     'OnSpecialFX',
     'ProcessOnUIAllianceRelationshipChanged',
     'ProcessRookieStateChange',
     'OnSetCorpStanding',
     'OnSetAllianceStanding',
     'OnSuspectsAndCriminalsUpdate',
     'OnSlimItemChange',
     'OnDroneStateChange2',
     'OnDroneControlLost',
     'OnItemChange',
     'OnBallparkCall',
     'OnEwarStart',
     'OnEwarEnd',
     'OnEwarOnConnect',
     'OnContactChange',
     'OnCrimewatchEngagementUpdated',
     'DoBallsRemove',
     'OnHideUI',
     'OnShowUI',
     'OnCombatMessage']
    __startupdependencies__ = ['settings', 'tacticalNavigation']
    __dependencies__ = ['clientDogmaStaticSvc',
     'state',
     'bracket',
     'overviewPresetSvc']
    ALL_COLUMNS = OrderedDict([('ICON', 'UI/Generic/Icon'),
     ('DISTANCE', 'UI/Common/Distance'),
     ('NAME', 'UI/Common/Name'),
     ('TYPE', 'UI/Common/Type'),
     ('TAG', 'UI/Common/Tag'),
     ('CORPORATION', 'UI/Common/Corporation'),
     ('ALLIANCE', 'UI/Common/Alliance'),
     ('FACTION', 'UI/Common/Faction'),
     ('MILITIA', 'UI/Common/Militia'),
     ('SIZE', 'UI/Inventory/ItemSize'),
     ('VELOCITY', 'UI/Overview/Velocity'),
     ('RADIALVELOCITY', 'UI/Overview/RadialVelocity'),
     ('TRANSVERSALVELOCITY', 'UI/Overview/TraversalVelocity'),
     ('ANGULARVELOCITY', 'UI/Generic/AngularVelocity')])
    COLUMN_UNITS = {'VELOCITY': 'UI/Overview/MetersPerSecondUnitShort',
     'RADIALVELOCITY': 'UI/Overview/MetersPerSecondUnitShort',
     'TRANSVERSALVELOCITY': 'UI/Overview/MetersPerSecondUnitShort',
     'ANGULARVELOCITY': 'UI/Overview/RadiansPerSecondUnitShort'}

    def __init__(self):
        service.Service.__init__(self)
        self._clearModuleTasklet = None

    def Run(self, *etc):
        service.Service.Run(self, *etc)
        self.tacticalOverlay = tacticalOverlay.TacticalOverlay(self, self.tacticalNavigation)
        self.logme = 0
        self.jammers = {}
        self.jammersByJammingType = {}
        self.filterFuncs = None
        self.CleanUp()
        if not (eve.rookieState and eve.rookieState < 23):
            self.Setup()
        self.hideUI = False
        self.flagsAreDirty = False
        self.flagCheckingThread = uthread.new(self.FlagsDirtyCheckingLoop)
        self.inBayDroneDamageTracker = None

    def Setup(self):
        self.CleanUp()
        self.AssureSetup()
        if util.InSpace():
            if self.IsTacticalOverlayActive():
                self.tacticalOverlay.Initialize()
            self.Open()

    def Stop(self, *etc):
        service.Service.Stop(self, *etc)
        self.CleanUp()

    def OnCombatMessage(self, messageName, messageArgs):
        if 'specialObject' in messageArgs:
            objectName = sm.GetService('bracket').GetBracketName2(messageArgs['specialObject'])
            messageArgs['specialObject'] = objectName
        sm.GetService('logger').AddCombatMessage(messageName, messageArgs)

    @telemetry.ZONE_METHOD
    def OnBallparkCall(self, eventName, argTuple):
        if self.sr is None:
            return
        if eventName == 'SetBallInteractive' and argTuple[1] == 1:
            bp = sm.GetService('michelle').GetBallpark()
            if not bp:
                return
            slimItem = bp.GetInvItem(argTuple[0])
            if not slimItem:
                return
            self.MarkFlagsAsDirty()

    @telemetry.ZONE_METHOD
    def OnItemChange(self, item, change):
        if (const.ixFlag in change or const.ixLocationID in change) and item.flagID == const.flagDroneBay:
            droneview = self.GetPanel('droneview')
            if droneview:
                droneview.CheckDrones()
            else:
                self.CheckInitDrones()

    @telemetry.ZONE_METHOD
    def ProcessSessionChange(self, isRemote, session, change):
        doResetJammers = False
        if self.logme:
            self.LogInfo('Tactical::ProcessSessionChange', isRemote, session, change)
        if 'stationid' in change:
            doResetJammers = True
        if 'solarsystemid' in change:
            self.TearDownOverlay()
            doResetJammers = True
        if 'shipid' in change:
            for itemID in self.attackers:
                sm.GetService('state').SetState(itemID, state.threatAttackingMe, 0)

            self.attackers = {}
            overview = form.OverView.GetIfOpen()
            if overview:
                overview.FlushEwarStates()
            doResetJammers = True
            droneview = self.GetPanel('droneview')
            if droneview:
                if getattr(self, '_initingDrones', False):
                    self.LogInfo('Tactical: ProcessSessionChange: busy initing drones, cannot close the window')
                else:
                    droneview.Close()
        if doResetJammers:
            self.ResetJammers()

    def ResetJammers(self):
        self.jammers = {}
        self.jammersByJammingType = {}
        sm.ScatterEvent('OnEwarEndFromTactical', doAnimate=False)

    def RemoveBallFromJammers(self, ball, *args):
        ballID = ball.id
        effectsFromBall = self.jammers.get(ballID)
        if effectsFromBall is None:
            return
        doUpdate = False
        for effectName, effectSet in self.jammersByJammingType.iteritems():
            if effectName not in effectsFromBall:
                continue
            tuplesToRemove = set()
            for effectTuple in effectSet:
                effectBallID, moduleID = effectTuple
                if effectBallID == ballID:
                    tuplesToRemove.add(effectTuple)

            if tuplesToRemove:
                effectSet.difference_update(tuplesToRemove)
                doUpdate = True

        self.jammers.pop(ballID, None)
        if doUpdate:
            sm.ScatterEvent('OnEwarEndFromTactical')

    def OnSessionChanged(self, isRemote, session, change):
        if util.InSpace():
            self.AssureSetup()
            self.Open()
            if self.IsTacticalOverlayActive() and not self.hideUI:
                self.tacticalOverlay.Initialize()
            self.CheckInitDrones()
            self.MarkFlagsAsDirty()
            if 'shipid' in change:
                self.tacticalOverlay.OnShipChange()
        else:
            self.CleanUp()

    @telemetry.ZONE_METHOD
    def OnSlimItemChange(self, oldSlim, newSlim):
        if not util.InSpace():
            return
        update = 0
        if getattr(newSlim, 'allianceID', None) and newSlim.allianceID != getattr(oldSlim, 'allianceID', None):
            update = 1
        elif newSlim.corpID and newSlim.corpID != oldSlim.corpID:
            update = 2
        elif newSlim.charID != oldSlim.charID:
            update = 3
        elif newSlim.ownerID != oldSlim.ownerID:
            update = 4
        elif getattr(newSlim, 'lootRights', None) != getattr(oldSlim, 'lootRights', None):
            update = 5
        elif getattr(newSlim, 'isEmpty', None) != getattr(oldSlim, 'isEmpty', None):
            update = 6
        if update:
            self.MarkFlagsAsDirty()

    def ProcessOnUIAllianceRelationshipChanged(self, *args):
        if self.InSpace():
            self.MarkFlagsAsDirty()

    def ProcessRookieStateChange(self, state):
        if util.InSpace():
            if not not (eve.rookieState and eve.rookieState < 23):
                self.CleanUp()
            elif not self.GetPanel(form.OverView.default_windowID):
                self.Setup()

    def OnContactChange(self, contactIDs, contactType = None):
        if util.InSpace():
            self.MarkFlagsAsDirty()

    def OnSetCorpStanding(self, *args):
        if util.InSpace():
            self.MarkFlagsAsDirty()

    def OnSetAllianceStanding(self, *args):
        if util.InSpace():
            self.MarkFlagsAsDirty()

    def OnCrimewatchEngagementUpdated(self, otherCharId, timeout):
        if util.InSpace():
            uthread.new(self.DelayedFlagStateUpdate)

    def OnSuspectsAndCriminalsUpdate(self, criminalizedCharIDs, decriminalizedCharIDs):
        if util.InSpace():
            uthread.new(self.DelayedFlagStateUpdate)

    def DelayedFlagStateUpdate(self):
        if getattr(self, 'delayedFlagStateUpdate', False):
            return
        setattr(self, 'delayedFlagStateUpdate', True)
        blue.pyos.synchro.SleepWallclock(1000)
        self.MarkFlagsAsDirty()
        setattr(self, 'delayedFlagStateUpdate', False)

    def OnHideUI(self):
        self.hideUI = True
        if self.IsTacticalOverlayActive():
            self.tacticalOverlay.TearDown()

    def OnShowUI(self):
        self.hideUI = False
        if self.IsTacticalOverlayActive():
            self.tacticalOverlay.Initialize()

    @telemetry.ZONE_METHOD
    def OnSpecialFX(self, shipID, moduleID, moduleTypeID, targetID, otherTypeID, guid, isOffensive, start, active, duration = -1, repeat = None, startTime = None, timeFromStart = 0, graphicInfo = None):
        if targetID == eve.session.shipid and isOffensive:
            attackerID = shipID
            attackTime = startTime
            attackRepeat = repeat
            shipItem = sm.StartService('michelle').GetItem(shipID)
            if shipItem and shipItem.categoryID == const.categoryStarbase:
                attackerID = moduleID
                attackTime = 0
                attackRepeat = 0
            data = self.attackers.get(attackerID, [])
            key = (moduleID,
             guid,
             attackTime,
             duration,
             attackRepeat)
            if start and shipID != session.shipid:
                if key not in data:
                    data.append(key)
                sm.GetService('state').SetState(attackerID, state.threatAttackingMe, 1)
            else:
                toRemove = None
                for signature in data:
                    if signature[0] == key[0] and signature[1] == key[1] and signature[2] == key[2] and signature[3] == key[3]:
                        toRemove = signature
                        break

                if toRemove is not None:
                    data.remove(toRemove)
                if not data:
                    sm.GetService('state').SetState(attackerID, state.threatAttackingMe, 0)
            self.attackers[attackerID] = data
        if start and guid == 'effects.WarpScramble':
            if settings.user.ui.Get('notifyMessagesEnabled', 1) or eve.session.shipid in (shipID, targetID):
                jammerName = sm.GetService('bracket').GetBracketName2(shipID)
                targetName = sm.GetService('bracket').GetBracketName2(targetID)
                if jammerName and targetName:
                    if eve.session.shipid == targetID:
                        sm.GetService('logger').AddCombatMessage('WarpScrambledBy', {'scrambler': jammerName})
                    elif eve.session.shipid == shipID:
                        sm.GetService('logger').AddCombatMessage('WarpScrambledSuccess', {'scrambled': targetName})
                    else:
                        sm.GetService('logger').AddCombatMessage('WarpScrambledOtherBy', {'scrambler': jammerName,
                         'scrambled': targetName})

    def CheckInitDrones(self):
        mySlim = uix.GetBallparkRecord(eve.session.shipid)
        if not mySlim:
            return
        if mySlim.groupID == const.groupCapsule:
            return
        dronesInBay = sm.GetService('invCache').GetInventoryFromId(session.shipid).ListDroneBay()
        if dronesInBay:
            self.InitDrones()
        else:
            myDrones = sm.GetService('michelle').GetDrones()
            if myDrones:
                self.InitDrones()

    @telemetry.ZONE_METHOD
    def Open(self):
        self.InitSelectedItem()
        self.InitOverview()
        self.CheckInitDrones()

    def GetMain(self):
        if self and getattr(self.sr, 'mainParent', None):
            return self.sr.mainParent

    def OnStateChange(self, itemID, flag, true, *args):
        uthread.new(self._OnStateChange, itemID, flag, true, *args)

    def _OnStateChange(self, itemID, flag, true, *args):
        if not util.InSpace():
            return
        if not self or getattr(self, 'sr', None) is None:
            return
        if self.logme:
            self.LogInfo('Tactical::OnStateChange', itemID, flag, true, *args)
        self.tacticalOverlay.CheckState(itemID, flag, true)

    def OnTacticalPresetChange(self, label, set):
        uthread.new(self.InitConnectors).context = 'tactical::OnTacticalPresetChange-->InitConnectors'

    def OnStateSetupChange(self, what):
        self.MarkFlagsAsDirty()
        self.InitConnectors()

    def Toggle(self):
        pass

    def BlinkHeader(self, key):
        if not self or self.sr is None:
            return
        panel = getattr(self.sr, key.lower(), None)
        if panel:
            panel.Blink()

    def IsExpanded(self, key):
        panel = getattr(self.sr, key.lower(), None)
        if panel:
            return panel.sr.main.state == uiconst.UI_PICKCHILDREN

    def AssureSetup(self):
        if self.logme:
            self.LogInfo('Tactical::AssureSetup')
        if getattr(self, 'setupAssured', None):
            return
        if getattr(self, 'sr', None) is None:
            self.sr = uiutil.Bunch()
        self.setupAssured = 1

    def CleanUp(self):
        if self.logme:
            self.LogInfo('Tactical::CleanUp')
        self.sr = None
        self.targetingRanges = None
        self.toggling = 0
        self.setupAssured = 0
        self.lastFactor = None
        self.groupList = None
        self.groupIDs = []
        self.intersections = []
        self.threats = {}
        self.attackers = {}
        self.TearDownOverlay()
        uicore.layer.tactical.Flush()
        self.dronesInited = 0
        self.busy = 0

    def GetFilterFuncs(self):
        if self.filterFuncs is None:
            stateSvc = sm.GetService('state')
            self.filterFuncs = {'Criminal': stateSvc.CheckCriminal,
             'Suspect': stateSvc.CheckSuspect,
             'Outlaw': stateSvc.CheckOutlaw,
             'Dangerous': stateSvc.CheckDangerous,
             'StandingHigh': stateSvc.CheckStandingHigh,
             'StandingGood': stateSvc.CheckStandingGood,
             'StandingNeutral': stateSvc.CheckStandingNeutral,
             'StandingBad': stateSvc.CheckStandingBad,
             'StandingHorrible': stateSvc.CheckStandingHorrible,
             'NoStanding': stateSvc.CheckNoStanding,
             'SameFleet': stateSvc.CheckSameFleet,
             'SameCorp': stateSvc.CheckSameCorp,
             'SameAlliance': stateSvc.CheckSameAlliance,
             'SameMilitia': stateSvc.CheckSameMilitia,
             'AtWarCanFight': stateSvc.CheckAtWarCanFight,
             'AtWarMilitia': stateSvc.CheckAtWarMilitia,
             'IsWanted': stateSvc.CheckIsWanted,
             'HasKillRight': stateSvc.CheckHasKillRight,
             'WreckViewed': stateSvc.CheckWreckViewed,
             'WreckEmpty': stateSvc.CheckWreckEmpty,
             'LimitedEngagement': stateSvc.CheckLimitedEngagement,
             'AlliesAtWar': stateSvc.CheckAlliesAtWar,
             'AgentInteractable': stateSvc.CheckAgentInteractable}
        return self.filterFuncs

    def CheckFiltered(self, slimItem, filtered, alwaysShow):
        stateSvc = sm.GetService('state')
        if len(filtered) + len(alwaysShow) > 3:
            ownerID = slimItem.ownerID
            if ownerID is None or ownerID == const.ownerSystem or util.IsNPC(ownerID):
                checkArgs = (slimItem, None)
            else:
                checkArgs = (slimItem, stateSvc._GetRelationship(slimItem))
        else:
            checkArgs = (slimItem,)
        functionDict = self.GetFilterFuncs()
        for functionName in alwaysShow:
            f = functionDict.get(functionName, None)
            if f is None:
                self.LogError('CheckFiltered got bad functionName: %r' % functionName)
                continue
            if f(*checkArgs):
                return False

        for functionName in filtered:
            f = functionDict.get(functionName, None)
            if f is None:
                self.LogError('CheckFiltered got bad functionName: %r' % functionName)
                continue
            if f(*checkArgs):
                return True

        return False

    def RefreshOverview(self):
        overview = form.OverView.GetIfOpen()
        if overview:
            overview.FullReload()

    def UpdateStates(self, slimItem, uiwindow):
        print 'Deprecated, TacticalSvc.UpdateStates, call UpdateFlagAndBackground on the uiwindow instead'

    def UpdateBackground(self, slimItem, uiwindow):
        print 'Deprecated, TacticalSvc.UpdateBackground, call on the uiwindow instead'

    def UpdateIcon(self, slimItem, uiwindow):
        print 'Deprecated, TacticalSvc.UpdateIcon, call UpdateIconColor on the uiwindow instead'

    def UpdateFlag(self, slimItem, uiwindow):
        print 'Deprecated, TacticalSvc.UpdateFlag, call on the uiwindow instead'

    def GetFlagUI(self, parent):
        print 'Deprecated, TacticalSvc.GetFlagUI, make the icon yourself'

    def UpdateFlagPositions(self, uiwindow, icon = None):
        print 'Deprecated, TacticalSvc.UpdateFlagPositions, call on the uiwindow instead'

    def MarkFlagsAsDirty(self):
        self.flagsAreDirty = True

    @telemetry.ZONE_METHOD
    def FlagsDirtyCheckingLoop(self):
        while self.state == service.SERVICE_RUNNING:
            try:
                if self.flagsAreDirty:
                    self.flagsAreDirty = False
                    self.InvalidateFlags()
            except Exception:
                log.LogException(extraText='Error invalidating tactical flags')
                sys.exc_clear()

            blue.pyos.synchro.SleepWallclock(500)

    def InvalidateFlags(self):
        if not util.InSpace():
            return
        overview = form.OverView.GetIfOpen()
        if overview:
            overview.UpdateAllIconAndBackgroundFlags()
        sm.GetService('bracket').RenewFlags()

    def InvalidateFlagsExtraLimited(self, charID):
        if util.InSpace():
            sm.GetService('bracket').RenewSingleFlag(charID)

    def GetAllColumns(self):
        return self.ALL_COLUMNS.keys()

    def GetColumnLabel(self, columnID, addFormatUnit = False):
        localizedID = self.ALL_COLUMNS.get(columnID, None)
        if localizedID:
            retString = localization.GetByLabel(localizedID)
            if addFormatUnit:
                unitLabelID = self.COLUMN_UNITS.get(columnID, None)
                if unitLabelID:
                    retString = '%s (%s)' % (retString, localization.GetByLabel(unitLabelID))
            return retString
        return columnID

    def GetColumns(self):
        default = self.GetDefaultVisibleColumns()
        userSet = settings.user.overview.Get('overviewColumns', None)
        if userSet is None:
            userSet = default
        userSetOrder = self.GetColumnOrder()
        return [ label for label in userSetOrder if label in userSet ]

    def GetColumnOrder(self):
        ret = settings.user.overview.Get('overviewColumnOrder', None)
        if ret is None:
            return self.GetAllColumns()
        return ret

    def GetDefaultVisibleColumns(self):
        default = ['ICON',
         'DISTANCE',
         'NAME',
         'TYPE']
        return default

    def GetNotSavedTranslations(self):
        ret = [u'Not saved', u'Nicht gespeichert', u'\u672a\u30bb\u30fc\u30d6']
        return ret

    def SetNPCGroups(self):
        sendGroupIDs = []
        userSettings = self.overviewPresetSvc.GetGroups()
        for cat, groupdict in util.GetNPCGroups().iteritems():
            for groupname, groupids in groupdict.iteritems():
                for groupid in groupids:
                    if groupid in userSettings:
                        sendGroupIDs += groupids
                        break

        if sendGroupIDs:
            changeList = [('groups', sendGroupIDs, 1)]
            self.overviewPresetSvc.ChangeSettings(changeList=changeList)

    def GetFilteredStatesFunctionNames(self, isBracket = False):
        return [ sm.GetService('state').GetStateProps(flag).label for flag in self.overviewPresetSvc.GetFilteredStates(isBracket=isBracket) ]

    def GetAlwaysShownStatesFunctionNames(self, isBracket = False):
        return [ sm.GetService('state').GetStateProps(flag).label for flag in self.overviewPresetSvc.GetAlwaysShownStates(isBracket=isBracket) ]

    def Get(self, what, default):
        if self.logme:
            self.LogInfo('Tactical::Get', what, default)
        return getattr(self, what, default)

    def OpenSettings(self, *args):
        uicore.cmd.OpenOverviewSettings()

    def ToggleOnOff(self):
        current = self.IsTacticalOverlayActive()
        if not current:
            self.ShowTacticalOverlay()
        elif self.tacticalOverlay.IsInitialized():
            self.HideTacticalOverlay()

    def HideTacticalOverlay(self):
        self._SetTacticalOverlayActive(False)
        self.TearDownOverlay()
        sm.ScatterEvent('OnTacticalOverlayChange')

    def _SetTacticalOverlayActive(self, isActive):
        cam = sm.GetService('sceneManager').GetActiveSpaceCamera()
        if cam.cameraID == evecamera.CAM_TACTICAL:
            settings.user.overview.Set('viewTactical_camTactical', isActive)
        elif cam.cameraID == evecamera.CAM_SHIPORBIT:
            settings.user.overview.Set('viewTactical', isActive)

    def ShowTacticalOverlay(self):
        if not self.IsTacticalOverlayAllowed():
            return
        self._SetTacticalOverlayActive(True)
        if not self.hideUI:
            self.tacticalOverlay.Initialize()
        sm.ScatterEvent('OnTacticalOverlayChange')

    def IsTacticalOverlayAllowed(self):
        cam = sm.GetService('sceneManager').GetActiveSpaceCamera()
        if cam.cameraID == evecamera.CAM_SHIPPOV:
            return False
        return True

    def IsTacticalOverlayActive(self):
        cameraID = sm.GetService('viewState').GetView(ViewState.Space).GetRegisteredCameraID()
        if cameraID == evecamera.CAM_TACTICAL:
            return settings.user.overview.Get('viewTactical_camTactical', True)
        elif cameraID == evecamera.CAM_SHIPPOV:
            return False
        else:
            return settings.user.overview.Get('viewTactical', False)

    def CheckInit(self):
        if util.InSpace() and self.IsTacticalOverlayActive() and not self.hideUI:
            self.tacticalOverlay.Initialize()

    def TearDownOverlay(self):
        if self.targetingRanges:
            self.targetingRanges.KillTimer()
        self.tacticalOverlay.TearDown()

    def GetOverlay(self):
        return self.tacticalOverlay

    def ShowModuleRange(self, module, charge = None):
        if self._clearModuleTasklet is not None:
            self._clearModuleTasklet.kill()
        self._clearModuleTasklet = None
        self.tacticalOverlay.UpdateModuleRange(module, charge)

    def ClearModuleRange(self):

        def _task():
            blue.synchro.SleepSim(500)
            if self._clearModuleTasklet is not None:
                self._clearModuleTasklet = None
                self.tacticalOverlay.UpdateModuleRange()

        self._clearModuleTasklet = uthread.new(_task)

    def FindMaxRange(self, module, charge, dogmaLocation = None, *args):
        maxRange = 0
        falloffDist = 0
        bombRadius = 0
        cynoRadius = 0
        if not dogmaLocation:
            dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        try:
            effectID = self.clientDogmaStaticSvc.GetDefaultEffect(module.typeID)
        except KeyError:
            pass
        else:
            effect = self.clientDogmaStaticSvc.GetEffect(effectID)
            if effect.rangeAttributeID is not None:
                maxRange = dogmaLocation.GetAccurateAttributeValue(module.itemID, effect.rangeAttributeID)
                if module.groupID in falloffEffectivnessModuleGroups:
                    falloffDist = dogmaLocation.GetAccurateAttributeValue(module.itemID, const.attributeFalloffEffectiveness)
                else:
                    falloffDist = dogmaLocation.GetAccurateAttributeValue(module.itemID, const.attributeFalloff)

        if module.groupID == const.groupCynosuralField:
            isCovert = dogmaLocation.GetAttributeValue(module.itemID, const.attributeIsCovert)
            beaconRadius = 0.0
            if isCovert:
                beaconRadius = evetypes.GetRadius(const.typeCovertCynosuralFieldI)
            else:
                beaconRadius = evetypes.GetRadius(const.typeCynosuralFieldI)
            cynoRadius = dogmaLocation.GetAccurateAttributeValue(module.itemID, const.attributeCynosuralFieldSpawnRadius)
            cynoRadius += 2.0 * beaconRadius
        excludedChargeGroups = [const.groupScannerProbe, const.groupSurveyProbe]
        if not maxRange and charge and charge.groupID not in excludedChargeGroups:
            flightTime = dogmaLocation.GetAccurateAttributeValue(charge.itemID, const.attributeExplosionDelay)
            velocity = dogmaLocation.GetAccurateAttributeValue(charge.itemID, const.attributeMaxVelocity)
            bombRadius = dogmaLocation.GetAccurateAttributeValue(charge.itemID, const.attributeEmpFieldRange)
            maxRange = flightTime * velocity / 1000.0
        return (maxRange,
         falloffDist,
         bombRadius,
         cynoRadius)

    def GetPanelForUpdate(self, what):
        panel = self.GetPanel(what)
        if panel and not panel.IsCollapsed() and not panel.IsMinimized():
            return panel

    def GetPanel(self, what):
        wnd = uicontrols.Window.GetIfOpen(what)
        if wnd and not wnd.destroyed:
            return wnd

    def InitDrones(self):
        if getattr(self, '_initingDrones', False):
            return
        self._initingDrones = True
        try:
            if not form.DroneView.GetIfOpen():
                form.DroneView.Open(showActions=False, panelName=localization.GetByLabel('UI/Drones/Drones'))
        finally:
            self._initingDrones = False

    def InitOverview(self):
        if not form.OverView.GetIfOpen():
            form.OverView.Open(showActions=False, panelName=localization.GetByLabel('UI/Overview/Overview'))

    def InitSelectedItem(self):
        if not form.ActiveItem.GetIfOpen():
            form.ActiveItem.Open(panelname=localization.GetByLabel('UI/Inflight/ActiveItem/SelectedItem'))

    def InitConnectors(self):
        if self.logme:
            self.LogInfo('Tactical::InitConnectors')
        if not self.tacticalOverlay.IsInitialized():
            return
        self.tacticalOverlay.InitConnectors()

    def WantIt(self, slimItem, filtered = None, alwaysShown = None, isBracket = False):
        if not slimItem:
            return False
        if slimItem.typeID in INVISIBLE_TYPES:
            return False
        if isBracket and self.overviewPresetSvc.GetActiveBracketPresetName() is None:
            return True
        if self.logme:
            self.LogInfo('Tactical::WantIt', slimItem)
        if slimItem.itemID == session.shipid:
            return isBracket
        filterGroups = self.overviewPresetSvc.GetValidGroups(isBracket=isBracket)
        if slimItem.groupID in filterGroups:
            if sm.GetService('state').CheckIfFilterItem(slimItem) and self.CheckFiltered(slimItem, filtered, alwaysShown):
                return False
            return True
        return False

    def CheckIfGroupIDActive(self, groupID):
        if getattr(self, 'logme', None):
            self.LogInfo('Tactical::CheckIfGroupIDActive', groupID)
        if groupID not in tacticalConst.groupIDs:
            return -1
        return groupID in self.overviewPresetSvc.GetGroups()

    def DoBallsAdded(self, *args, **kw):
        import stackless
        import blue
        t = stackless.getcurrent()
        timer = t.PushTimer(blue.pyos.taskletTimer.GetCurrent() + '::tactical')
        try:
            return self.DoBallsAdded_(*args, **kw)
        finally:
            t.PopTimer(timer)

    def DoBallsAdded_(self, lst):
        if not self or getattr(self, 'sr', None) is None:
            return
        uthread.pool('Tactical::DoBallsAdded', self._DoBallsAdded, lst)

    def _DoBallsAdded(self, lst):
        if not self or self.sr is None:
            return
        if self.logme:
            self.LogInfo('Tactical::DoBallsAdded', lst)
        self.LogInfo('Tactical - adding balls, num balls:', len(lst))
        inCapsule = 0
        mySlim = uix.GetBallparkRecord(eve.session.shipid)
        if mySlim and mySlim.groupID == const.groupCapsule:
            inCapsule = 1
        checkDrones = 0
        filtered = self.GetFilteredStatesFunctionNames()
        alwaysShown = self.GetAlwaysShownStatesFunctionNames()
        for each in lst:
            if each[1].itemID == eve.session.shipid:
                checkDrones = 1
            if not checkDrones and not inCapsule and each[1].categoryID == const.categoryDrone:
                drone = sm.GetService('michelle').GetDroneState(each[1].itemID)
                if drone and (drone.ownerID == eve.session.charid or drone.controllerID == eve.session.shipid):
                    checkDrones = 1
            if not self.WantIt(each[1], filtered, alwaysShown):
                continue
            self.tacticalOverlay.AddConnector(each[0])

        if checkDrones:
            droneview = self.GetPanel('droneview')
            if droneview:
                droneview.CheckDrones()
            else:
                self.CheckInitDrones()

    def OnDroneStateChange2(self, droneID, oldState, newState):
        self.InitDrones()
        droneview = self.GetPanel('droneview')
        if droneview:
            droneview.CheckDrones()

    def OnDroneControlLost(self, droneID):
        droneview = self.GetPanel('droneview')
        if droneview:
            droneview.CheckDrones()

    @telemetry.ZONE_METHOD
    def DoBallsRemove(self, pythonBalls, isRelease):
        for ball, slimItem, terminal in pythonBalls:
            self.DoBallRemove(ball, slimItem, terminal)

    def DoBallRemove(self, ball, slimItem, terminal):
        if not self or getattr(self, 'sr', None) is None:
            return
        if ball is None:
            return
        if not util.InSpace():
            return
        if self.logme:
            self.LogInfo('Tactical::DoBallRemove', ball.id)
        uthread.pool('tactical::DoBallRemoveThread', self.DoBallRemoveThread, ball, slimItem, terminal)
        self.RemoveBallFromJammers(ball)

    def DoBallRemoveThread(self, ball, slimItem, terminal):
        self.tacticalOverlay.RemoveConnector(ball.id)
        droneview = self.GetPanel('droneview')
        if droneview and slimItem.categoryID == const.categoryDrone and slimItem.ownerID == eve.session.charid:
            droneview.CheckDrones()

    def OnEwarStart(self, sourceBallID, moduleID, targetBallID, jammingType):
        if not jammingType:
            self.LogError('Tactical::OnEwarStart', sourceBallID, jammingType)
            return
        if not hasattr(self, 'jammers'):
            self.jammers = {}
        if not hasattr(self, 'jammersByJammingType'):
            self.jammersByJammingType = {}
        if targetBallID == session.shipid:
            if sourceBallID not in self.jammers:
                self.jammers[sourceBallID] = {}
            self.jammers[sourceBallID][jammingType] = sm.GetService('state').GetEwarFlag(jammingType)
            if jammingType not in self.jammersByJammingType:
                self.jammersByJammingType[jammingType] = set()
            self.jammersByJammingType[jammingType].add((sourceBallID, moduleID))
            sm.ScatterEvent('OnEwarStartFromTactical')

    def OnEwarEnd(self, sourceBallID, moduleID, targetBallID, jammingType):
        if not jammingType:
            self.LogError('Tactical::OnEwarEnd', sourceBallID, jammingType)
            return
        if not hasattr(self, 'jammers'):
            return
        if sourceBallID in self.jammers and jammingType in self.jammers[sourceBallID]:
            del self.jammers[sourceBallID][jammingType]
        if jammingType in self.jammersByJammingType and (sourceBallID, moduleID) in self.jammersByJammingType[jammingType]:
            self.jammersByJammingType[jammingType].remove((sourceBallID, moduleID))
        ewarId = (sourceBallID, moduleID, targetBallID)
        sm.ScatterEvent('OnEwarEndFromTactical', jammingType, ewarId)

    def OnEwarOnConnect(self, shipID, m, moduleTypeID, targetID, *args):
        if targetID != session.shipid:
            return
        ewarType = self.FindEwarTypeFromModuleTypeID(moduleTypeID)
        if ewarType is not None:
            self.OnEwarStart(shipID, m, targetID, ewarType)

    def FindEwarTypeFromModuleTypeID(self, moduleTypeID, *args):
        try:
            effectID = self.clientDogmaStaticSvc.GetDefaultEffect(moduleTypeID)
            return dogma.effects.GetEwarTypeByEffectID(effectID)
        except KeyError:
            pass

    def ImportOverviewSettings(self, *args):
        form.ImportOverviewWindow.Open()

    def ExportOverviewSettings(self, *args):
        form.ExportOverviewWindow.Open()

    def OnEveGetsFocus(self, *args):
        pass

    def GetInBayDroneDamageTracker(self):
        dogmaLM = sm.GetService('godma').GetDogmaLM()
        clientDogmaLM = sm.GetService('clientDogmaIM').GetDogmaLocation()
        if self.inBayDroneDamageTracker is None:
            self.inBayDroneDamageTracker = InBayDroneDamageTracker(dogmaLM, clientDogmaLM)
        else:
            self.inBayDroneDamageTracker.SetDogmaLM(dogmaLM)
        return self.inBayDroneDamageTracker
