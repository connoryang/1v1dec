#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\structureBrowser\entries\structureEntryMyCorp.py
from collections import defaultdict
import structures
from carbon.common.script.util.commonutils import StripTags
from carbon.common.script.util.format import FmtDate
from carbonui.control.menuLabel import MenuLabel
from carbonui.primitives.sprite import Sprite
from carbonui.util.sortUtil import SortListOfTuples
from eve.client.script.ui.control.baseListEntry import BaseListEntryCustomColumns
from eve.client.script.ui.control.eveIcon import ItemIcon
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.glowSprite import GlowSprite
from eve.client.script.ui.eveFontConst import EVE_MEDIUM_FONTSIZE
from eve.client.script.ui.services.menuSvcExtras.openFunctions import OpenProfileSettingsForStructure
from eve.client.script.ui.station import stationServiceConst
from eve.client.script.ui.structure import ChangeSignalConnect
from eve.client.script.ui.structure.structureBrowser.controllers.structureEntryController import StructureEntryController
from eve.client.script.ui.structure.structureBrowser.entries.structureEntry import StructureServiceIconMyCorp
from eve.client.script.ui.structure.structureBrowser.structureState import StructureStateIcon
from eve.client.script.ui.structure.structureSettings.schedule.smallSchedule import SmallSchedule
from localization import GetByLabel
import carbonui.const as uiconst
from utillib import KeyVal
import blue
HEIGHT = 48
ICONSIZE = 20
LABEL_PARAMS = (EVE_MEDIUM_FONTSIZE, 0, 0)
STATE_ICON_SIZE = 30

