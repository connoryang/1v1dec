#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\planet\planetEditModeContainer.py
import carbonui.const as uiconst
import evetypes
import uiprimitives
import uicontrols
import util
import eve.client.script.ui.control.entries as listentry
import blue
import uiutil
import localization
from eve.common.script.sys.eveCfg import InShipInSpace
from .pinContainers.BasePinContainer import IconButton
ICON_SIZE = 24

class PlanetEditModeContainer(uicontrols.ContainerAutoSize):
    __guid__ = 'planet.ui.PlanetEditModeContainer'
    default_name = 'planetEditMode'
    default_align = uiconst.TOTOP
    default_state = uiconst.UI_HIDDEN
    __notifyevents__ = ['OnEditModeChanged',
     'OnEditModeBuiltOrDestroyed',
     'OnPlanetCommandCenterDeployedOrRemoved',
     'OnItemChange',
     'OnSessionChanged']
    COLOR_ENABLED = (1.0, 1.0, 1.0, 1.0)
    COLOR_DISABLED = (0.7, 0.7, 0.7, 0.8)

    def ApplyAttributes(self, attributes):
        uicontrols.ContainerAutoSize.ApplyAttributes(self, attributes)
        self.activeBuildEntry = None
        self.buildContainer = uicontrols.ContainerAutoSize(parent=self, name='buildContainer', align=uiconst.TOTOP)
        self.CreateLayout()
        sm.RegisterNotify(self)

    def CreateLayout(self):
        icon = 'ui_44_32_7'
        commandPinObject = sm.GetService('planetUI').GetCurrentPlanet().GetCommandCenterForCharacter(session.charid)
        commandPin = commandPinObject is not None and not commandPinObject.IsInEditMode()
        buttonList = [(const.groupExtractionControlUnitPins, 'ui_77_32_26'),
         (const.groupProcessPins, 'ui_77_32_30'),
         (const.groupStoragePins, 'ui_77_32_25'),
         (const.groupSpaceportPins, 'ui_77_32_27'),
         (const.groupPlanetaryLinks, 'ui_77_32_31')]
        if not commandPin:
            buttonList.insert(0, (const.groupCommandPins, 'ui_77_32_29'))
        for groupID, icon in buttonList:
            groupEnabled = commandPin or groupID == const.groupCommandPins
            if groupEnabled:
                color = self.COLOR_ENABLED
            else:
                color = self.COLOR_DISABLED
            buildEntry = uiprimitives.Container(parent=self.buildContainer, name='buildEntry' + str(groupID), align=uiconst.TOTOP, pos=(0,
             0,
             0,
             ICON_SIZE), state=uiconst.UI_NORMAL)
            buildEntry.groupID = groupID
            buildEntry.headerContainer = header = uiprimitives.Container(parent=buildEntry, name='buildHeaderContainer', align=uiconst.TOTOP, pos=(0,
             0,
             0,
             ICON_SIZE))
            buildEntry.iconButton = iconButton = IconButton(parent=header, name='pin_' + str(groupID), icon=icon, align=uiconst.TOLEFT, pos=(0,
             0,
             ICON_SIZE,
             0), state=uiconst.UI_NORMAL, size=ICON_SIZE, color=color)
            iconButton.OnMouseEnter = (self.OnBuildIconButtonMouseEnter, buildEntry)
            iconButton.OnMouseExit = (self.OnBuildIconButtonMouseExit, buildEntry)
            if commandPin:
                iconButton.OnClick = (self.OnBuildIconButtonClicked, buildEntry)
            buildEntry.heading = uicontrols.EveHeaderMedium(parent=header, text='<b>' + evetypes.GetGroupNameByGroup(groupID) + '</b>', state=uiconst.UI_NORMAL, hilightable=1, pos=(ICON_SIZE + 4,
             6,
             200,
             ICON_SIZE), color=color)
            buildEntry.heading.OnMouseEnter = (self.OnBuildIconButtonMouseEnter, buildEntry)
            buildEntry.heading.OnMouseExit = (self.OnBuildIconButtonMouseExit, buildEntry)
            buildEntry.heading.OnClick = (self.OnBuildIconButtonClicked, buildEntry)
            buildEntry.structureScroll = uicontrols.Scroll(parent=buildEntry, name='structureScroll', padLeft=ICON_SIZE)
            buildEntry.structureScroll.state = uiconst.UI_HIDDEN
            buildEntry.structureScroll.HideBackground()
            buildEntry.structureScroll.RemoveActiveFrame()
            buildEntry.structureScroll.scrollEnabled = 0
            buildEntry.structureScroll.multiSelect = False
            try:
                self.LoadStructureScroll(buildEntry, commandPin, color)
            except AttributeError:
                if buildEntry.destroyed or not self or self.destroyed:
                    return
                raise

    def OnBuildIconButtonMouseEnter(self, buildEntry, *args):
        buildEntry.headerContainer.fill = uiprimitives.Fill(parent=buildEntry.headerContainer)

    def OnBuildIconButtonMouseExit(self, buildEntry, *args):
        if hasattr(buildEntry.headerContainer, 'fill'):
            buildEntry.headerContainer.fill.Close()

    def OnBuildIconButtonClicked(self, buildEntry, *args):
        if self.activeBuildEntry is not None:
            self.HideActiveStructureGroup()
            if buildEntry == self.activeBuildEntry:
                self.activeBuildEntry = None
                return
        height = max(buildEntry.structureScroll.GetContentHeight() + ICON_SIZE + 4, ICON_SIZE)
        uicore.effect.MorphUI(buildEntry, 'height', height, time=250.0)
        buildEntry.structureScroll.state = uiconst.UI_NORMAL
        uicore.effect.MorphUI(buildEntry.structureScroll, 'opacity', 1, float=1, time=250.0)
        self.activeBuildEntry = buildEntry

    def HideActiveStructureGroup(self):
        uicore.effect.MorphUI(self.activeBuildEntry.structureScroll, 'opacity', 0, float=1, time=250.0)
        self.activeBuildEntry.structureScroll.state = uiconst.UI_HIDDEN
        uicore.effect.MorphUI(self.activeBuildEntry, 'height', ICON_SIZE, time=250.0)

    def GetStructuresForGroup(self, groupID):
        planetTypeID = sm.GetService('planetUI').typeID
        godma = sm.GetService('godma')
        structureIDs = set()
        for typeID in evetypes.GetTypeIDsByGroup(groupID):
            typeRestriction = godma.GetTypeAttribute(typeID, const.attributePlanetRestriction)
            if typeRestriction and int(typeRestriction) != planetTypeID:
                continue
            structureIDs.add(typeID)

        return structureIDs

    def LoadStructureScroll(self, buildEntry, groupEnabled, color):
        scrolllist = []
        if buildEntry.groupID == const.groupPlanetaryLinks:
            data = util.KeyVal(label=localization.GetByLabel('UI/PI/Common/CreateLink'), createLink=True, hideLines=1, fontColor=(self.COLOR_DISABLED, self.COLOR_ENABLED)[groupEnabled], OnClick=self.OnBuildEntryClicked, ignoreRightClick=True)
            scrolllist.append(('', listentry.Get('Generic', data=data)))
        else:
            for typeID in self.GetStructuresForGroup(buildEntry.groupID):
                if not evetypes.IsPublished(typeID):
                    continue
                data = util.KeyVal(label=evetypes.GetName(typeID), typeID=typeID, hideLines=1, ignoreRightClick=True)
                isEnabled, hint = self.IsBuildEntryEnabled(buildEntry.groupID, typeID, groupEnabled)
                if isEnabled:
                    data.OnClick = self.OnBuildEntryClicked
                    data.fontColor = self.COLOR_ENABLED
                else:
                    data.fontColor = self.COLOR_DISABLED
                    data.hint = hint
                if buildEntry.groupID == const.groupCommandPins:
                    sortBy = evetypes.GetBasePrice(typeID)
                else:
                    sortBy = data.label.lower()
                scrolllist.append((sortBy, listentry.Get('Generic', data=data)))

        scrolllist = uiutil.SortListOfTuples(scrolllist)
        buildEntry.structureScroll.Load(contentList=scrolllist)

    def IsBuildEntryEnabled(self, groupID, structureTypeID, groupEnabled):
        if groupID == const.groupCommandPins:
            planetID = sm.GetService('planetUI').planetID
            planetSolarSystemID = sm.GetService('map').GetPlanetInfo(planetID).solarSystemID
            if not InShipInSpace() or session.solarsystemid != planetSolarSystemID:
                return (False, localization.GetByLabel('UI/PI/Common/CannotBuildLocation'))
            planetRows = sm.GetService('planetSvc').GetMyPlanets()
            skills = sm.GetService('skills').GetSkills()
            if len(planetRows) > 0:
                skillRec = skills.get(const.typeInterplanetaryConsolidation, None)
                myLevel = getattr(skillRec, 'skillLevel', -1)
                if myLevel < len(planetRows):
                    if myLevel < 5:
                        hint = localization.GetByLabel('UI/PI/Common/CannotBuildMaxColoniesTrain', skillName=evetypes.GetName(const.typeInterplanetaryConsolidation))
                    else:
                        hint = localization.GetByLabel('UI/PI/Common/CannotBuildMaxColonies')
                    return (False, hint)
            skillsRequired = sm.GetService('skills').GetRequiredSkills(structureTypeID)
            for skillTypeID, level in skillsRequired.iteritems():
                skillRec = skills.get(skillTypeID, None)
                myLevel = getattr(skillRec, 'skillLevel', -1)
                if myLevel < level:
                    hint = localization.GetByLabel('UI/PI/Common/CannotBuildSkillNeeded', skillName=evetypes.GetName(skillTypeID), skillLevel=int(level))
                    return (False, hint)

            if session.shipid is None:
                hint = localization.GetByLabel('UI/PI/Common/CannotBuildNoCommandCenter', typeName=evetypes.GetName(structureTypeID))
                return (False, hint)
            inv = sm.GetService('invCache').GetInventoryFromId(session.shipid)
            commandCenterID = None
            if inv:
                invList = inv.List(const.flagSpecializedCommandCenterHold)
                invList.extend(inv.List(const.flagCargo))
                for item in invList:
                    if item.typeID == structureTypeID:
                        commandCenterID = item.itemID
                        break

            if commandCenterID is None:
                hint = localization.GetByLabel('UI/PI/Common/CannotBuildNoCommandCenter', typeName=evetypes.GetName(structureTypeID))
                return (False, hint)
        elif not groupEnabled:
            return (False, localization.GetByLabel('UI/PI/Common/CannotBuildNoCommandCenterBuilt'))
        return (True, '')

    def OnBuildEntryClicked(self, entry):
        if entry.sr.node.createLink:
            sm.GetService('planetUI').myPinManager.CreateLinkOnNextClick()
        else:
            typeID = entry.sr.node.typeID
            sm.GetService('planetUI').myPinManager.PlacePinOnNextClick(typeID)

    def OnPlanetCommandCenterDeployedOrRemoved(self):
        self.ResetBuildbuttons()

    def OnItemChange(self, item = None, change = None):
        locationIdx = const.ixLocationID
        if session.shipid not in (item[locationIdx], change.get(locationIdx, 'No location change')):
            return
        if evetypes.GetGroupID(item.typeID) == const.groupCommandPins:
            self.ResetBuildbuttons()

    def ResetBuildbuttons(self):
        uicore.effect.MorphUI(self.buildContainer, 'opacity', 0.0, time=250.0, newthread=False, float=True)
        if not self or self.destroyed:
            return
        self.buildContainer.Flush()
        self.activeBuildEntry = None
        self.CreateLayout()
        blue.pyos.synchro.SleepWallclock(300)
        if not self or self.destroyed:
            return
        uicore.effect.MorphUI(self.buildContainer, 'opacity', 1.0, time=250.0, newthread=False, float=True)

    def OnSessionChanged(self, isRemote, sess, change):
        self.ResetBuildbuttons()
