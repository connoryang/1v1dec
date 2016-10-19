#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\structureSettings\settingSection.py
import carbonui
from carbonui.control.menuLabel import MenuLabel
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.util.bunch import Bunch
from carbonui.util.sortUtil import SortListOfTuples
from eve.client.script.ui.control.buttons import ButtonIcon
from eve.client.script.ui.control.checkbox import Checkbox
from eve.client.script.ui.control.entries import Generic
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.themeColored import FillThemeColored
from eve.client.script.ui.structure import ChangeSignalConnect
from eve.client.script.ui.structure.structureSettings import AreGroupNodes, GetGroupIDFromNode, CanHaveGroups
from eve.client.script.ui.structure.structureSettings.groupEntryCont import GroupEntry
from eve.client.script.ui.structure.structureSettings.profileEntry import ProfileEntryBase
import carbonui.const as uiconst
from eve.client.script.ui.structure.structureSettings.uiSettingUtil import AddValueEdit
from localization import GetByLabel
from ownergroups.ownergroupConst import NO_GROUP_ID
import structures
SECTION_LABEL_LEFT = 22
UI_EXPANDED_SETTING = 'structureProfile_expanded_setting_%s'

class SettingSection(ContainerAutoSize):
    default_name = 'SettingSection'
    default_align = uiconst.TOTOP

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        self.structureProfileController = attributes.structureProfileController
        self.ChangeSignalConnection()
        self.settingID = attributes.settingID
        sgControllers = self.structureProfileController.GetGroupsBySettingID(self.settingID)
        canHaveGroups = CanHaveGroups(self.settingID)
        if not canHaveGroups and not sgControllers:
            self.structureProfileController.AddGroup(self.settingID, groupID=NO_GROUP_ID, doSignal=False)
            sgControllers = self.structureProfileController.GetGroupsBySettingID(self.settingID)
        self.AddHeader(canHaveGroups, sgControllers)
        self.sectionCont = ContainerAutoSize(parent=self, name='sectionCont', align=uiconst.TOTOP)
        self.LoadGroups()

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.structureProfileController.on_groups_added, self.OnGroupsAdded), (self.structureProfileController.on_group_changed, self.OnGroupsChanged)]
        ChangeSignalConnect(signalAndCallback, connect)

    def LoadGroups(self):
        self.sectionCont.Flush()
        canHaveGroups = CanHaveGroups(self.settingID)
        if not canHaveGroups:
            return
        sgControllers = self.structureProfileController.GetGroupsBySettingID(self.settingID)
        if sgControllers:
            accessGroupsController = sm.GetService('structureControllers').GetAccessGroupController()
            groupIDs = [ c.GetGroupID() for c in sgControllers ]
            accessGroupsController.PopulatePublicGroupInfo(groupIDs)
            toSort = []
            for c in sgControllers:
                groupInfo = accessGroupsController.GetGroupInfoFromID(c.GetGroupID())
                if groupInfo is None:
                    continue
                nameLower = groupInfo['name'].lower()
                toSort.append((nameLower, (c, groupInfo)))

            sortedControllers = SortListOfTuples(toSort)
            for c, groupInfo in sortedControllers:
                GroupEntry(parent=self.sectionCont, groupID=c.GetGroupID(), settingGroupController=c, structureProfileController=self.structureProfileController, groupInfo=groupInfo)

        else:
            x = Generic(parent=self.sectionCont, height=30)
            x.Startup()
            x.Load(node=Bunch(label=GetByLabel('UI/StructureSettingWnd/NoGroups'), sublevel=1))

    def AddHeader(self, canHaveGroups, sgControllers):
        if canHaveGroups:
            self.header = SettingSectionHeaderWithGroups(parent=self, structureProfileController=self.structureProfileController, expanderFunc=self.OnExpandGroups, settingID=self.settingID)
        else:
            sgController = list(sgControllers)[0]
            if sgController.GetSettingType() == structures.SETTINGS_TYPE_PERCENTAGE:
                headerClass = SettingSectionHeaderWithPercentage
            elif sgController.GetSettingType() == structures.SETTINGS_TYPE_BOOL:
                headerClass = SettingSectionHeaderWithCheckbox
            else:
                raise RuntimeError('Bad settingType', sgController.GetSettingType(), sgController.GetSettingID())
            self.header = headerClass(parent=self, structureProfileController=self.structureProfileController, sgController=sgController, settingID=self.settingID)

    def OnExpandGroups(self):
        isExpanded = settings.user.ui.Get(UI_EXPANDED_SETTING % self.settingID, True)
        self.sectionCont.display = isExpanded

    def DragChanged(self, initiated):
        canHaveGroups = CanHaveGroups(self.settingID)
        if not canHaveGroups:
            return
        self.header.OnGroupsDragged(initiated)

    def Close(self):
        self.ChangeSignalConnection(connect=False)
        self.structureProfileController = None
        ContainerAutoSize.Close(self)

    def OnGroupsAdded(self, settingID, groupIDs):
        if settingID != self.settingID:
            return
        self.LoadGroups()
        self.header.BlinkBgFill()

    def OnGroupsChanged(self):
        self.LoadGroups()