class StructureEntryMyCorp(BaseListEntryCustomColumns):
    default_name = 'StructureEntryMyCorp'
    isDragObject = True

    def ApplyAttributes(self, attributes):
        BaseListEntryCustomColumns.ApplyAttributes(self, attributes)
        self.controller = self.node.controller
        self.slimProfileController = self.node.slimProfileController
        self.ChangeSignalConnection(connect=True)
        self.BuildUI()

    def BuildUI(self):
        self.AddProfileNameColumn()
        self.stateColumn = self.AddColumnContainer()
        self.jumpColumn = self.AddColumnContainer()
        self.securityColumn = self.AddColumnContainer()
        self.nameColumn = self.AddColumnContainer()
        self.servicesColumn = self.AddColumnContainer()
        self.scheduleColumn = self.AddColumnContainer()
        self.fuelColumn = self.AddColumnContainer()
        self.LoadUI()

    def LoadUI(self):
        self.PopulateProfileNameColumn()
        self.PopulateStateColumn()
        self.PopulateJumpColumns()
        self.PopulateSecurityColumn()
        self.PopulateNameColumn()
        self.PopulateServicesColumn()
        self.PopulateScheduleColumn()
        self.PopulateFuelColumn()

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.controller.on_structure_state_changed, self.OnStructureStateChanged)]
        ChangeSignalConnect(signalAndCallback, connect)

    def AddProfileNameColumn(self):
        pass

    def PopulateProfileNameColumn(self):
        pass

    def PopulateStateColumn(self):
        self.stateColumn.Flush()
        self.structureStateIcon = StructureStateIcon(parent=self.stateColumn)
        self.structureStateIcon.DelegateEvents(self)
        self.SetStructureState()

    def SetStructureState(self):
        if self.structureStateIcon:
            structureState = self.controller.GetState()
            self.structureStateIcon.SetStructureState(structureState)

    def PopulateNameColumn(self):
        self.nameColumn.Flush()
        name = self.controller.GetName()
        size = HEIGHT - 4
        ItemIcon(parent=self.nameColumn, align=uiconst.CENTERLEFT, typeID=self.controller.GetTypeID(), width=size, height=size, state=uiconst.UI_DISABLED)
        Label(parent=self.nameColumn, text=name, align=uiconst.CENTERLEFT, left=HEIGHT, state=uiconst.UI_NORMAL)

    def PopulateServicesColumn(self):
        self.servicesColumn.Flush()
        availableServices = self.controller.GetServices()
        serviceData = stationServiceConst.serviceData
        for i, data in enumerate(serviceData):
            left = i * ICONSIZE
            isAvailable = self.IsThisServiceAvailable(data, availableServices)
            opacity = 1.0 if isAvailable else 0.1
            s = StructureServiceIconMyCorp(name=data.name, parent=self.servicesColumn, texturePath=data.iconID, pos=(left,
             0,
             ICONSIZE,
             ICONSIZE), hintHeader=data.label, opacity=opacity, serviceName=data.name, controller=self.controller, serviceID=data.serviceID)
            s.DelegateEvents(self)

    def IsThisServiceAvailable(self, data, availableServices):
        return data in availableServices or data.serviceID == stationServiceConst.serviceIDAlwaysPresent or data.serviceID == structures.SERVICE_FITTING

    def PopulateJumpColumns(self):
        self.jumpColumn.Flush()
        text = self.controller.GetNumJumps()
        Label(parent=self.jumpColumn, text=text, align=uiconst.CENTERLEFT, left=6)

    def PopulateSecurityColumn(self):
        self.securityColumn.Flush()
        text = self.controller.GetSecurityWithColor()
        Label(parent=self.securityColumn, text=text, align=uiconst.CENTERLEFT, left=6)

    def PopulateScheduleColumn(self):
        self.scheduleColumn.Flush()
        vulnerableHoursThisWeek = self.controller.GetCurrentSchedule()
        vulnerableHoursNextWeek = self.controller.GetNextWeekSchedule()
        isSameSchedule = vulnerableHoursThisWeek == vulnerableHoursNextWeek
        s = SmallSchedule(parent=self.scheduleColumn, align=uiconst.CENTERLEFT, vulnerableHours=vulnerableHoursThisWeek, state=uiconst.UI_NORMAL, left=6)
        s.DelegateEvents(self)
        if not isSameSchedule:
            texturePath = 'res:/UI/Texture/classes/StructureBrowser/notSameSchedule.png'
            hint = GetByLabel('UI/Structures/Browser/NotSameScheduleHint')
            diffSprite = Sprite(name='notSameSchedule', parent=self.scheduleColumn, align=uiconst.CENTERRIGHT, pos=(2, 2, 16, 16), iconSize=16, texturePath=texturePath, opacity=0.75, hint=hint)
            diffSprite.DelegateEvents(self)
        s.LoadTooltipPanel = self.LoadScheduleToolTip

    def PopulateFuelColumn(self):
        self.fuelColumn.Flush()
        fuelExpires = self.controller.GetFuelExpiry()
        if fuelExpires:
            text = FmtDate(fuelExpires - blue.os.GetWallclockTime(), 'ns')
            Label(parent=self.fuelColumn, text=text, align=uiconst.CENTERLEFT, left=6)

    def GetDragData(self):
        nodesSelected = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        data = []
        for eachNode in nodesSelected:
            k = KeyVal(__guid__='xtriui.ListSurroundingsBtn', itemID=eachNode.controller.GetItemID(), typeID=eachNode.controller.GetTypeID(), label=StripTags(eachNode.controller.GetName().replace('<br>', '-')), isMyCorpStructureEntry=True)
            data.append(k)

        return data

    def GetMenu(self):
        selectedNodes = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        numSelectedNodes = len(selectedNodes)
        itemID = self.controller.GetItemID()
        typeID = self.controller.GetTypeID()
        m = []
        if numSelectedNodes == 1:
            if self.controller.CanUnanchor():
                m.append([MenuLabel('UI/StructureBrowser/Decommission'), sm.GetService('structureDeployment').Unanchor, [itemID, typeID]])
            elif self.controller.CanCancelUnanchor():
                m.append([MenuLabel('UI/StructureBrowser/CancelDecommission'), sm.GetService('structureDeployment').CancelUnanchor, [itemID, typeID]])
        numOptions = self._GetModifyMenuOptions(selectedNodes)
        m += numOptions
        if numSelectedNodes > 1:
            setProfileMenu = MenuLabel('UI/StructureBrowser/SetProfileMany', {'numSelected': numSelectedNodes})
        else:
            setProfileMenu = MenuLabel('UI/StructureBrowser/SetProfile')
        m += self.GetMenuToFindProfile(itemID)
        m += [[setProfileMenu, ('isDynamic', self._GetProfilesMenu, (selectedNodes,))]]
        m += sm.GetService('menu').GetMenuFormItemIDTypeID(itemID=itemID, typeID=typeID)
        return m

    def GetMenuToFindProfile(self, itemID):
        return []

    def _GetModifyMenuOptions(self, selectedNodes):
        selectedControllers = [ x.controller for x in selectedNodes ]
        controllersByHours = defaultdict(list)
        for eachController in selectedControllers:
            controllersByHours[eachController.GetRequiredHours()].append(eachController)

        modifyOptions = []
        for requiredHours, controllers in controllersByHours.iteritems():
            infoOnStructures = [ (x.GetItemID(),
             x.GetSolarSystemID(),
             x.GetCurrentSchedule(),
             x.GetNextWeekSchedule()) for x in controllers ]
            menuLabel = MenuLabel('UI/StructureBrowser/ModifySchedule', {'numHours': requiredHours})
            funcArgs = (requiredHours, infoOnStructures)
            modifyOptions.append((requiredHours, (menuLabel, self.ModifyVulnerability, funcArgs)))

        numOptions = SortListOfTuples(modifyOptions)
        return numOptions

    def _GetProfilesMenu(self, selectedNodes):
        selectedStructureIDs = [ x.controller.GetItemID() for x in selectedNodes ]
        allStructureProfileController = sm.GetService('structureControllers').GetAllStructuresProfileController()
        allCorpProfiles = allStructureProfileController.GetProfiles()

        def UpdateProfileIDForStructures(profileID):
            allStructureProfileController.UpdateProfileIDForStructures(profileID, selectedStructureIDs)

        m = []
        for profileID, profileController in allCorpProfiles.iteritems():
            name = profileController.GetProfileName()
            m.append((name.lower(), (name, UpdateProfileIDForStructures, (profileID,))))

        m = SortListOfTuples(m)
        return m

    def ModifyVulnerability(self, requiredHours, infoOnStructures):
        from eve.client.script.ui.structure.structureSettings.schedule.vulnerabilityScheduleWnd import VulnerabilityScheduleWnd
        VulnerabilityScheduleWnd(requiredHours=requiredHours, infoOnStructures=infoOnStructures)

    def LoadScheduleToolTip(self, tooltipPanel, *args):
        from eve.client.script.ui.structure.structureSettings.schedule.scheduleTooltip import ScheduleTooltip
        hoursThisWeek = self.controller.GetCurrentSchedule()
        hoursNextWeek = self.controller.GetNextWeekSchedule()
        typeID = self.controller.GetTypeID()
        t = ScheduleTooltip()
        t.AddScheduleToTooltip(tooltipPanel, typeID, hoursThisWeek, hoursNextWeek)

    def OnStructureStateChanged(self, structureID):
        self.LoadUI()

    def Close(self):
        self.ChangeSignalConnection(connect=False)
        BaseListEntryCustomColumns.Close(self)

    @staticmethod
    def GetColumnSortValues(controller, slimProfileController):
        return (controller.GetState(),
         controller.GetNumJumps(),
         controller.GetSecurity(),
         '%s %s ' % (controller.GetSystemName(), StripTags(controller.GetName()).lower()),
         len(controller.GetServices()),
         (controller.GetCurrentSchedule(), controller.GetNextWeekSchedule()),
         '')

    @staticmethod
    def GetSortValue(node, by, sortDirection, idx):
        return (node.columnSortValues[idx],) + tuple(node.columnSortValues)

    @staticmethod
    def GetHeaders():
        return (GetByLabel('UI/Structures/Browser/HeaderState'),
         GetByLabel('UI/Common/Jumps'),
         GetByLabel('UI/Common/Security'),
         GetByLabel('UI/Common/Name'),
         GetByLabel('UI/Structures/Browser/HeaderServices'),
         GetByLabel('UI/Structures/Browser/HeaderSchedule'),
         GetByLabel('UI/Structures/Browser/HeaderFuel'))

    @staticmethod
    def GetDynamicHeight(node, width):
        return HEIGHT

    @staticmethod
    def GetFixedColumns():
        return {GetByLabel('UI/Structures/Browser/HeaderServices'): ICONSIZE * len(stationServiceConst.serviceData) + 2,
         GetByLabel('UI/Structures/Browser/HeaderSchedule'): 76}

    @staticmethod
    def GetColWidths(node, idx = None):
        controller = node.controller
        widths = []
        getAllWidths = idx is None
        if getAllWidths or idx == 0:
            widths.append(STATE_ICON_SIZE + 10)
        if getAllWidths or idx == 1:
            jumpText = unicode(controller.GetNumJumps())
            widths.append(uicore.font.MeasureTabstops([(jumpText,) + LABEL_PARAMS])[0])
        if getAllWidths or idx == 2:
            securityText = unicode(controller.GetSecurity())
            widths.append(uicore.font.MeasureTabstops([(securityText,) + LABEL_PARAMS])[0])
        if getAllWidths or idx == 3:
            nameToUse = max(StripTags(controller.GetName(), ignoredTags=('br',)).split('<br>'), key=len)
            widths.append(uicore.font.MeasureTabstops([(nameToUse,) + LABEL_PARAMS])[0] + HEIGHT - 4)
        return widths


