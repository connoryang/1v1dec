#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\neocom\characterSheetWindow.py
import telemetry
import const
import localization
import uicontrols
import uthread
import util
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control import entries as listentry
from eve.client.script.ui.control.divider import Divider
from eve.client.script.ui.shared.info.infoWindow import PortraitWindow
from eve.client.script.ui.shared.neocom.charsheet import PANEL_SHIPSKINS, PANEL_PLEX, PANEL_EMPLOYMENT, PANEL_JUMPCLONES, PANEL_KILLRIGHTS, PANEL_SECURITYSTATUS, PANEL_BIO, PANEL_IMPLANTSBOOTERS, PANEL_ATTRIBUTES, PANEL_COMBATLOG, PANEL_DECORATIONS, PANEL_SKILLS, PANEL_STANDINGS, TABS, PANEL_SKILLS_CERTIFICATES, PANEL_SKILLS_SKILLS, PANEL_SKILLS_HISTORY
from eve.client.script.ui.shared.neocom.charsheet.attributesPanel import AttributesPanel
from eve.client.script.ui.shared.neocom.charsheet.bioPanel import BioPanel
from eve.client.script.ui.shared.neocom.charsheet.combatLogPanel import CombatLogPanel
from eve.client.script.ui.shared.neocom.charsheet.decorationsPanel import DecorationsPanel
from eve.client.script.ui.shared.neocom.charsheet.employmentHistoryPanel import EmploymentHistoryPanel
from eve.client.script.ui.shared.neocom.charsheet.implantsBoostersPanel import ImplantsBoostersPanel
from eve.client.script.ui.shared.neocom.charsheet.jumpClonesPanel import JumpClonesPanel
from eve.client.script.ui.shared.neocom.charsheet.killRightsPanel import KillRightsPanel
from eve.client.script.ui.shared.neocom.charsheet.plexPanel import PLEXPanel
from eve.client.script.ui.shared.neocom.charsheet.securityStatusPanel import SecurityStatusPanel
from eve.client.script.ui.shared.neocom.charsheet.skillsPanel import SkillsPanel
from eve.client.script.ui.shared.neocom.charsheet.skinsPanel import SkinsPanel
from eve.client.script.ui.shared.neocom.charsheet.standingsPanel import StandingsPanel
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipHeaderDescriptionWrapper
from eve.client.script.ui.util.uix import GetTextHeight
from localization import GetByLabel