DRAGGING_OPACITY = 0.75

class SettingSectionHeaderBase(ProfileEntryBase):
    default_name = 'SettingSectionHeader'
    rightBtnTexturePath = None
    default_height = 30
    default_align = uiconst.TOTOP
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        ProfileEntryBase.ApplyAttributes(self, attributes)
        self.bgFill = None
        self.settingID = attributes.settingID
        self.structureProfileController = attributes.structureProfileController
        self.fillUnderlay = FillThemeColored(bgParent=self, colorType=uiconst.COLORTYPE_UIBASECONTRAST)
        self.fill = FillThemeColored(bgParent=self, colorType=uiconst.COLORTYPE_UIHEADER, padBottom=1)
        self.rigthCont = Container(parent=self, name='rightCont', align=uiconst.TORIGHT, width=0)
        self.labelCont = Container(parent=self, name='labelCont', padLeft=SECTION_LABEL_LEFT)
        self.sectionNameLabel = EveLabelMedium(name='sectionName', parent=self.labelCont, align=uiconst.CENTERLEFT, text='', autoFadeSides=20)
        self.SetSectionLabel()

    def SetSectionLabel(self):
        text, hint = self.structureProfileController.GetSettingText(self.settingID)
        self.sectionNameLabel.text = text
        self.hint = hint

    def Close(self):
        self.structureProfileController = None
        ProfileEntryBase.Close(self)

    def OnGroupsDragged(self, initiated):
        if initiated:
            self.ConstructBgFill()
            self.FadeBgFill(endValue=DRAGGING_OPACITY)
        elif self.bgFill:
            self.FadeBgFill(endValue=0)

    def ConstructBgFill(self):
        if self.bgFill is None or self.bgFill.destroyed:
            self.bgFill = FillThemeColored(bgParent=self, colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=0)

    def FadeBgFill(self, endValue):
        uicore.animations.FadeTo(self.bgFill, startVal=self.bgFill.opacity, endVal=endValue, duration=0.25)

    def BlinkBgFill(self):
        self.ConstructBgFill()
        uicore.animations.FadeTo(self.bgFill, 0.0, 0.75, duration=0.25, curveType=uiconst.ANIM_WAVE, loops=2)


