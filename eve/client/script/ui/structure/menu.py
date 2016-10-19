#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\menu.py
import const
import structures
import carbon.common.script.sys.serviceConst as service
from carbonui.control.menuLabel import MenuLabel
from eve.client.script.ui.services.menuSvcExtras import menuFunctions

def GetStructureMenu(item):
    entries = []
    if item.categoryID == const.categoryStructure:
        state = getattr(item, 'state', structures.STATE_UNKNOWN)
        isElevatedPlayer = session.role & service.ROLEMASK_ELEVATEDPLAYER
        checkIsMyCorps = item.ownerID == session.corpid
        checkAmDirector = session.corprole & const.corpRoleDirector > 0
        checkOnline = state not in structures.OFFLINE_STATES
        if checkOnline and checkIsMyCorps and checkAmDirector:
            entries.append([MenuLabel('UI/Inflight/POS/TransferSovStructureOwnership'), menuFunctions.TransferCorporationOwnership, [item.itemID]])
        if session.shipid == item.itemID:
            entries.append([MenuLabel('UI/Inflight/HUDOptions/ReleaseControl'), sm.GetService('structureControl').Alight, [item.itemID]])
        elif session.structureid == item.itemID:
            entries.append([MenuLabel('UI/Neocom/UndockBtn'), sm.GetService('structureDocking').Undock, [item.itemID]])
            if isElevatedPlayer:
                entries.append([MenuLabel('UI/Commands/TakeStructureControl'), sm.GetService('structureControl').Board, [item.itemID]])
        if isElevatedPlayer:
            entries.append(['GM: Vulnerability Schedule', OpenVulnerabilityScheduleWnd, [item.itemID, item.typeID]])
            states = [ [name, GMSetStructureState, [item.itemID, value]] for value, name in structures.STATES.iteritems() ]
            entries.append(['GM: Set State', states])
            times = [ ['{} seconds'.format(time), GMSetStructureTimer, [item.itemID, time]] for time in [5,
             15,
             60,
             600,
             6000] ]
            entries.append(['GM: Set Timer', times])
            unanchoring = [['Start Unanchoring', GMSetStructureUnanchoring, [item.itemID]], ['Cancel Unanchoring', GMSetStructureUnanchoring, [item.itemID, 'cancel']]]
            unanchoring += [ ['{} seconds'.format(time), GMSetStructureUnanchoring, [item.itemID, time]] for time in [5,
             15,
             60,
             600,
             6000] ]
            entries.append(['GM: Set Unanchoring', unanchoring])
    return entries


def GMSetStructureState(structureID, state):
    sm.RemoteSvc('slash').SlashCmd('/structure state %d %d' % (structureID, state))


def GMSetStructureTimer(structureID, seconds):
    sm.RemoteSvc('slash').SlashCmd('/structure timer %d %d' % (structureID, seconds))


def GMSetStructureUnanchoring(structureID, action = ''):
    sm.RemoteSvc('slash').SlashCmd('/structure unanchor %d %s' % (structureID, action))


def OpenVulnerabilityScheduleWnd(itemID, typeID):
    from eve.client.script.ui.structure.structureSettings.schedule.vulnerabilityScheduleWnd import VulnerabilityScheduleWnd
    requiredHours = int(sm.GetService('clientDogmaIM').GetDogmaLocation().GetModifiedTypeAttribute(typeID, const.attributeVulnerabilityRequired))
    thisWeek, nextWeek = sm.RemoteSvc('structureVulnerability').GetSchedule(itemID)
    VulnerabilityScheduleWnd(infoOnStructures=[(itemID,
      session.solarsystemid2,
      thisWeek,
      nextWeek)], requiredHours=requiredHours)
