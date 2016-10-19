#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\services\menuSvcExtras\movementFunctions.py
import sys
from eve.client.script.parklife import states
from eve.common.script.sys.eveCfg import CheckShipHasFighterBay
import uix
import uiutil
import util
import service
import destiny
import carbonui.const as uiconst
import localization
import eve.client.script.ui.util.defaultRangeUtils as defaultRangeUtils
import const
import log
from eveexceptions import UserError
ORBIT_RANGES = (500, 1000, 2500, 5000, 7500, 10000, 15000, 20000, 25000, 30000)
KEEP_AT_RANGE_RANGES = (500, 1000, 2500, 5000, 7500, 10000, 15000, 20000, 25000, 30000)

def SetDefaultDist(key):
    if not key:
        return
    minDist, maxDist = {'Orbit': (500, 1000000),
     'KeepAtRange': (50, 1000000),
     'WarpTo': (const.minWarpEndDistance, const.maxWarpEndDistance)}.get(key, (500, 1000000))
    current = sm.GetService('menu').GetDefaultActionDistance(key)
    current = current or ''
    fromDist = util.FmtAmt(minDist)
    toDist = util.FmtAmt(maxDist)
    if key == 'KeepAtRange':
        hint = localization.GetByLabel('UI/Inflight/SetDefaultKeepAtRangeDistanceHint', fromDist=fromDist, toDist=toDist)
        caption = localization.GetByLabel('UI/Inflight/SetDefaultKeepAtRangeDistance')
    elif key == 'Orbit':
        hint = localization.GetByLabel('UI/Inflight/SetDefaultOrbitDistanceHint', fromDist=fromDist, toDist=toDist)
        caption = localization.GetByLabel('UI/Inflight/SetDefaultOrbitDistance')
    elif key == 'WarpTo':
        hint = localization.GetByLabel('UI/Inflight/SetDefaultWarpWithinDistanceHint', fromDist=fromDist, toDist=toDist)
        caption = localization.GetByLabel('UI/Inflight/SetDefaultWarpWithinDistance')
    else:
        hint = ''
        caption = ''
    r = uix.QtyPopup(maxvalue=maxDist, minvalue=minDist, setvalue=current, hint=hint, caption=caption, label=None, digits=0)
    if r:
        newRange = max(minDist, min(maxDist, r['qty']))
        defaultRangeUtils.UpdateRangeSetting(key, newRange)


def GetKeepAtRangeMenu(itemID, dist, currentDistance):
    keepRangeMenu = _GetRangeMenu(itemID=itemID, dist=dist, currentDistance=currentDistance, rangesList=KEEP_AT_RANGE_RANGES, mainFunc=KeepAtRange, setDefaultFunc=defaultRangeUtils.SetDefaultKeepAtRangeDist, atCurrentRangeLabel='UI/Inflight/KeepAtCurrentRange', setDefaultLabel='UI/Inflight/Submenus/SetDefaultWarpRange')
    return keepRangeMenu


def GetOrbitMenu(itemID, dist, currentDistance):
    orbitMenu = _GetRangeMenu(itemID=itemID, dist=dist, currentDistance=currentDistance, rangesList=ORBIT_RANGES, mainFunc=Orbit, setDefaultFunc=defaultRangeUtils.SetDefaultOrbitDist, atCurrentRangeLabel='UI/Inflight/OrbitAtCurrentRange', setDefaultLabel='UI/Inflight/Submenus/SetDefaultWarpRange')
    return orbitMenu


def _GetRangeMenu(itemID, dist, currentDistance, rangesList, mainFunc, setDefaultFunc, atCurrentRangeLabel, setDefaultLabel, *args):
    rangeMenu = []
    rangeSubMenu = []
    for eachRange in rangesList:
        fmtRange = util.FmtDist(eachRange)
        rangeSubMenu.append((fmtRange, setDefaultFunc, (eachRange,)))
        rangeMenu.append((fmtRange, mainFunc, (itemID, eachRange)))

    rangeMenu += [(uiutil.MenuLabel(atCurrentRangeLabel, {'currentDistance': currentDistance}), mainFunc, (itemID, dist)), None, (uiutil.MenuLabel(setDefaultLabel), rangeSubMenu)]
    return rangeMenu


