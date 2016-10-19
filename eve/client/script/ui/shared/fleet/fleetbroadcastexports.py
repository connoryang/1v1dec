#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fleet\fleetbroadcastexports.py
from eve.common.script.sys.eveCfg import InShipInSpace
import util
import state
import evefleet.const as fleetConst
import types
from inventorycommon.const import groupTitan, groupBlackOps
import localization
import uiutil
from eve.client.script.ui.services.menuSvcExtras.movementFunctions import WarpToItem
activeBroadcastColor = 'ddffffff'
flagToName = {state.gbEnemySpotted: 'EnemySpotted',
 state.gbTarget: 'Target',
 state.gbHealShield: 'HealShield',
 state.gbHealArmor: 'HealArmor',
 state.gbHealCapacitor: 'HealCapacitor',
 state.gbWarpTo: 'WarpTo',
 state.gbNeedBackup: 'NeedBackup',
 state.gbAlignTo: 'AlignTo',
 state.gbJumpTo: 'JumpTo',
 state.gbInPosition: 'InPosition',
 state.gbHoldPosition: 'HoldPosition',
 state.gbTravelTo: 'TravelTo',
 state.gbJumpBeacon: 'JumpBeacon',
 state.gbLocation: 'Location'}
types = {'EnemySpotted': {'bigIcon': 'res:/UI/Texture/Icons/44_32_51.png',
                  'smallIcon': 'res:/UI/Texture/Icons/38_16_88.png'},
 'Target': {'bigIcon': 'res:/UI/Texture/Icons/44_32_17.png',
            'smallIcon': 'res:/UI/Texture/Icons/38_16_72.png'},
 'HealArmor': {'bigIcon': 'res:/UI/Texture/Icons/44_32_53.png',
               'smallIcon': 'res:/UI/Texture/Icons/38_16_74.png'},
 'HealShield': {'bigIcon': 'res:/UI/Texture/Icons/44_32_52.png',
                'smallIcon': 'res:/UI/Texture/Icons/38_16_73.png'},
 'HealCapacitor': {'bigIcon': 'res:/UI/Texture/Icons/44_32_54.png',
                   'smallIcon': 'res:/UI/Texture/Icons/38_16_75.png'},
 'WarpTo': {'bigIcon': 'res:/UI/Texture/Icons/44_32_55.png',
            'smallIcon': 'res:/UI/Texture/Icons/38_16_76.png'},
 'NeedBackup': {'bigIcon': 'res:/UI/Texture/Icons/44_32_56.png',
                'smallIcon': 'res:/UI/Texture/Icons/38_16_77.png'},
 'AlignTo': {'bigIcon': 'res:/UI/Texture/Icons/44_32_57.png',
             'smallIcon': 'res:/UI/Texture/Icons/38_16_78.png'},
 'JumpTo': {'bigIcon': 'res:/UI/Texture/Icons/44_32_39.png',
            'smallIcon': 'res:/UI/Texture/Icons/38_16_86.png'},
 'TravelTo': {'bigIcon': 'res:/UI/Texture/Icons/44_32_58.png',
              'smallIcon': 'res:/UI/Texture/Icons/38_16_87.png'},
 'InPosition': {'bigIcon': 'res:/UI/Texture/Icons/44_32_49.png',
                'smallIcon': 'res:/UI/Texture/Icons/38_16_70.png'},
 'HoldPosition': {'bigIcon': 'res:/UI/Texture/Icons/44_32_50.png',
                  'smallIcon': 'res:/UI/Texture/Icons/38_16_71.png'},
 'JumpBeacon': {'bigIcon': 'res:/UI/Texture/Icons/44_32_58.png',
                'smallIcon': 'res:/UI/Texture/Icons/38_16_76.png'},
 'Location': {'bigIcon': 'res:/UI/Texture/Icons/44_32_58.png',
              'smallIcon': 'res:/UI/Texture/Icons/38_16_87.png'}}
