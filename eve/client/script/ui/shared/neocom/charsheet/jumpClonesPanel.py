#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\neocom\charsheet\jumpClonesPanel.py
import evetypes
from carbon.common.script.util.format import FmtDate
from carbonui.control.menuLabel import MenuLabel
from carbonui.primitives.container import Container
from carbonui.util.sortUtil import SortListOfTuples
from eve.client.script.ui.control import entries
from eve.client.script.ui.control.eveScroll import Scroll
import blue
from collections import OrderedDict
from eve.client.script.ui.util.utilWindows import NamePopup
from eve.common.script.sys.idCheckers import IsStation
import localization
from localization import GetByLabel

class JumpClonesPanel(Container):
    default_name = 'JumpClonesPanel'
    __notifyevents__ = ['OnCloneJumpUpdate']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.scroll = Scroll(parent=self, padding=(0, 4, 0, 4))

    def LoadPanel(self, *args):
        jumpCloneSvc = sm.GetService('clonejump')
        jumpClones = jumpCloneSvc.GetClones()
        scrolllist = []
        lastJump = jumpCloneSvc.LastCloneJumpTime()
        hoursLimit = sm.GetService('godma').GetItem(session.charid).cloneJumpCoolDown
        if lastJump:
            jumpTime = lastJump + hoursLimit * const.HOUR
            nextJump = jumpTime > blue.os.GetWallclockTime()
        else:
            nextJump = False
        nextAvailableLabel = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/JumpCloneScroll/NextCloneJump')
        availableNow = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/JumpCloneScroll/Now')
        if nextJump:
            scrolllist.append(entries.Get('TextTimer', {'line': 1,
             'label': nextAvailableLabel,
             'text': FmtDate(lastJump),
             'iconID': const.iconDuration,
             'countdownTime': int(jumpTime),
             'finalText': availableNow}))
        else:
            scrolllist.append(entries.Get('TextTimer', {'line': 1,
             'label': nextAvailableLabel,
             'text': availableNow,
             'iconID': const.iconDuration,
             'countdownTime': 0}))
        if jumpClones:
            d = OrderedDict([('station', {}), ('shipOrStructure', {})])
            primeLocs = []
            for jc in jumpClones:
                jumpCloneID = jc.jumpCloneID
                locationID = jc.locationID
                cloneName = jc.cloneName
                primeLocs.append(locationID)
                destinationType = 'station' if IsStation(locationID) else 'shipOrStructure'
                d[destinationType][locationID] = (jumpCloneID, locationID, cloneName)

            cfg.evelocations.Prime(primeLocs)
            for locInfo in d.itervalues():
                locIDs = locInfo.keys()
                locNames = self.GetLocNames(locIDs)
                locNames = localization.util.Sort(locNames, key=lambda x: x[0])
                for _, locationString, locationID in locNames:
                    infoForLocation = locInfo[locationID]
                    cloneName = infoForLocation[2]
                    label = '%s - %s' % (cloneName, locationString) if cloneName else locationString
                    groupID = infoForLocation
                    data = {'GetSubContent': self.GetCloneImplants,
                     'label': label,
                     'id': groupID,
                     'jumpCloneID': infoForLocation[0],
                     'locationID': infoForLocation[1],
                     'cloneName': cloneName,
                     'state': 'locked',
                     'iconMargin': 18,
                     'showicon': 'res:/ui/Texture/WindowIcons/jumpclones.png',
                     'sublevel': 0,
                     'MenuFunction': self.JumpCloneMenu,
                     'showlen': 0}
                    scrolllist.append(entries.Get('Group', data))

        self.scroll.sr.id = 'charsheet_jumpclones'
        noClonesFoundHint = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/JumpCloneScroll/NoJumpClonesFound')
        self.scroll.Load(contentList=scrolllist, noContentHint=noClonesFoundHint)

    def GetLocNames(self, locIDs):
        locNames = []
        destroyedLocString = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/JumpCloneScroll/CloneLocationDestroyed')
        destroyedLocName = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/JumpCloneScroll/DestroyedLocation')
        for locID in locIDs:
            if locID in cfg.evelocations:
                locName = cfg.evelocations.Get(locID).name
                locString = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/JumpCloneScroll/CloneLocation', cloneLocation=locID)
            else:
                locName = destroyedLocName
                locString = destroyedLocString
            locNames.append((locName, locString, locID))

        return locNames

    def GetCloneImplants(self, nodedata, *args):
        scrolllist = []
        godma = sm.GetService('godma')
        implants = SortListOfTuples([ (getattr(godma.GetType(implant.typeID), 'implantness', None), implant) for implant in sm.GetService('clonejump').GetImplantsForClone(nodedata.jumpCloneID) ])
        if implants:
            for cloneImplantRow in implants:
                scrolllist.append(entries.Get('ImplantEntry', {'implant_booster': cloneImplantRow,
                 'label': evetypes.GetName(cloneImplantRow.typeID),
                 'sublevel': 1}))

        else:
            noImplantsString = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/JumpCloneScroll/NoImplantsInstalled')
            scrolllist.append(entries.Get('Text', {'label': noImplantsString,
             'text': noImplantsString}))
        scrolllist.append(entries.Get('CloneButtons', {'locationID': nodedata.locationID,
         'jumpCloneID': nodedata.jumpCloneID}))
        return scrolllist

    def JumpCloneMenu(self, node):
        m = []
        validLocation = node.locationID in cfg.evelocations
        if eve.session.stationid and validLocation:
            m += [None]
            m += [(MenuLabel('UI/CharacterSheet/CharacterSheetWindow/JumpCloneScroll/Jump'), sm.GetService('clonejump').CloneJump, (node.locationID,))]
        if validLocation:
            m.append((MenuLabel('UI/CharacterSheet/CharacterSheetWindow/JumpCloneScroll/Destroy'), sm.GetService('clonejump').DestroyInstalledClone, (node.jumpCloneID,)))
            if IsStation(node.locationID):
                stationInfo = sm.StartService('ui').GetStation(node.locationID)
                m += sm.StartService('menu').CelestialMenu(node.locationID, typeID=stationInfo.stationTypeID, parentID=stationInfo.solarSystemID)
            m += [(MenuLabel('UI/Commands/SetName'), self.SetJumpCloneName, (node.jumpCloneID, node.cloneName))]
        return m

    def SetJumpCloneName(self, cloneID, oldName):
        nameRet = NamePopup(GetByLabel('UI/Menusvc/SetName'), GetByLabel('UI/Menusvc/TypeInNewName'), setvalue=oldName, maxLength=100)
        if nameRet:
            sm.GetService('clonejump').SetJumpCloneName(cloneID, nameRet)

    def OnCloneJumpUpdate(self):
        if self.display:
            self.LoadPanel()