def GetDefaultDist(key, itemID = None, minDist = 500, maxDist = 1000000):
    drange = sm.GetService('menu').GetDefaultActionDistance(key)
    if drange is None:
        dist = ''
        if itemID:
            bp = sm.StartService('michelle').GetBallpark()
            if not bp:
                return
            ball = bp.GetBall(itemID)
            if not ball:
                return
            dist = long(max(minDist, min(maxDist, ball.surfaceDist)))
        fromDist = util.FmtAmt(minDist)
        toDist = util.FmtAmt(maxDist)
        if key == 'KeepAtRange':
            hint = localization.GetByLabel('UI/Inflight/SetDefaultKeepAtRangeDistanceHint', fromDist=fromDist, toDist=toDist)
            caption = localization.GetByLabel('UI/Inflight/SetDefaultKeepAtRangeDistance')
        elif key == 'Orbit':
            hint = localization.GetByLabel('UI/Inflight/SetDefaultOrbitDistanceHint', fromDist=fromDist, toDist=toDist)
            caption = localization.GetByLabel('UI/Inflight/SetDefaultOrbitDistance')
        elif key == 'WarpTo':
            hint = localization.GetByLabel('UI/Inflight/SetDefaultWarpWithinDistanceHint', fromDist=fromDist, toDist=toDist)
            caption = localization.GetByLabel('UI/Inflight/SetDefaultWarpWithinDistance')
        else:
            hint = ''
            caption = ''
        r = uix.QtyPopup(maxvalue=maxDist, minvalue=minDist, setvalue=dist, hint=hint, caption=caption, label=None, digits=0)
        if r:
            newRange = max(minDist, min(maxDist, r['qty']))
            defaultRangeUtils.UpdateRangeSetting(key, newRange)
        else:
            return
    return drange


def GetSelectedShipAndFighters():
    selectedFighterIDs = GetFightersSelectedForNavigation()
    shipIsSelected = len(selectedFighterIDs) == 0 or IsSelectedForNavigation(session.shipid)
    return (shipIsSelected, selectedFighterIDs)


def GetFightersSelectedForNavigation():
    if not CheckShipHasFighterBay(session.shipid):
        return []
    selectedItemIDs = sm.GetService('state').GetStatesForFlag(states.selectedForNavigation)
    fighterIDsInSpace = sm.GetService('fighters').shipFighterState.GetAllFighterIDsInSpace()
    return [ fighterItemID for fighterItemID in fighterIDsInSpace if fighterItemID in selectedItemIDs ]


def IsSelectedForNavigation(itemID):
    return sm.GetService('state').GetState(itemID, states.selectedForNavigation)


def SelectForNavigation(itemID):
    if not CheckShipHasFighterBay(session.shipid):
        return
    sm.GetService('state').SetState(itemID, states.selectedForNavigation, True)


def DeselectForNavigation(itemID):
    sm.GetService('state').SetState(itemID, states.selectedForNavigation, False)


def ToggleSelectForNavigation(itemID):
    if IsSelectedForNavigation(itemID):
        DeselectForNavigation(itemID)
    else:
        SelectForNavigation(itemID)


def DeselectAllForNavigation():
    sm.GetService('state').ResetByFlag(states.selectedForNavigation)


def _IsAlreadyFollowingBallAtRange(ballID, targetID, targetRange, moveMode = destiny.DSTBALL_FOLLOW):
    ball = sm.GetService('michelle').GetBall(ballID)
    if ball is None:
        return
    return ball.mode == moveMode and ball.followId == targetID and ball.followRange == targetRange


def _GetMovementDistanceOrDefault(targetID, targetRange, action, **kwargs):
    if targetRange is None:
        return GetDefaultDist(action, targetID, **kwargs)
    return targetRange


def KeepAtRange(targetID, followRange = None):
    if _IsInvalidMovementTarget(targetID):
        return
    followRange = _GetMovementDistanceOrDefault(targetID, followRange, 'KeepAtRange', minDist=const.approachRange)
    if followRange is None:
        return
    shipIsSelected, selectedFighterIDs = GetSelectedShipAndFighters()
    if shipIsSelected:
        _Ship_KeepAtRange(targetID, followRange)
    if selectedFighterIDs:
        sm.GetService('fighters').CmdMovementFollow(selectedFighterIDs, targetID, followRange)


def _Ship_KeepAtRange(targetID, followRange):
    if _IsAlreadyFollowingBallAtRange(session.shipid, targetID, followRange):
        return
    sm.GetService('space').SetIndicationTextForcefully(ballMode=destiny.DSTBALL_FOLLOW, followId=targetID, followRange=int(followRange))
    bp = sm.GetService('michelle').GetRemotePark()
    bp.CmdFollowBall(targetID, followRange)
    if not sm.GetService('machoNet').GetGlobalConfig().get('newAutoNavigationKillSwitch', False):
        sm.GetService('autoPilot').CancelSystemNavigation()
    sm.GetService('flightPredictionSvc').OptionActivated('KeepAtRange', targetID, followRange)