defaultIcon = ['res:/UI/Texture/Icons/44_32_29.png', 'res:/UI/Texture/Icons/38_16_70.png']
broadcastNames = {'EnemySpotted': 'UI/Fleet/FleetBroadcast/Commands/EnemySpotted',
 'Target': 'UI/Fleet/FleetBroadcast/Commands/BroadcastTarget',
 'HealArmor': 'UI/Fleet/FleetBroadcast/Commands/HealArmor',
 'HealShield': 'UI/Fleet/FleetBroadcast/Commands/HealShield',
 'HealCapacitor': 'UI/Fleet/FleetBroadcast/Commands/HealCapacitor',
 'WarpTo': 'UI/Fleet/FleetBroadcast/Commands/BroadcastWarpTo',
 'NeedBackup': 'UI/Fleet/FleetBroadcast/Commands/NeedBackup',
 'AlignTo': 'UI/Fleet/FleetBroadcast/Commands/BroadcastAlignTo',
 'JumpTo': 'UI/Fleet/FleetBroadcast/Commands/BroadcastJumpTo',
 'TravelTo': 'UI/Fleet/FleetBroadcast/Commands/BroadcastTravelTo',
 'InPosition': 'UI/Fleet/FleetBroadcast/Commands/InPosition',
 'HoldPosition': 'UI/Fleet/FleetBroadcast/Commands/HoldPosition',
 'JumpBeacon': 'UI/Fleet/FleetBroadcast/Commands/JumpBeacon',
 'Location': 'UI/Fleet/FleetBroadcast/Commands/Location',
 'Event': 'UI/Fleet/FleetBroadcast/FleetEvent'}
broadcastScopes = {fleetConst.BROADCAST_DOWN: {fleetConst.BROADCAST_UNIVERSE: 'UI/Fleet/FleetBroadcast/BroadcastRangeDown',
                             fleetConst.BROADCAST_SYSTEM: 'UI/Fleet/FleetBroadcast/BroadcastRangeDownSystem',
                             fleetConst.BROADCAST_BUBBLE: 'UI/Fleet/FleetBroadcast/BroadcastRangeDownBubble'},
 fleetConst.BROADCAST_UP: {fleetConst.BROADCAST_UNIVERSE: 'UI/Fleet/FleetBroadcast/BroadcastRangeUp',
                           fleetConst.BROADCAST_SYSTEM: 'UI/Fleet/FleetBroadcast/BroadcastRangeUpSystem',
                           fleetConst.BROADCAST_BUBBLE: 'UI/Fleet/FleetBroadcast/BroadcastRangeUpBubble'},
 fleetConst.BROADCAST_ALL: {fleetConst.BROADCAST_UNIVERSE: 'UI/Fleet/FleetBroadcast/BroadcastRangeAll',
                            fleetConst.BROADCAST_SYSTEM: 'UI/Fleet/FleetBroadcast/BroadcastRangeAllSystem',
                            fleetConst.BROADCAST_BUBBLE: 'UI/Fleet/FleetBroadcast/BroadcastRangeAllBubble'}}
broadcastRanges = {'Target': fleetConst.BROADCAST_BUBBLE,
 'HealArmor': fleetConst.BROADCAST_BUBBLE,
 'HealShield': fleetConst.BROADCAST_BUBBLE,
 'HealCapacitor': fleetConst.BROADCAST_BUBBLE,
 'WarpTo': fleetConst.BROADCAST_SYSTEM,
 'AlignTo': fleetConst.BROADCAST_SYSTEM,
 'JumpTo': fleetConst.BROADCAST_SYSTEM}
defaultBroadcastRange = fleetConst.BROADCAST_UNIVERSE
broadcastRangeNames = {fleetConst.BROADCAST_UNIVERSE: 'UI/Fleet/FleetBroadcast/BroadcastRangeGlobal',
 fleetConst.BROADCAST_SYSTEM: 'UI/Fleet/FleetBroadcast/BroadcastRangeSystem',
 fleetConst.BROADCAST_BUBBLE: 'UI/Fleet/FleetBroadcast/BroadcastRangeBubble'}

def ShouldListen(gbName, senderRole, senderJob, senderWingID, senderSquadID):
    return settings.user.ui.Get('listenBroadcast_%s' % gbName, True) or senderRole == fleetConst.fleetRoleLeader or senderJob == fleetConst.fleetJobCreator or senderRole == fleetConst.fleetRoleWingCmdr and senderWingID == session.wingid or senderRole == fleetConst.fleetRoleSquadCmdr and senderSquadID == session.squadid


def FilteredBroadcast(f, name):

    def deco(self, senderID, *args, **kw):
        rec = sm.GetService('fleet').GetMembers().get(senderID)
        if not rec or ShouldListen(name, rec.role, rec.job, rec.wingID, rec.squadID):
            f(self, senderID, *args, **kw)

    return deco


def MenuGetter(gbType, *args):
    GetMenu = globals()['GetMenu_%s' % gbType]
    return lambda : GetMenu(*args)