class SettingSectionHeaderWithGroups(SettingSectionHeaderBase):

    def ApplyAttributes(self, attributes):
        SettingSectionHeaderBase.ApplyAttributes(self, attributes)
        self.expanderFunc = attributes.expanderFunc
        arrowTexturePath = self.GetExpandedTexture()
        left = SECTION_LABEL_LEFT - 20
        self.expandArrow = ButtonIcon(name='expandArrow', parent=self, align=uiconst.CENTERLEFT, pos=(left,
         0,
         16,
         16), iconSize=16, texturePath=arrowTexturePath, func=self.OnExpanderClicked)
        self.addGroupBtn = ButtonIcon(name='addBtn', parent=self, align=uiconst.CENTERRIGHT, pos=(6, 0, 12, 12), iconSize=12, texturePath='res:/UI/Texture/Icons/Plus_Small.png', func=self.OnAddEntry)
        self.rigthCont.width = 20
        self.ChangeRightContDisplay(False)

    def GetExpandedTexture(self):
        isExpanded = settings.user.ui.Get(UI_EXPANDED_SETTING % self.settingID, True)
        if isExpanded:
            return 'res:/UI/Texture/Icons/38_16_229.png'
        else:
            return 'res:/UI/Texture/Icons/38_16_228.png'

    def OnClick(self, *args):
        self.OnExpanderClicked()

    def OnExpanderClicked(self, *args):
        isExpanded = settings.user.ui.Get(UI_EXPANDED_SETTING % self.settingID, True)
        settings.user.ui.Set(UI_EXPANDED_SETTING % self.settingID, not isExpanded)
        self.expanderFunc()
        self.expandArrow.SetTexturePath(self.GetExpandedTexture())

    def FadeSprites(self, toValue):
        SettingSectionHeaderBase.FadeSprites(self, toValue)

    def OnAddEntry(self, *args):
        carbonui.control.menu.ShowMenu(self)

    def GetMenu(self, *args):
        m = []
        if CanHaveGroups(self.settingID):
            accessGroupsController = sm.GetService('structureControllers').GetAccessGroupController()
            myGroups = accessGroupsController.GetMyGroups()
            if myGroups:
                m += [[MenuLabel('UI/StructureSettingWnd/AddGroupToSetting'), ('isDynamic', self._GetMyGroupsMenu, (myGroups,))]]
        m += [(MenuLabel('UI/StructureSettingWnd/ManageAccessGroups'), uicore.cmd.OpenAccessGroupsWindow, ())]
        return m

    def _GetMyGroupsMenu(self, myGroups):
        m = []
        groupsWithSetting = self.structureProfileController.GetGroupsBySettingID(self.settingID)
        groupIDs = {g.groupID for g in groupsWithSetting}
        for groupID, g in myGroups.iteritems():
            if groupID in groupIDs:
                continue
            groupName = g.name
            m.append((groupName.lower(), (groupName, self.AddGroupsToSettingSection, ([groupID],))))

        m = SortListOfTuples(m)
        return m

    def ChangeRightContDisplay(self, show = False):
        self.rigthCont.display = show

    def OnDropData(self, dragSource, dragData):
        if not dragData or not CanHaveGroups(settingID=self.settingID):
            return
        if not AreGroupNodes(dragData):
            return
        groupIDsToAdd = filter(None, [ GetGroupIDFromNode(eachNode) for eachNode in dragData ])
        if groupIDsToAdd:
            self.AddGroupsToSettingSection(groupIDsToAdd)

    def AddGroupsToSettingSection(self, groupIDsToAdd):
        self.structureProfileController.AddNewGroups(self.settingID, groupIDsToAdd)


class SettingSectionHeaderWithPercentage(SettingSectionHeaderBase):

    def ApplyAttributes(self, attributes):
        SettingSectionHeaderBase.ApplyAttributes(self, attributes)
        self.sgController = attributes.sgController
        self.valueEdit = AddValueEdit(self.rigthCont, self.sgController, callback=self.OnRateChanged)
        self.rigthCont.width = self.valueEdit.width

    def OnRateChanged(self, value, *args):
        self.sgController.SetValue(value)


class SettingSectionHeaderWithCheckbox(SettingSectionHeaderBase):

    def ApplyAttributes(self, attributes):
        SettingSectionHeaderBase.ApplyAttributes(self, attributes)
        self.sgController = attributes.sgController
        checked = bool(self.sgController.GetValue())
        left = SECTION_LABEL_LEFT - 20 - 2
        self.checkbox = Checkbox(parent=self, align=uiconst.CENTERLEFT, text='', checked=checked, callback=self.CheckBoxChange, pos=(4, 0, 0, 20))

    def CheckBoxChange(self, cb):
        value = cb.GetValue()
        self.sgController.SetValue(value)

    def OnClick(self, *args):
        self.checkbox.ToggleState()