def Orbit(targetID, followRange = None):
    if _IsInvalidMovementTarget(targetID):
        return
    followRange = _GetMovementDistanceOrDefault(targetID, followRange, 'Orbit')
    if followRange is None:
        return
    followRange = float(followRange) if followRange < 10.0 else int(followRange)
    shipIsSelected, selectedFighterIDs = GetSelectedShipAndFighters()
    if shipIsSelected:
        _Ship_Orbit(targetID, followRange)
    if selectedFighterIDs:
        sm.GetService('fighters').CmdMovementOrbit(selectedFighterIDs, targetID, followRange)


def _Ship_Orbit(targetID, followRange):
    if _IsAlreadyFollowingBallAtRange(session.shipid, targetID, followRange, moveMode=destiny.DSTBALL_ORBIT):
        return
    sm.GetService('space').SetIndicationTextForcefully(ballMode=destiny.DSTBALL_ORBIT, followId=targetID, followRange=followRange)
    bp = sm.GetService('michelle').GetRemotePark()
    bp.CmdOrbit(targetID, followRange)
    if not sm.GetService('machoNet').GetGlobalConfig().get('newAutoNavigationKillSwitch', False):
        sm.GetService('autoPilot').CancelSystemNavigation()
    sm.GetService('flightPredictionSvc').OptionActivated('Orbit', targetID, followRange)
    try:
        slimItem = sm.GetService('michelle').GetItem(targetID)
        if slimItem:
            sm.ScatterEvent('OnClientEvent_Orbit', slimItem)
        else:
            log.LogTraceback('Failed at scattering orbit event')
    except Exception as e:
        log.LogTraceback('Failed at scattering orbit event')


def Approach(targetID, cancelAutoNavigation = True):
    if _IsInvalidMovementTarget(targetID):
        return
    shipIsSelected, selectedFighterIDs = GetSelectedShipAndFighters()
    if shipIsSelected:
        ShipApproach(targetID, cancelAutoNavigation)
    if selectedFighterIDs:
        sm.GetService('fighters').CmdMovementFollow(selectedFighterIDs, targetID, const.approachRange)


def ShipApproach(targetID, cancelAutoNavigation = True):
    autoPilot = sm.GetService('autoPilot')
    if not sm.GetService('machoNet').GetGlobalConfig().get('newAutoNavigationKillSwitch', False):
        if cancelAutoNavigation:
            autoPilot.CancelSystemNavigation()
    else:
        autoPilot.AbortWarpAndTryCommand()
        autoPilot.AbortApproachAndTryCommand(targetID)
    approachRange = const.approachRange
    if _IsAlreadyFollowingBallAtRange(session.shipid, targetID, approachRange):
        return
    sm.GetService('space').SetIndicationTextForcefully(ballMode=destiny.DSTBALL_FOLLOW, followId=targetID, followRange=approachRange)
    bp = sm.GetService('michelle').GetRemotePark()
    bp.CmdFollowBall(targetID, approachRange)
    sm.GetService('flightPredictionSvc').OptionActivated('Approach', targetID, approachRange)
    sm.ScatterEvent('OnClientEvent_Approach')


def GoToPoint(position):
    bp = sm.GetService('michelle').GetRemotePark()
    if bp is not None:
        shipIsSelected, selectedFighterIDs = GetSelectedShipAndFighters()
        if selectedFighterIDs:
            _Fighters_GoToPoint(selectedFighterIDs, position)
        if shipIsSelected:
            _Ship_GoToPoint(bp, position)


def _Ship_GoToPoint(bp, position):
    if not sm.GetService('machoNet').GetGlobalConfig().get('newAutoNavigationKillSwitch', False):
        sm.GetService('autoPilot').CancelSystemNavigation()
    bp.CmdGotoPoint(*position)


def _Fighters_GoToPoint(fighterIDs, position):
    fighterSvc = sm.GetService('fighters')
    fighterSvc.CmdGotoPoint(fighterIDs, position)


def GetWarpToRanges():
    ranges = [const.minWarpEndDistance,
     (const.minWarpEndDistance / 10000 + 1) * 10000,
     (const.minWarpEndDistance / 10000 + 2) * 10000,
     (const.minWarpEndDistance / 10000 + 3) * 10000,
     (const.minWarpEndDistance / 10000 + 5) * 10000,
     (const.minWarpEndDistance / 10000 + 7) * 10000,
     const.maxWarpEndDistance]
    return ranges


