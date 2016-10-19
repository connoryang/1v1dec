#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\neocom\charsheet\charSheetUtil.py
import evetypes
from carbon.common.script.util.format import FmtDate
from carbonui.control.menuLabel import MenuLabel
from crimewatch.util import GetKillReportHashValue
from eve.client.script.ui.control import entries
from eve.client.script.ui.shared.killReportUtil import OpenKillReport, CleanKillMail
from eve.common.script.util.eveCommonUtils import GetPublicCrestUrl, CombatLog_CopyText
from localization import GetByLabel
from utillib import KeyVal
import blue

def GetMedalScrollEntries(charID, noHeaders = False, publicOnly = False):
    scrolllist = []
    inDecoList = []
    publicDeco = (sm.StartService('medals').GetMedalsReceivedWithFlag(charID, [3]), GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/Public'))
    privateDeco = (sm.StartService('medals').GetMedalsReceivedWithFlag(charID, [2]), GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/Private'))
    _, characterMedalInfo = sm.StartService('medals').GetMedalsReceived(charID)
    if publicOnly:
        t = (publicDeco,)
    else:
        t = (publicDeco, privateDeco)
    for deco, hint in t:
        if deco and not noHeaders:
            scrolllist.append(entries.Get('Header', {'label': hint}))
        for medalID, medalData in deco.iteritems():
            if medalID in inDecoList:
                continue
            inDecoList.append(medalID)
            details = characterMedalInfo.Filter('medalID')
            if details and details.has_key(medalID):
                details = details.get(medalID)
            entry = sm.StartService('info').GetMedalEntry(medalData, details, 0)
            if entry:
                scrolllist.append(entry)

    return scrolllist


def GetCombatEntries(recent, filterText = ''):
    showAsCondensed = settings.user.ui.Get('charsheet_condensedcombatlog', 0)
    if showAsCondensed:
        headers = [GetByLabel('UI/Common/Date'),
         GetByLabel('UI/Common/Type'),
         GetByLabel('UI/Common/Name'),
         GetByLabel('UI/Common/Corporation'),
         GetByLabel('UI/Common/Alliance'),
         GetByLabel('UI/Common/Faction')]
    else:
        headers = []
    primeEveOwners = set()
    primeEveLocations = set()
    primeCorps = set()
    primeAlliances = set()
    ret = []
    unknownShipLabel = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/KillsTabs/UnknownShip')
    unknownNameLabel = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/KillsTabs/UnknownName')
    unknownCorporationLabel = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/KillsTabs/UnknownCorporation')
    unknownAllianceLabel = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/KillsTabs/UnknownAlliance')
    unknownFactionLabel = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/KillsTabs/UnknownFaction')
    for kill in recent:
        primeEveLocations.add(kill.solarSystemID)
        primeEveLocations.add(kill.moonID)
        primeEveOwners.add(kill.victimCharacterID)
        primeEveOwners.add(kill.victimCorporationID)
        primeCorps.add(kill.victimCorporationID)
        primeEveOwners.add(kill.victimAllianceID)
        primeAlliances.add(kill.victimAllianceID)
        primeEveOwners.add(kill.victimFactionID)
        primeEveOwners.add(kill.finalCharacterID)
        primeEveOwners.add(kill.finalCorporationID)
        primeCorps.add(kill.finalCorporationID)
        primeEveOwners.add(kill.finalAllianceID)
        primeAlliances.add(kill.finalAllianceID)
        primeEveOwners.add(kill.finalFactionID)

    cfg.eveowners.Prime(filter(None, primeEveOwners))
    cfg.evelocations.Prime(filter(None, primeEveLocations))
    cfg.corptickernames.Prime(filter(None, primeCorps))
    cfg.allianceshortnames.Prime(filter(None, primeAlliances))

    def GetOwnerName(ownerID):
        owner = cfg.eveowners.GetIfExists(ownerID)
        return getattr(owner, 'name', '')

    def GetTypeName(typeID):
        try:
            return evetypes.GetName(typeID)
        except evetypes.TypeNotFoundException:
            return ''

    def FilterOut(kill):
        if not filterText:
            return False
        if GetTypeName(kill.victimShipTypeID).lower().find(filterText) >= 0:
            return False
        for ownerID in [kill.victimCharacterID, kill.victimCorporationID, kill.victimAllianceID]:
            ownerName = GetOwnerName(ownerID)
            if ownerName.lower().find(filterText) >= 0:
                return False

        return True

    for kill in recent:
        if FilterOut(kill):
            continue
        if showAsCondensed:
            data = KeyVal()
            timeOfKill = FmtDate(kill.killTime)
            shipOfCharacterKilled = GetTypeName(kill.victimShipTypeID) or unknownShipLabel
            characterKilled = GetOwnerName(kill.victimCharacterID) or unknownNameLabel
            corporationOfCharacterKilled = GetOwnerName(kill.victimCorporationID) or unknownCorporationLabel
            allianceOfCharacterKilled = GetOwnerName(kill.victimAllianceID) or unknownAllianceLabel
            factionOfCharacterKilled = GetOwnerName(kill.victimFactionID) or unknownFactionLabel
            labelList = [timeOfKill,
             shipOfCharacterKilled,
             characterKilled,
             corporationOfCharacterKilled,
             allianceOfCharacterKilled,
             factionOfCharacterKilled]
            data.label = '<t>'.join(labelList)
            data.GetMenu = GetCombatMenu
            data.OnDblClick = (GetCombatDblClick, data)
            data.kill = kill
            data.mail = kill
            ret.append(entries.Get('KillMailCondensed', data=data))
        else:
            ret.append(entries.Get('KillMail', {'mail': kill}))

    return (ret, headers)


def GetCombatDblClick(entry, *args):
    kill = entry.sr.node.kill
    if kill is not None:
        OpenKillReport(kill)


def GetCombatMenu(entry, *args):
    m = [(MenuLabel('UI/CharacterSheet/CharacterSheetWindow/KillsTabs/CopyKillInfo'), GetCombatText, (entry.sr.node.kill, 1)), (MenuLabel('UI/Control/Entries/CopyExternalKillLink'), GetCrestUrl, (entry.sr.node.kill,))]
    return m


def GetCrestUrl(self, killmail):
    crest_url = GetPublicCrestUrl('killmails', killmail.killID, GetKillReportHashValue(killmail))
    blue.pyos.SetClipboardData(crest_url)


def GetCombatText(self, kill, isCopy = 0):
    ret = CombatLog_CopyText(kill)
    if isCopy:
        blue.pyos.SetClipboardData(CleanKillMail(ret))
    else:
        return ret