def GetMenu_EnemySpotted(charID, locationID, nearID):
    where = Where(charID, locationID)
    menuSvc = sm.GetService('menu')
    m = []
    if where in (inSystem, inBubble):
        defaultWarpDist = menuSvc.GetDefaultActionDistance('WarpTo')
        m.extend([[uiutil.MenuLabel('UI/Fleet/WarpToMember'), menuSvc.WarpToMember, (charID, float(defaultWarpDist))],
         [uiutil.MenuLabel('UI/Fleet/WarpToMemberSubmenuOption'), menuSvc.WarpToMenu(menuSvc.WarpToMember, charID)],
         [uiutil.MenuLabel('UI/Fleet/WarpFleetToMember'), menuSvc.WarpFleetToMember, (charID, float(defaultWarpDist))],
         [uiutil.MenuLabel('UI/Fleet/FleetSubmenus/WarpFleetToMember'), menuSvc.WarpToMenu(menuSvc.WarpFleetToMember, charID)]])
    else:
        m.extend(GetMenu_TravelTo(charID, locationID, nearID))
    return m


GetMenu_NeedBackup = GetMenu_InPosition = GetMenu_EnemySpotted

def GetMenu_TravelTo(charID, solarSystemID, destinationID):
    destinationID = destinationID or solarSystemID
    starmapSvc = sm.GetService('starmap')
    waypoints = starmapSvc.GetWaypoints()
    m = [[uiutil.MenuLabel('UI/Inflight/SetDestination'), starmapSvc.SetWaypoint, (destinationID, True)]]
    if destinationID in waypoints:
        m.append([uiutil.MenuLabel('UI/Inflight/RemoveWaypoint'), starmapSvc.ClearWaypoints, (destinationID,)])
    else:
        m.append([uiutil.MenuLabel('UI/Inflight/AddWaypoint'), starmapSvc.SetWaypoint, (destinationID,)])
    return m


def GetMenu_Location(charID, solarSystemID, nearID):
    if solarSystemID != session.solarsystemid2:
        m = GetMenu_TravelTo(charID, solarSystemID, None)
        m.append([uiutil.MenuLabel('UI/Fleet/FleetSubmenus/ShowDistance'), sm.GetService('fleet').DistanceToFleetMate, (solarSystemID, nearID)])
    else:
        m = GetMenu_WarpTo(charID, solarSystemID, nearID)
    return m


def GetMenu_JumpBeacon(charID, solarSystemID, itemID):
    menuSvc = sm.GetService('menu')
    starmapSvc = sm.GetService('starmap')
    waypoints = starmapSvc.GetWaypoints()
    beacon = (solarSystemID, itemID)
    m = [[uiutil.MenuLabel('UI/Inflight/JumpToFleetMember'), menuSvc.JumpToBeaconFleet, (charID, beacon)]]
    isTitan = False
    if session.solarsystemid and session.shipid:
        ship = sm.GetService('godma').GetItem(session.shipid)
        if ship.groupID in [groupTitan, groupBlackOps]:
            isTitan = True
    if isTitan:
        m.append([uiutil.MenuLabel('UI/Fleet/BridgeToMember'), menuSvc.BridgeToBeacon, (charID, beacon)])
    m.append(None)
    m.append([uiutil.MenuLabel('UI/Inflight/SetDestination'), starmapSvc.SetWaypoint, (solarSystemID, True)])
    if solarSystemID in waypoints:
        m.append([uiutil.MenuLabel('UI/Inflight/RemoveWaypoint'), starmapSvc.ClearWaypoints, (solarSystemID,)])
    else:
        m.append([uiutil.MenuLabel('UI/Inflight/AddWaypoint'), starmapSvc.SetWaypoint, (solarSystemID,)])
    return m


def GetMenu_WarpTo(charID, solarSystemID, locationID):
    return GetWarpLocationMenu(locationID)