def DockOrJumpOrActivateGate(itemID):
    if _IsInvalidMovementTarget(itemID):
        return
    bp = sm.StartService('michelle').GetBallpark()
    menuSvc = sm.GetService('menu')
    if bp:
        item = bp.GetInvItem(itemID)
        if item.groupID == const.groupStation:
            menuSvc.DockStation(itemID)
        elif item.categoryID == const.categoryStructure:
            sm.GetService('structureDocking').Dock(itemID)
        elif item.groupID == const.groupStargate:
            bp = sm.StartService('michelle').GetBallpark()
            slimItem = bp.slimItems.get(itemID)
            if slimItem:
                jump = slimItem.jumps[0]
                if not jump:
                    return
                menuSvc.StargateJump(itemID, jump.toCelestialID, jump.locationID)
        elif item.groupID == const.groupWarpGate:
            menuSvc.ActivateAccelerationGate(itemID)


def _IsInvalidMovementTarget(itemID):
    if sm.GetService('michelle').GetRemotePark() is None:
        return False
    return itemID == session.shipid or sm.GetService('sensorSuite').IsSiteBall(itemID)


def ApproachLocation(bookmark):
    bp = sm.StartService('michelle').GetRemotePark()
    if bp:
        if getattr(bookmark, 'agentID', 0) and hasattr(bookmark, 'locationNumber'):
            referringAgentID = getattr(bookmark, 'referringAgentID', None)
            sm.StartService('agents').GetAgentMoniker(bookmark.agentID).GotoLocation(bookmark.locationType, bookmark.locationNumber, referringAgentID)
        else:
            bp.CmdGotoBookmark(bookmark.bookmarkID)
            sm.ScatterEvent('OnClientEvent_Approach')


def WarpToBookmark(bookmark, warpRange = 20000.0, fleet = False):
    bp = sm.StartService('michelle').GetRemotePark()
    if bp:
        if getattr(bookmark, 'agentID', 0) and hasattr(bookmark, 'locationNumber'):
            referringAgentID = getattr(bookmark, 'referringAgentID', None)
            sm.StartService('agents').GetAgentMoniker(bookmark.agentID).WarpToLocation(bookmark.locationType, bookmark.locationNumber, warpRange, fleet, referringAgentID)
        else:
            if not sm.GetService('machoNet').GetGlobalConfig().get('newAutoNavigationKillSwitch', False):
                sm.GetService('autoPilot').CancelSystemNavigation()
            bp.CmdWarpToStuff('bookmark', bookmark.bookmarkID, minRange=warpRange, fleet=fleet)
            sm.StartService('space').WarpDestination(bookmarkID=bookmark.bookmarkID)


def WarpFleetToBookmark(bookmark, warpRange = 20000.0, fleet = True):
    bp = sm.StartService('michelle').GetRemotePark()
    if bp:
        if getattr(bookmark, 'agentID', 0) and hasattr(bookmark, 'locationNumber'):
            referringAgentID = getattr(bookmark, 'referringAgentID', None)
            sm.StartService('agents').GetAgentMoniker(bookmark.agentID).WarpToLocation(bookmark.locationType, bookmark.locationNumber, warpRange, fleet, referringAgentID)
        else:
            if not sm.GetService('machoNet').GetGlobalConfig().get('newAutoNavigationKillSwitch', False):
                sm.GetService('autoPilot').CancelSystemNavigation()
            bp.CmdWarpToStuff('bookmark', bookmark.bookmarkID, minRange=warpRange, fleet=fleet)


def WarpToItem(itemID, warpRange = None, cancelAutoNavigation = True):
    if itemID == session.shipid:
        return
    siteBracket = sm.GetService('sensorSuite').GetBracketByBallID(itemID)
    if siteBracket:
        siteBracket.data.WarpToAction(None, warpRange)
        return
    if warpRange is None:
        warprange = sm.GetService('menu').GetDefaultActionDistance('WarpTo')
    else:
        warprange = warpRange
    bp = sm.StartService('michelle').GetRemotePark()
    if bp is not None and sm.StartService('space').CanWarp(itemID):
        if not sm.GetService('machoNet').GetGlobalConfig().get('newAutoNavigationKillSwitch', False):
            if cancelAutoNavigation:
                sm.GetService('autoPilot').CancelSystemNavigation()
        else:
            sm.GetService('autoPilot').AbortWarpAndTryCommand(itemID)
            sm.GetService('autoPilot').AbortApproachAndTryCommand()
        bp.CmdWarpToStuff('item', itemID, minRange=warprange)
        sm.StartService('space').WarpDestination(celestialID=itemID)
        sm.GetService('flightPredictionSvc').OptionActivated('AlignTo', itemID)


