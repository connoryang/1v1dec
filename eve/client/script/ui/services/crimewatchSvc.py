#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\services\crimewatchSvc.py
from eve.common.script.sys.eveCfg import InStructure
import service
import util
import moniker
import uicls
import uthread
import blue
from crimewatch.const import containerGroupsWithLootRights
from crimewatch.util import IsItemFreeForAggression

class CrimewatchService(service.Service):
    __guid__ = 'svc.crimewatchSvc'
    __dependencies__ = ['michelle',
     'godma',
     'war',
     'facwar',
     'corp']
    __startupdependencies__ = []
    __notifyevents__ = ['ProcessSessionChange',
     'OnWeaponsTimerUpdate',
     'OnPvpTimerUpdate',
     'OnNpcTimerUpdate',
     'OnCriminalTimerUpdate',
     'OnSystemCriminalFlagUpdates',
     'OnCrimewatchEngagementCreated',
     'OnCrimewatchEngagementEnded',
     'OnCrimewatchEngagementStartTimeout',
     'OnCrimewatchEngagementStopTimeout',
     'OnDuelChallenge',
     'OnSecurityStatusUpdate',
     'OnJumpTimersUpdated',
     'OnCorpAggressionSettingsChange']

    def Run(self, *args):
        service.Service.Run(self, *args)
        self.weaponsTimerState = None
        self.weaponsTimerExpiry = None
        self.pvpTimerState = None
        self.pvpTimerExpiry = None
        self.npcTimerState = None
        self.npcTimerExpiry = None
        self.criminalTimerState = None
        self.criminalTimerExpiry = None
        self.criminalFlagsByCharID = {}
        self.myEngagements = {}
        self.safetyLevel = const.shipSafetyLevelFull
        self.duelWindow = None
        self.mySecurityStatus = None
        self.jumpTimers = None
        self.corpAggressionSettings = None

    def ProcessSessionChange(self, isRemote, session, change):
        if 'locationid' in change:
            myCombatTimers, myEngagements, flaggedCharacters, safetyLevel = moniker.CharGetCrimewatchLocation().GetClientStates()
            self.LogInfo('ProcessSessionChange', myCombatTimers, myEngagements, flaggedCharacters, safetyLevel)
            self._UpdateSafetyLevel(safetyLevel)
            weaponTimerState, pvpTimerState, npcTimerState, criminalTimerState = myCombatTimers
            self.weaponsTimerState, self.weaponsTimerExpiry = weaponTimerState
            self.pvpTimerState, self.pvpTimerExpiry = pvpTimerState
            self.npcTimerState, self.npcTimerExpiry = npcTimerState
            self.criminalTimerState, self.criminalTimerExpiry = criminalTimerState
            self.myEngagements = myEngagements
            sm.ScatterEvent('OnCombatTimersUpdated')
            criminals, suspects = flaggedCharacters
            self.criminalFlagsByCharID.clear()
            self.UpdateSuspectsAndCriminals(criminals, suspects)
            if self.duelWindow is not None:
                self.duelWindow.Close()
                self.duelWindow = None
        elif 'shipid' in change and session.structureid:
            _, _, _, safetyLevel = moniker.CharGetCrimewatchLocation().GetClientStates()
            self.LogInfo('ProcessSessionChange', safetyLevel)
            self._UpdateSafetyLevel(safetyLevel)
        if 'corpid' in change:
            self.RefreshCorpAggressionSettings()

    def _UpdateSafetyLevel(self, safetyLevel):
        if self.IsSafetyLockedToFullLevel():
            safetyLevel = const.shipSafetyLevelFull
        self.safetyLevel = safetyLevel

    def IsSafetyLockedToFullLevel(self):
        if InStructure():
            securityClass = sm.GetService('map').GetSecurityClass(session.solarsystemid)
            if securityClass >= const.securityClassHighSec:
                return True
        return False

    def GetSlimItemDataForCharID(self, charID):
        slimItem = None
        if session.solarsystemid is not None:
            ballpark = self.michelle.GetBallpark()
            for _slimItem in ballpark.slimItems.itervalues():
                if _slimItem.charID == charID:
                    slimItem = _slimItem
                    break

        if slimItem is None:
            pubInfo = sm.RemoteSvc('charMgr').GetPublicInfo(charID)
            info = cfg.eveowners.Get(charID)
            slimItem = util.KeyVal()
            slimItem.charID = charID
            slimItem.typeID = info.typeID
            slimItem.corpID = pubInfo.corporationID
            slimItem.warFactionID = sm.GetService('facwar').GetCorporationWarFactionID(pubInfo.corporationID)
            slimItem.allianceID = sm.GetService('corp').GetCorporation(pubInfo.corporationID).allianceID
            slimItem.securityStatus = self.GetCharacterSecurityStatus(charID)
            slimItem.groupID = const.groupCharacter
            slimItem.categoryID = const.categoryOwner
            slimItem.itemID = None
            slimItem.ownerID = charID
        return slimItem

    def UpdateSuspectsAndCriminals(self, criminals, suspects, decriminalizedCharIDs = ()):
        for charID in decriminalizedCharIDs:
            try:
                del self.criminalFlagsByCharID[charID]
            except KeyError:
                pass

        for charID in criminals:
            self.criminalFlagsByCharID[charID] = const.criminalTimerStateActiveCriminal

        for charID in suspects:
            self.criminalFlagsByCharID[charID] = const.criminalTimerStateActiveSuspect

        criminalizedCharIDs = set(self.criminalFlagsByCharID.iterkeys())
        sm.ScatterEvent('OnSuspectsAndCriminalsUpdate', criminalizedCharIDs, set(decriminalizedCharIDs))

    def OnWeaponsTimerUpdate(self, state, expiryTime):
        self.LogInfo('OnWeaponsTimerUpdate', state, expiryTime)
        self.weaponsTimerState = state
        self.weaponsTimerExpiry = expiryTime

    def OnPvpTimerUpdate(self, state, expiryTime):
        self.LogInfo('OnPvpTimerUpdate', state, expiryTime)
        self.pvpTimerState = state
        self.pvpTimerExpiry = expiryTime

    def OnNpcTimerUpdate(self, state, expiryTime):
        self.LogInfo('OnNpcTimerUpdate', state, expiryTime)
        self.npcTimerState = state
        self.npcTimerExpiry = expiryTime

    def OnCriminalTimerUpdate(self, state, expiryTime):
        self.LogInfo('OnCriminalTimerUpdate', state, expiryTime)
        self.criminalTimerState = state
        self.criminalTimerExpiry = expiryTime

    def OnSystemCriminalFlagUpdates(self, newIdles, newSuspects, newCriminals):
        self.LogInfo('OnSystemCriminalFlagUpdates', newIdles, newSuspects, newCriminals)
        self.UpdateSuspectsAndCriminals(newCriminals, newSuspects, newIdles)

    def OnCrimewatchEngagementCreated(self, otherCharId, timeout):
        self.LogInfo('OnCrimewatchEngagementCreated', otherCharId, timeout)
        self.myEngagements[otherCharId] = timeout
        sm.ScatterEvent('OnCrimewatchEngagementUpdated', otherCharId, timeout)
        if self.duelWindow is not None and self.duelWindow.charID == otherCharId:
            self.duelWindow.Close()
            self.duelWindow = None

    def OnCrimewatchEngagementEnded(self, otherCharId):
        self.LogInfo('OnCrimewatchEngagementEnded', otherCharId)
        if otherCharId in self.myEngagements:
            del self.myEngagements[otherCharId]
        sm.ScatterEvent('OnCrimewatchEngagementUpdated', otherCharId, None)

    def OnCrimewatchEngagementStartTimeout(self, otherCharId, timeout):
        self.LogInfo('OnCrimewatchEngagementStartTimeout', otherCharId, timeout)
        self.myEngagements[otherCharId] = timeout
        sm.ScatterEvent('OnCrimewatchEngagementUpdated', otherCharId, timeout)

    def OnCrimewatchEngagementStopTimeout(self, otherCharId):
        self.LogInfo('OnCrimewatchEngagementStopTimeout', otherCharId)
        self.myEngagements[otherCharId] = const.crimewatchEngagementTimeoutOngoing
        sm.ScatterEvent('OnCrimewatchEngagementUpdated', otherCharId, const.crimewatchEngagementTimeoutOngoing)

    def GetMyEngagements(self):
        return self.myEngagements.copy()

    def GetMyBoosters(self):
        myGodmaItem = sm.GetService('godma').GetItem(session.charid)
        boosters = myGodmaItem.boosters
        return boosters

    def GetBoosterEffects(self, booster):
        godma = sm.GetService('godma')
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        staticMgr = dogmaLocation.dogmaStaticMgr
        boosterEffectsNegative = []
        boosterEffectsPositive = []
        if booster:
            boosterEffects = staticMgr.GetPassiveFilteredEffectsByType(booster.boosterTypeID)
            for effectID in boosterEffects:
                eff = cfg.dgmeffects.Get(effectID)
                chanceAttributeID = staticMgr.effects[effectID].fittingUsageChanceAttributeID
                if chanceAttributeID and effectID in booster.sideEffectIDs:
                    boosterEffectsNegative.append(eff)
                if not chanceAttributeID:
                    boosterEffectsPositive.append(eff)

        return {'negative': boosterEffectsNegative,
         'positive': boosterEffectsPositive}

    def GetWeaponsTimer(self):
        return (self.weaponsTimerState, self.weaponsTimerExpiry)

    def GetNpcTimer(self):
        return (self.npcTimerState, self.npcTimerExpiry)

    def GetPvpTimer(self):
        return (self.pvpTimerState, self.pvpTimerExpiry)

    def GetCriminalTimer(self):
        return (self.criminalTimerState, self.criminalTimerExpiry)

    def GetSafetyLevel(self):
        return self.safetyLevel

    def SetSafetyLevel(self, safetyLevel):
        moniker.CharGetCrimewatchLocation().SetSafetyLevel(safetyLevel)
        self.safetyLevel = safetyLevel
        sm.ScatterEvent('OnSafetyLevelChanged', self.safetyLevel)

    def IsCriminal(self, charID):
        return self.criminalFlagsByCharID.get(charID) == const.criminalTimerStateActiveCriminal

    def IsSuspect(self, charID):
        return self.criminalFlagsByCharID.get(charID) == const.criminalTimerStateActiveSuspect

    def IsCriminallyFlagged(self, charID):
        return charID in self.criminalFlagsByCharID

    def HasLimitedEngagmentWith(self, charID):
        return charID in self.myEngagements

    def GetRequiredSafetyLevelForAssistanc(self, targetID):
        if self.IsCriminal(targetID):
            return const.shipSafetyLevelNone
        elif self.IsSuspect(targetID):
            return const.shipSafetyLevelPartial
        else:
            return const.shipSafetyLevelFull

    def GetSafetyLevelRestrictionForAttackingTarget(self, targetID, effect = None):
        securityClass = sm.GetService('map').GetSecurityClass(session.solarsystemid)
        minSafetyLevel = const.shipSafetyLevelFull
        if securityClass > const.securityClassZeroSec:
            item = self.michelle.GetItem(targetID)
            if not item:
                if effect.rangeAttributeID is not None:
                    minSafetyLevel = const.shipSafetyLevelNone
            elif util.IsSystemOrNPC(item.ownerID):
                if item.ownerID == const.ownerCONCORD:
                    minSafetyLevel = const.shipSafetyLevelNone
                elif item.groupID in const.illegalTargetNpcOwnedGroups:
                    if securityClass == const.securityClassHighSec:
                        minSafetyLevel = const.shipSafetyLevelNone
                    else:
                        minSafetyLevel = const.shipSafetyLevelPartial
            elif not self.CanAttackFreely(item):
                if securityClass == const.securityClassHighSec:
                    if item.groupID in const.targetGroupsWithSuspectPenaltyInHighSec:
                        minSafetyLevel = const.shipSafetyLevelPartial
                    else:
                        minSafetyLevel = const.shipSafetyLevelNone
                elif item.groupID == const.groupCapsule:
                    minSafetyLevel = const.shipSafetyLevelNone
                else:
                    minSafetyLevel = const.shipSafetyLevelPartial
        return minSafetyLevel

    def GetSafetyLevelRestrictionForAidingTarget(self, targetID):
        secClass = sm.GetService('map').GetSecurityClass(session.solarsystemid)
        minSafetyLevel = const.shipSafetyLevelFull
        if secClass > const.securityClassZeroSec:
            item = self.michelle.GetItem(targetID)
            if item and item.ownerID != session.charid:
                if self.IsCriminallyFlagged(item.ownerID):
                    if self.IsCriminal(item.ownerID):
                        minSafetyLevel = const.shipSafetyLevelNone
                    elif self.IsSuspect(item.ownerID):
                        minSafetyLevel = const.shipSafetyLevelPartial
                else:
                    minSafetyLevel = const.shipSafetyLevelFull
        return minSafetyLevel

    def CanAttackFreely(self, item):
        if util.IsSystem(item.ownerID) or item.ownerID == session.charid:
            return True
        securityClass = sm.GetService('map').GetSecurityClass(session.solarsystemid)
        if securityClass == const.securityClassZeroSec:
            return True
        if self.IsCriminallyFlagged(item.ownerID):
            return True
        if self.HasLimitedEngagmentWith(item.ownerID):
            return True
        if util.IsCharacter(item.ownerID) and util.IsOutlawStatus(item.securityStatus):
            return True
        if session.warfactionid:
            if hasattr(item, 'corpID') and self.facwar.IsEnemyCorporation(item.corpID, session.warfactionid):
                return True
        belongToPlayerCorp = not util.IsNPC(session.corpid)
        if belongToPlayerCorp:
            if item.ownerID == session.corpid:
                if self.GetCorpAggressionSettings().IsFriendlyFireLegalAtTime(blue.os.GetWallclockTime()):
                    return True
            otherCorpID = getattr(item, 'corpID', None)
            if otherCorpID is not None:
                if otherCorpID == session.corpid:
                    if self.GetCorpAggressionSettings().IsFriendlyFireLegalAtTime(blue.os.GetWallclockTime()):
                        return True
                if self.war.GetRelationship(otherCorpID) == const.warRelationshipAtWarCanFight:
                    return True
            otherAllianceID = getattr(item, 'allianceID', None)
            if otherAllianceID is not None:
                if self.war.GetRelationship(otherAllianceID) == const.warRelationshipAtWarCanFight:
                    return True
        if IsItemFreeForAggression(item.groupID):
            return True
        return False

    def GetRequiredSafetyLevelForEffect(self, effect, targetID = None):
        requiredSafetyLevel = const.shipSafetyLevelFull
        if effect is not None:
            if targetID is None and effect.effectCategory == const.dgmEffTarget:
                targetID = sm.GetService('target').GetActiveTargetID()
                if targetID is None:
                    return requiredSafetyLevel
            requiredSafetyLevel = const.shipSafetyLevelFull
            if effect.isOffensive:
                requiredSafetyLevel = self.GetSafetyLevelRestrictionForAttackingTarget(targetID, effect)
            elif effect.isAssistance:
                requiredSafetyLevel = self.GetSafetyLevelRestrictionForAidingTarget(targetID)
        return requiredSafetyLevel

    def CheckUnsafe(self, requiredSafetyLevel):
        if requiredSafetyLevel < self.safetyLevel:
            return True
        else:
            return False

    def SafetyActivated(self, requiredSafetyLevel):
        self.LogInfo('Safeties activated', self.safetyLevel, requiredSafetyLevel)
        sm.ScatterEvent('OnCrimewatchSafetyCheckFailed')

    def CheckCanTakeItems(self, containerID):
        if session.solarsystemid is None:
            return True
        bp = self.michelle.GetBallpark()
        if self.GetSafetyLevel() == const.shipSafetyLevelFull and bp:
            item = bp.GetInvItem(containerID)
            if item is not None:
                if item.groupID in containerGroupsWithLootRights:
                    bp = self.michelle.GetBallpark()
                    if bp and not bp.HaveLootRight(containerID):
                        return False
        return True

    def GetRequiredSafetyLevelForEngagingDrones(self, droneIDs, targetID):
        safetyLevel = const.shipSafetyLevelFull
        if targetID is not None:
            isAttacking = False
            isAiding = False
            effectIDs = set()
            for droneID in droneIDs:
                item = self.michelle.GetItem(droneID)
                if item is not None:
                    for row in cfg.dgmtypeeffects.get(item.typeID, []):
                        effectID, isDefault = row.effectID, row.isDefault
                        if isDefault:
                            effectIDs.add(effectID)

            if effectIDs:
                effects = [ cfg.dgmeffects.Get(effectID) for effectID in effectIDs ]
                safetyLevels = [ self.GetRequiredSafetyLevelForEffect(effect, targetID) for effect in effects ]
                safetyLevel = min(safetyLevels)
        return safetyLevel

    def OnDuelChallenge(self, fromCharID, fromCorpID, fromAllianceID, expiryTime):
        self.LogInfo('OnDuelChallenge', fromCharID, fromCorpID, fromAllianceID, expiryTime)
        wnd = uicls.DuelInviteWindow(charID=fromCharID, corpID=fromCorpID, allianceID=fromAllianceID)
        try:
            self.duelWindow = wnd
            wnd.StartTimeout(expiryTime)
            result = wnd.ShowDialog(modal=False)
            accept = None
            if 'accept' in wnd.result:
                accept = True
            elif 'decline' in wnd.result:
                accept = False
            if 'block' in wnd.result:
                uthread.new(sm.GetService('addressbook').BlockOwner, fromCharID)
            if accept is not None:
                moniker.CharGetCrimewatchLocation().RespondToDuelChallenge(fromCharID, expiryTime, accept)
        finally:
            self.duelWindow = None

    def StartDuel(self, charID):
        if charID in self.myEngagements:
            self.LogInfo('The char', charID, 'is already in limited engagement with us. No duel request sent.')
        else:
            moniker.CharGetCrimewatchLocation().StartDuelChallenge(charID)

    def GetMySecurityStatus(self):
        if self.mySecurityStatus is None:
            self.mySecurityStatus = moniker.CharGetCrimewatchLocation().GetMySecurityStatus()
        return self.mySecurityStatus

    def GetCharacterSecurityStatus(self, charID):
        return moniker.CharGetCrimewatchLocation().GetCharacterSecurityStatus(charID)

    def OnSecurityStatusUpdate(self, newSecurityStatus):
        self.mySecurityStatus = newSecurityStatus

    def GetSecurityStatusTransactions(self):
        return moniker.CharGetCrimewatchLocation().GetSecurityStatusTransactions()

    def GetJumpTimers(self):
        if self.jumpTimers is None:
            self.jumpTimers = sm.RemoteSvc('jumpTimers').GetTimers(session.charid)
        return self.jumpTimers

    def OnJumpTimersUpdated(self, *args):
        self.jumpTimers = args

    def RefreshCorpAggressionSettings(self):
        self.corpAggressionSettings = self.corp.GetCorpRegistry().GetAggressionSettings()

    def GetCorpAggressionSettings(self):
        if self.corpAggressionSettings is None:
            self.RefreshCorpAggressionSettings()
        return self.corpAggressionSettings

    def OnCorpAggressionSettingsChange(self, aggressionSettings):
        self.corpAggressionSettings = aggressionSettings