class CharacterSheetWindow(uicontrols.Window):
    __guid__ = 'form.CharacterSheet'
    default_width = 497
    default_height = 456
    default_minSize = (497, 456)
    default_left = 0
    default_top = 32
    default_windowID = 'charactersheet'
    default_captionLabelPath = 'UI/CharacterSheet/CharacterSheetWindow/CharacterSheetCaption'
    default_descriptionLabelPath = 'Tooltips/Neocom/CharacterSheet_description'
    default_iconNum = 'res:/ui/Texture/WindowIcons/charactersheet.png'
    default_scope = 'station_inflight'
    default_topParentHeight = 0
    __notifyevents__ = ['OnGodmaItemChange', 'OnSkillsChanged']

    def OnUIRefresh(self):
        pass

    @telemetry.ZONE_METHOD
    def ApplyAttributes(self, attributes):
        uicontrols.Window.ApplyAttributes(self, attributes)
        panelID = attributes.panelID
        self.loadingHeader = False
        self.loading = False
        self.currPanel = None
        self.topCont = ContainerAutoSize(name='topCont', parent=self.sr.main, align=uiconst.TOTOP, alignMode=uiconst.TOPLEFT, clipChildren=True, padRight=3)
        self.leftCont = Container(name='leftSide', parent=self.sr.main, align=uiconst.TOLEFT, left=const.defaultPadding, width=settings.user.ui.Get('charsheetleftwidth', 200))
        self.panelSelectScroll = uicontrols.Scroll(name='panelSelectScroll', parent=self.leftCont, padding=(0, 4, 0, 4), multiSelect=False)
        self.panelSelectScroll.OnSelectionChange = self.OnSelectEntry
        self.mainCont = Container(name='mainCont', parent=self.sr.main, align=uiconst.TOALL, padRight=4)
        self.ConstructDivider()
        self.panelCont = Container(name='panelCont', parent=self.mainCont)
        self.employmentHistoryPanel = EmploymentHistoryPanel(parent=self.panelCont, state=uiconst.UI_HIDDEN)
        self.jumpClonesPanel = JumpClonesPanel(parent=self.panelCont, state=uiconst.UI_HIDDEN)
        self.killRightsPanel = KillRightsPanel(parent=self.panelCont, state=uiconst.UI_HIDDEN)
        self.attributesPanel = AttributesPanel(parent=self.panelCont, state=uiconst.UI_HIDDEN)
        self.decorationsPanel = DecorationsPanel(parent=self.panelCont, state=uiconst.UI_HIDDEN)
        self.plexPanel = PLEXPanel(parent=self.panelCont, state=uiconst.UI_HIDDEN)
        self.skinsPanel = SkinsPanel(parent=self.panelCont, state=uiconst.UI_HIDDEN, padding=(0, 4, 0, 4))
        self.bioPanel = BioPanel(parent=self.panelCont, state=uiconst.UI_HIDDEN)
        self.implantsBoostersPanel = ImplantsBoostersPanel(parent=self.panelCont, state=uiconst.UI_HIDDEN)
        self.standingsPanel = StandingsPanel(parent=self.panelCont, state=uiconst.UI_HIDDEN)
        self.securityStatusPanel = SecurityStatusPanel(parent=self.panelCont, state=uiconst.UI_HIDDEN)
        self.skillsPanel = SkillsPanel(parent=self.panelCont, state=uiconst.UI_HIDDEN, padTop=2)
        self.combatLogPanel = CombatLogPanel(parent=self.panelCont, state=uiconst.UI_HIDDEN)
        self.ConstructHeader()
        self.ConstructPanelSelectScroll()
        if panelID:
            self.LoadPanel(panelID)
        else:
            self.LoadDefaultPanel()
        self._CheckShowT3ShipLossMessage()

    def LoadDefaultPanel(self):
        self.panelSelectScroll.SetSelected(min(len(TABS) - 1, settings.char.ui.Get('charactersheetselection', 0)))

    def ConstructDivider(self):
        divider = Divider(name='divider', align=uiconst.TOLEFT, width=const.defaultPadding - 1, parent=self.mainCont, state=uiconst.UI_NORMAL)
        divider.Startup(self.leftCont, 'width', 'x', 84, 220)
        self.sr.divider = divider

    def ConstructHeader(self):
        if self.loadingHeader:
            return
        self.loadingHeader = True
        self.topCont.Flush()
        characterName = cfg.eveowners.Get(session.charid).name
        if not getattr(self, 'charMgr', None):
            self.charMgr = sm.RemoteSvc('charMgr')
        if not getattr(self, 'cc', None):
            self.charsvc = sm.GetService('cc')
        self.sr.charinfo = charinfo = self.charMgr.GetPublicInfo(session.charid)
        if settings.user.ui.Get('charsheetExpanded', 1):
            parent = self.topCont
            self.sr.picParent = Container(name='picpar', parent=parent, align=uiconst.TOPLEFT, width=200, height=200, left=const.defaultPadding, top=16)
            self.sr.pic = Sprite(parent=self.sr.picParent, align=uiconst.TOALL, left=1, top=1, height=1, width=1)
            self.sr.pic.OnClick = self.OpenPortraitWnd
            self.sr.pic.cursor = uiconst.UICURSOR_MAGNIFIER
            uicontrols.Frame(parent=self.sr.picParent, opacity=0.2)
            sm.GetService('photo').GetPortrait(session.charid, 256, self.sr.pic)
            infoTextPadding = self.sr.picParent.width + const.defaultPadding * 4
            characterLink = GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=characterName, info=('showinfo', const.typeCharacterAmarr, session.charid))
            self.sr.nameText = uicontrols.EveCaptionMedium(text=characterLink, parent=self.topCont, left=infoTextPadding, top=12, state=uiconst.UI_NORMAL)
            self.sr.raceinfo = raceinfo = cfg.races.Get(charinfo.raceID)
            self.sr.bloodlineinfo = bloodlineinfo = cfg.bloodlines.Get(charinfo.bloodlineID)
            self.sr.schoolinfo = schoolinfo = self.charsvc.GetData('schools', ['schoolID', charinfo.schoolID])
            self.sr.ancestryinfo = ancestryinfo = self.charsvc.GetData('ancestries', ['ancestryID', charinfo.ancestryID])
            if self.destroyed:
                self.loadingHeader = False
                return
            securityStatus = sm.GetService('crimewatchSvc').GetMySecurityStatus()
            roundedSecurityStatus = localization.formatters.FormatNumeric(securityStatus, decimalPlaces=1)
            cloneLocationRow = sm.RemoteSvc('charMgr').GetHomeStationRow()
            if cloneLocationRow:
                stationID = cloneLocationRow.stationID
                cloneLocationSystemID = cloneLocationRow.solarSystemID
                if cloneLocationSystemID:
                    labelPath = 'UI/CharacterSheet/CharacterSheetWindow/CloneLocationHint'
                    cloneLocationHint = GetByLabel(labelPath, locationId=stationID, systemId=cloneLocationSystemID)
                    cloneLocation = cfg.evelocations.Get(cloneLocationSystemID).name
                else:
                    cloneLocationHint = cfg.evelocations.Get(stationID).name
                    cloneLocation = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/UnknownSystem')
            else:
                cloneLocation = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/UnknownSystem')
                cloneLocationHint = ''
            alliance = ''
            if session.allianceid:
                cfg.eveowners.Prime([session.allianceid])
                alliance = (GetByLabel('UI/Common/Alliance'), cfg.eveowners.Get(session.allianceid).name, '')
            faction = ''
            if session.warfactionid:
                fac = sm.StartService('facwar').GetFactionalWarStatus()
                faction = (GetByLabel('UI/Common/Militia'), cfg.eveowners.Get(fac.factionID).name, '')
            bounty = ''
            bountyOwnerIDs = (session.charid, session.corpid, session.allianceid)
            bountyAmount = sm.GetService('bountySvc').GetBounty(*bountyOwnerIDs)
            bountyAmounts = sm.GetService('bountySvc').GetBounties(*bountyOwnerIDs)
            charBounty = 0
            corpBounty = 0
            allianceBounty = 0
            if len(bountyAmounts):
                for ownerID, value in bountyAmounts.iteritems():
                    if util.IsCharacter(ownerID):
                        charBounty = value
                    elif util.IsCorporation(ownerID):
                        corpBounty = value
                    elif util.IsAlliance(ownerID):
                        allianceBounty = value

            bountyHint = GetByLabel('UI/Station/BountyOffice/BountyHint', charBounty=util.FmtISK(charBounty, 0), corpBounty=util.FmtISK(corpBounty, 0), allianceBounty=util.FmtISK(allianceBounty, 0))
            bounty = (GetByLabel('UI/Station/BountyOffice/Bounty'), util.FmtISK(bountyAmount, 0), bountyHint)
            skillPoints = int(sm.GetService('skills').GetSkillPoints())
            textList = [(GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillPoints'), localization.formatters.FormatNumeric(skillPoints, useGrouping=True), ''),
             (GetByLabel('UI/CharacterSheet/CharacterSheetWindow/HomeSystem'), cloneLocation, cloneLocationHint),
             (GetByLabel('UI/CharacterSheet/CharacterSheetWindow/CharacterBackground'), GetByLabel('UI/CharacterSheet/CharacterSheetWindow/CharacterBackgroundInformation', raceName=localization.GetByMessageID(raceinfo.raceNameID), bloodlineName=localization.GetByMessageID(bloodlineinfo.bloodlineNameID), ancestryName=localization.GetByMessageID(ancestryinfo.ancestryNameID)), GetByLabel('UI/CharacterSheet/CharacterSheetWindow/CharacterBackgroundHint')),
             (GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DateOfBirth'), localization.formatters.FormatDateTime(charinfo.createDateTime, dateFormat='long', timeFormat='long'), ''),
             (GetByLabel('UI/CharacterSheet/CharacterSheetWindow/School'), localization.GetByMessageID(schoolinfo.schoolNameID), ''),
             (GetByLabel('UI/Common/Corporation'), cfg.eveowners.Get(session.corpid).name, ''),
             (GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SecurityStatus'), roundedSecurityStatus, localization.formatters.FormatNumeric(securityStatus, decimalPlaces=4))]
            if faction:
                textList.insert(len(textList) - 1, faction)
            if alliance:
                textList.insert(len(textList) - 1, alliance)
            if bounty:
                textList.insert(len(textList), bounty)
            numLines = len(textList) + 2
            mtext = 'Xg<br>' * numLines
            mtext = mtext[:-4]
            th = GetTextHeight(mtext)
            topParentHeight = max(220, th + const.defaultPadding * 2 + 2)
            top = max(34, self.sr.nameText.top + self.sr.nameText.height)
            leftContainer = Container(parent=self.topCont, left=infoTextPadding, top=top, align=uiconst.TOPLEFT)
            rightContainer = Container(parent=self.topCont, top=top, align=uiconst.TOPLEFT)
            subTop = 0
            for label, value, hint in textList:
                label = uicontrols.EveLabelMedium(text=label, parent=leftContainer, idx=0, state=uiconst.UI_NORMAL, align=uiconst.TOPLEFT, top=subTop)
                label.hint = hint
                label._tabMargin = 0
                display = uicontrols.EveLabelMedium(text=value, parent=rightContainer, idx=0, state=uiconst.UI_NORMAL, align=uiconst.TOPLEFT, top=subTop)
                display.hint = hint
                display._tabMargin = 0
                subTop += label.height

            leftContainer.AutoFitToContent()
            rightContainer.left = leftContainer.left + leftContainer.width + 20
            rightContainer.AutoFitToContent()
            self.topCont.EnableAutoSize()
        else:
            self.topCont.DisableAutoSize()
            self.topCont.height = 18
        charsheetExpanded = settings.user.ui.Get('charsheetExpanded', 1)
        if not charsheetExpanded:
            uicontrols.EveLabelMedium(text=characterName, parent=self.topCont, left=8, top=1, state=uiconst.UI_DISABLED)
        expandOptions = [GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Expand'), GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Collapse')]
        a = uicontrols.EveLabelSmall(text=expandOptions[charsheetExpanded], parent=self.topCont, left=15, top=3, state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT, bold=True)
        a.OnClick = self.ToggleGeneral
        expander = Sprite(parent=self.topCont, pos=(3, 2, 11, 11), name='expandericon', state=uiconst.UI_NORMAL, texturePath=['res:/UI/Texture/Shared/expanderDown.png', 'res:/UI/Texture/Shared/expanderUp.png'][charsheetExpanded], align=uiconst.TOPRIGHT)
        expander.OnClick = self.ToggleGeneral
        self.loadingHeader = False

    def LoadPanel(self, panelID):
        for entry in self.panelSelectScroll.GetNodes():
            if entry.key == panelID:
                self.panelSelectScroll.SelectNode(entry)
                return

    def OnSelectEntry(self, node):
        if node != []:
            self._LoadPanel(node[0].key)
            settings.char.ui.Set('charactersheetselection', node[0].idx)

    def _LoadPanel(self, panelID, subPanelID = None):
        if self.loading or self.GetPanelByID(panelID) == self.currPanel:
            return
        self.loading = True
        try:
            if self.currPanel:
                self.currPanel.Hide()
                if hasattr(self.currPanel, 'UnloadPanel'):
                    self.currPanel.UnloadPanel()
            self.currPanel = self.GetPanelByID(panelID)
            self.currPanel.state = uiconst.UI_PICKCHILDREN
            self.currPanel.LoadPanel()
        finally:
            self.loading = False

    def GetPanelByID(self, panelID):
        if panelID == PANEL_STANDINGS:
            return self.standingsPanel
        if panelID == PANEL_SKILLS:
            return self.skillsPanel
        if panelID == PANEL_DECORATIONS:
            return self.decorationsPanel
        if panelID == PANEL_COMBATLOG:
            return self.combatLogPanel
        if panelID == PANEL_ATTRIBUTES:
            return self.attributesPanel
        if panelID == PANEL_IMPLANTSBOOTERS:
            return self.implantsBoostersPanel
        if panelID == PANEL_BIO:
            return self.bioPanel
        if panelID == PANEL_SECURITYSTATUS:
            return self.securityStatusPanel
        if panelID == PANEL_KILLRIGHTS:
            return self.killRightsPanel
        if panelID == PANEL_JUMPCLONES:
            return self.jumpClonesPanel
        if panelID == PANEL_EMPLOYMENT:
            return self.employmentHistoryPanel
        if panelID == PANEL_PLEX:
            return self.plexPanel
        if panelID == PANEL_SHIPSKINS:
            return self.skinsPanel

    def GetActivePanel(self):
        return self.currPanel

    def HideAllPanels(self):
        for panel in self.panelCont.children:
            panel.Hide()

    def OpenPortraitWnd(self, *args):
        PortraitWindow.CloseIfOpen()
        PortraitWindow.Open(charID=session.charid)

    def ToggleGeneral(self, *args):
        charsheetExpanded = not settings.user.ui.Get('charsheetExpanded', 1)
        settings.user.ui.Set('charsheetExpanded', charsheetExpanded)
        self.ConstructHeader()

    def ConstructPanelSelectScroll(self):
        scrolllist = []
        for label, icon, key, UIName, descriptionLabelPath in TABS:
            data = util.KeyVal()
            label = GetByLabel(label)
            data.text = label
            data.label = label
            data.icon = icon
            data.key = key
            data.hint = label
            data.name = UIName
            data.line = False
            data.labeloffset = 4
            data.tooltipPanelClassInfo = TooltipHeaderDescriptionWrapper(header=label, description=GetByLabel(descriptionLabelPath), tooltipPointer=uiconst.POINT_RIGHT_2)
            scrolllist.append(listentry.Get('IconEntry', data=data))

        self.panelSelectScroll.Load(contentList=scrolllist)

    def GetSelected(self):
        return self.panelSelectScroll.GetSelected()

    def DeselectAll(self):
        self.panelSelectScroll.DeselectAll()

    def SetSelected(self, idx):
        self.panelSelectScroll.SetSelected(idx)

    @telemetry.ZONE_METHOD
    def _CheckShowT3ShipLossMessage(self):
        lossMessages = sm.StartService('skills').GetRecentLossMessages()
        for messageTuple in lossMessages:
            messageType, messageDict = messageTuple
            uicore.Message(messageType, messageDict)

        if len(lossMessages):
            sm.GetService('skills').ResetSkillHistory()

    def Close(self, *args, **kwds):
        settings.user.ui.Set('charsheetleftwidth', self.leftCont.width)
        uicontrols.Window.Close(self, *args, **kwds)

    def OnGodmaItemChange(self, item, change):
        self.ConstructHeader()

    def OnSkillsChanged(self, *args):
        self.ConstructHeader()

    @classmethod
    def OpenCertificates(cls):
        panelID = PANEL_SKILLS_CERTIFICATES
        wnd = cls._OpenSkillSubPanel(panelID)
        return wnd

    @classmethod
    def _OpenSkillSubPanel(cls, panelID):
        wnd = cls.GetIfOpen()
        if wnd:
            wnd.LoadPanel(PANEL_SKILLS)
        else:
            wnd = cls.Open(panelID=PANEL_SKILLS)
        uthread.new(wnd.GetPanelByID(PANEL_SKILLS).SelectTab, panelID)
        return wnd

    @classmethod
    def OpenSkills(cls):
        panelID = PANEL_SKILLS_SKILLS
        wnd = cls._OpenSkillSubPanel(panelID)
        return wnd

    @classmethod
    def OpenSkillHistory(cls):
        panelID = PANEL_SKILLS_HISTORY
        wnd = cls._OpenSkillSubPanel(panelID)
        return wnd

    @classmethod
    def OpenSkillHistoryHilightSkills(cls, skillIDs):
        uthread.new(cls._HighlightSkillHistorySkills, skillTypeIds=skillIDs)

    @classmethod
    def _HighlightSkillHistorySkills(cls, skillTypeIds):
        wnd = cls.OpenSkillHistory()
        wnd.GetPanelByID(PANEL_SKILLS).HighlightSkillHistorySkills(skillTypeIds)

    def DeselectAllNodes(self, wnd):
        for node in wnd.sr.scroll.GetNodes():
            wnd.sr.scroll._DeselectNode(node)