def WarpToDistrict(districtID, warpRange = None, cancelAutoNavigation = True):
    if warpRange is None:
        warprange = sm.GetService('menu').GetDefaultActionDistance('WarpTo')
    else:
        warprange = warpRange
    bp = sm.StartService('michelle').GetRemotePark()
    if bp is not None and sm.StartService('space').CanWarp(districtID):
        if not sm.GetService('machoNet').GetGlobalConfig().get('newAutoNavigationKillSwitch', False):
            if cancelAutoNavigation:
                sm.GetService('autoPilot').CancelSystemNavigation()
        else:
            sm.GetService('autoPilot').AbortWarpAndTryCommand(districtID)
            sm.GetService('autoPilot').AbortApproachAndTryCommand()
        bp.CmdWarpToStuff('district', districtID, minRange=warprange)


def RealDock(itemID):
    bp = sm.StartService('michelle').GetBallpark()
    if not bp:
        return
    if sm.GetService('viewState').HasActiveTransition():
        return
    eve.Message('OnDockingRequest')
    eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Inflight/RequestToDockAt', station=itemID)})
    paymentRequired = 0
    try:
        bp = sm.GetService('michelle').GetRemotePark()
        if bp is not None:
            log.LogNotice('Docking', itemID)
            if uicore.uilib.Key(uiconst.VK_CONTROL) and uicore.uilib.Key(uiconst.VK_SHIFT) and uicore.uilib.Key(uiconst.VK_MENU) and session.role & service.ROLE_GML:
                success = sm.GetService('sessionMgr').PerformSessionChange('dock', bp.CmdTurboDock, itemID)
            else:
                success = sm.GetService('sessionMgr').PerformSessionChange('dock', bp.CmdDock, itemID, session.shipid)
    except UserError as e:
        if e.msg == 'DockingRequestDeniedPaymentRequired':
            sys.exc_clear()
            paymentRequired = e.args[1]['amount']
        else:
            raise
    except Exception as e:
        raise

    if paymentRequired:
        if eve.Message('AskPayDockingFee', {'cost': paymentRequired}, uiconst.YESNO) == uiconst.ID_YES:
            bp = sm.GetService('michelle').GetRemotePark()
            if bp is not None:
                session.ResetSessionChangeTimer('Retrying with docking payment')
                if uicore.uilib.Key(uiconst.VK_CONTROL) and session.role & service.ROLE_GML:
                    sm.GetService('sessionMgr').PerformSessionChange('dock', bp.CmdTurboDock, itemID, paymentRequired)
                else:
                    sm.GetService('sessionMgr').PerformSessionChange('dock', bp.CmdDock, itemID, session.shipid, paymentRequired)


def RealActivateAccelerationGate(itemID):
    if eve.rookieState and not sm.StartService('tutorial').CheckAccelerationGateActivation():
        return
    sm.StartService('sessionMgr').PerformSessionChange(localization.GetByLabel('UI/Inflight/ActivateGate'), sm.RemoteSvc('keeper').ActivateAccelerationGate, itemID, violateSafetyTimer=1)
    log.LogNotice('Acceleration Gate activated to ', itemID)


def RealEnterWormhole(itemID):
    fromSecClass = sm.StartService('map').GetSecurityClass(session.solarsystemid)
    if fromSecClass == const.securityClassHighSec and eve.Message('WormholeJumpingFromHiSec', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
        return
    log.LogNotice('Wormhole Jump from', session.solarsystemid2, 'to', itemID)
    sm.StartService('sessionMgr').PerformSessionChange(localization.GetByLabel('UI/Inflight/EnterWormhole'), sm.RemoteSvc('wormholeMgr').WormholeJump, itemID)


def GetGlobalActiveItemKeyName(forWhat):
    key = None
    actions = ['UI/Inflight/OrbitObject', 'UI/Inflight/Submenus/KeepAtRange', DefaultWarpToLabel()[0]]
    if forWhat in actions:
        idx = actions.index(forWhat)
        key = ['Orbit', 'KeepAtRange', 'WarpTo'][idx]
    return key


def DefaultWarpToLabel():
    defaultWarpDist = sm.GetService('menu').GetDefaultActionDistance('WarpTo')
    label = uiutil.MenuLabel('UI/Inflight/WarpToWithinDistance', {'distance': util.FmtDist(float(defaultWarpDist))})
    return label