class StructureEntryMyCorpAllProfiles(StructureEntryMyCorp):

    def AddProfileNameColumn(self):
        self.profileNameColumn = self.AddColumnContainer()

    def PopulateProfileNameColumn(self):
        self.profileNameColumn.Flush()
        profileName = self._GetProfileName(self.slimProfileController)
        Label(parent=self.profileNameColumn, text=profileName, align=uiconst.CENTERLEFT, left=6)

    def GetMenuToFindProfile(self, itemID):
        return [[MenuLabel('UI/Commands/EditProfileForStructure'), OpenProfileSettingsForStructure, (itemID,)]]

    @staticmethod
    def _GetProfileName(slimProfileController):
        if slimProfileController:
            profileName = slimProfileController.GetProfileName()
        else:
            profileName = ''
        return profileName

    @staticmethod
    def GetColumnSortValues(controller, slimProfileController):
        baseSortValues = StructureEntryMyCorp.GetColumnSortValues(controller, slimProfileController)
        return (StructureEntryMyCorpAllProfiles._GetProfileName(slimProfileController).lower(),) + baseSortValues

    @staticmethod
    def GetHeaders():
        baseHeaders = StructureEntryMyCorp.GetHeaders()
        return (GetByLabel('UI/Structures/Browser/HeaderProfileName'),) + baseHeaders

    @staticmethod
    def GetColWidths(node, idx = None):
        widths = []
        getAllWidths = idx is None
        if getAllWidths or idx == 0:
            profileName = StructureEntryMyCorpAllProfiles._GetProfileName(node.slimProfileController)
            widths.append(uicore.font.MeasureTabstops([(profileName,) + LABEL_PARAMS])[0])
        if getAllWidths:
            widths += StructureEntryMyCorp.GetColWidths(node, idx)
        elif idx > 0:
            widths += StructureEntryMyCorp.GetColWidths(node, idx - 1)
        return widths