def GetWarpLocationMenu(locationID):
    if not InShipInSpace():
        return []
    menuSvc = sm.GetService('menu')
    defaultWarpDist = menuSvc.GetDefaultActionDistance('WarpTo')
    ret = [[uiutil.MenuLabel('UI/Inflight/WarpToBookmark'), WarpToItem, (locationID, float(defaultWarpDist))], [uiutil.MenuLabel('UI/Inflight/Submenus/WarpToWithin'), menuSvc.WarpToMenu(WarpToItem, locationID)], [uiutil.MenuLabel('UI/Inflight/AlignTo'), menuSvc.AlignTo, (locationID,)]]
    if session.fleetrole == fleetConst.fleetRoleLeader:
        ret.extend([[uiutil.MenuLabel('UI/Fleet/WarpFleetToLocation'), menuSvc.WarpFleet, (locationID, float(defaultWarpDist))], [uiutil.MenuLabel('UI/Fleet/FleetSubmenus/WarpFleetToLocationWithin'), menuSvc.WarpToMenu(menuSvc.WarpFleet, locationID)]])
    elif session.fleetrole == fleetConst.fleetRoleWingCmdr:
        ret.extend([[uiutil.MenuLabel('UI/Fleet/WarpWingToLocation'), menuSvc.WarpFleet, (locationID, float(defaultWarpDist))], [uiutil.MenuLabel('UI/Fleet/FleetSubmenus/WarpWingToLocationWithin'), menuSvc.WarpToMenu(menuSvc.WarpFleet, locationID)]])
    elif session.fleetrole == fleetConst.fleetRoleSquadCmdr:
        ret.extend([[uiutil.MenuLabel('UI/Fleet/WarpSquadToLocation'), menuSvc.WarpFleet, (locationID, float(defaultWarpDist))], [uiutil.MenuLabel('UI/Fleet/FleetSubmenus/WarpSquadToLocationWithin'), menuSvc.WarpToMenu(menuSvc.WarpFleet, locationID)]])
    return ret


def GetMenu_Target(charID, solarSystemID, shipID):
    m = []
    targetSvc = sm.GetService('target')
    targets = targetSvc.GetTargets()
    if not targetSvc.BeingTargeted(shipID) and shipID not in targets:
        m = [(uiutil.MenuLabel('UI/Inflight/LockTarget'), targetSvc.TryLockTarget, (shipID,))]
    return m


def GetMenu_Member(charID):
    m = [(uiutil.MenuLabel('UI/Fleet/Ranks/FleetMember'), sm.GetService('menu').FleetMenu(charID, unparsed=False))]
    return m


def GetMenu_Ignore(name):
    isListen = settings.user.ui.Get('listenBroadcast_%s' % name, True)
    if isListen:
        m = [(uiutil.MenuLabel('UI/Fleet/FleetBroadcast/IgnoreBroadcast'), sm.GetService('fleet').SetListenBroadcast, (name, False))]
    else:
        m = [(uiutil.MenuLabel('UI/Fleet/FleetBroadcast/UnignoreBroadcast'), sm.GetService('fleet').SetListenBroadcast, (name, True))]
    return m


def GetMenu_HealArmor(charID, solarSystemID, shipID):
    return GetMenu_Target(charID, solarSystemID, shipID)


def GetMenu_HealShield(charID, solarSystemID, shipID):
    return GetMenu_Target(charID, solarSystemID, shipID)


def GetMenu_HealCapacitor(charID, solarSystemID, shipID):
    return GetMenu_Target(charID, solarSystemID, shipID)


def GetMenu_JumpTo(charID, solarSystemID, locationID):
    return GetMenu_WarpTo(charID, solarSystemID, locationID)


def GetMenu_AlignTo(charID, solarSystemID, locationID):
    return GetMenu_WarpTo(charID, solarSystemID, locationID)


def _Rank(role):
    if not hasattr(_Rank, 'ranks'):
        _Rank.ranks = {fleetConst.fleetRoleLeader: 4,
         fleetConst.fleetRoleWingCmdr: 3,
         fleetConst.fleetRoleSquadCmdr: 2,
         fleetConst.fleetRoleMember: 1}
    return _Rank.ranks.get(role, -1)


def GetRankName(member):
    if member.job & fleetConst.fleetJobCreator:
        if member.role == fleetConst.fleetRoleLeader:
            return localization.GetByLabel('UI/Fleet/Ranks/FleetCommanderBoss')
        elif member.role == fleetConst.fleetRoleWingCmdr:
            return localization.GetByLabel('UI/Fleet/Ranks/WingCommanderBoss')
        elif member.role == fleetConst.fleetRoleSquadCmdr:
            return localization.GetByLabel('UI/Fleet/Ranks/SquadCommanderBoss')
        elif member.role == fleetConst.fleetRoleMember:
            return localization.GetByLabel('UI/Fleet/Ranks/SquadMemberBoss')
        else:
            return localization.GetByLabel('UI/Fleet/Ranks/NonMember')
    else:
        return GetRoleName(member.role)


def GetBoosterName(roleBooster):
    boosternames = {fleetConst.fleetBoosterFleet: localization.GetByLabel('UI/Fleet/Ranks/FleetBooster'),
     fleetConst.fleetBoosterWing: localization.GetByLabel('UI/Fleet/Ranks/WingBooster'),
     fleetConst.fleetBoosterSquad: localization.GetByLabel('UI/Fleet/Ranks/SquadBooster')}
    name = boosternames.get(roleBooster, '')
    return name


def GetRoleName(role):
    if role == fleetConst.fleetRoleLeader:
        return localization.GetByLabel('UI/Fleet/Ranks/FleetCommander')
    elif role == fleetConst.fleetRoleWingCmdr:
        return localization.GetByLabel('UI/Fleet/Ranks/WingCommander')
    elif role == fleetConst.fleetRoleSquadCmdr:
        return localization.GetByLabel('UI/Fleet/Ranks/SquadCommander')
    elif role == fleetConst.fleetRoleMember:
        return localization.GetByLabel('UI/Fleet/Ranks/SquadMember')
    else:
        return localization.GetByLabel('UI/Fleet/Ranks/NonMember')


def _ICareAbout(*args):

    def MySuperior(role, wingID, squadID):
        return _Rank(role) > _Rank(session.fleetrole) and wingID in (session.wingid, -1) and squadID in (session.squadid, -1)

    def SubordinateICareAbout(role, wingID, squadID):
        return role != fleetConst.fleetRoleMember and _Rank(role) == _Rank(session.fleetrole) - 1 and session.wingid in (-1, wingID)

    return MySuperior(*args) or SubordinateICareAbout(*args)


inBubble = 1
inSystem = 2
exSystem = 3

def Where(charID, locationID = None):
    if util.SlimItemFromCharID(charID) is not None:
        return inBubble
    elif locationID in (None, session.solarsystemid):
        return inSystem
    else:
        return exSystem


def GetRoleIconFromCharID(charID):
    if charID is None:
        return
    info = sm.GetService('fleet').GetMemberInfo(int(charID))
    if info is None:
        return
    if info.job & fleetConst.fleetJobCreator:
        iconRole = '73_20'
    else:
        iconRole = {fleetConst.fleetRoleLeader: '73_17',
         fleetConst.fleetRoleWingCmdr: '73_18',
         fleetConst.fleetRoleSquadCmdr: '73_19'}.get(info.role, None)
    return iconRole


def GetVoiceMenu(entry, charID = None, channel = None):
    if entry:
        charID = entry.sr.node.charID
        channel = entry.sr.node.channel
    m = []
    charID = int(charID)
    if channel:
        state = sm.GetService('fleet').GetVoiceChannelState(channel)
        vivoxSvc = sm.GetService('vivox')
        if state in [fleetConst.CHANNELSTATE_LISTENING, fleetConst.CHANNELSTATE_SPEAKING, fleetConst.CHANNELSTATE_MAYSPEAK]:
            m.append((uiutil.MenuLabel('UI/Chat/ChannelWindow/LeaveChannel'), vivoxSvc.LeaveChannel, (channel,)))
            if vivoxSvc.GetSpeakingChannel() != channel:
                m.append((uiutil.MenuLabel('UI/Chat/MakeSpeakingChannel'), vivoxSvc.SetSpeakingChannel, (channel,)))
        elif type(channel) is not types.TupleType or not channel[0].startswith('inst'):
            m.append((uiutil.MenuLabel('UI/Chat/ChannelWindow/JoinChannel'), vivoxSvc.JoinChannel, (channel,)))
        m.append(None)
    m += sm.GetService('menu').CharacterMenu(charID)
    return m


def GetBroadcastScopeName(scope, where = fleetConst.BROADCAST_UNIVERSE):
    labelName = broadcastScopes.get(scope, {}).get(where, 'UI/Fleet/FleetBroadcast/BroadcastRangeAll')
    return localization.GetByLabel(labelName)


def GetBroadcastWhere(name):
    return broadcastRanges.get(name, defaultBroadcastRange)


def GetBroadcastWhereName(scope):
    return localization.GetByLabel(broadcastRangeNames[scope])


def GetBroadcastName(broadcastType):
    return localization.GetByLabel(broadcastNames[broadcastType])


import carbon.common.script.util.autoexport as autoexport
exports = autoexport.AutoExports('fleetbr', locals())
