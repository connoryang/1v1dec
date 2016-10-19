#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\squadrons\squadronAbilityTooltip.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbon.common.script.util.timerstuff import AutoTimer
from eve.client.script.ui.control.tooltips import TooltipPanel, ShortcutHint
from eve.client.script.ui.crimewatch.crimewatchConst import Colors as CrimeWatchColors
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from localization import GetByMessageID, GetByLabel

class SquadronTooltipModuleWrapper(TooltipBaseWrapper):

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = SquadronAbilityTooltip(parent=parent, owner=owner, idx=idx)
        return self.tooltipPanel


class SquadronAbilityTooltip(TooltipPanel):

    def ApplyAttributes(self, attributes):
        TooltipPanel.ApplyAttributes(self, attributes)
        self.columns = 4
        self.margin = (4, 4, 4, 4)
        self.cellPadding = 0
        self.cellSpacing = 0
        self.labelPadding = (4, 2, 4, 2)
        self.SetBackgroundAlpha(0.75)
        self.controller = getattr(self.owner, 'controller', None)

    def LoadTooltip(self):
        if not self.owner:
            return
        self.ability = self.controller.GetAbilityInfo()
        self.abilityNameID = self.ability.displayNameID
        self.abilityTooltipID = self.ability.tooltipTextID
        self.slotID = self.controller.slotID
        self.UpdateToolTips()
        self._toolTooltipUpdateTimer = AutoTimer(1000, self.UpdateToolTips)

    def UpdateToolTips(self):
        if self.destroyed or self.beingDestroyed or self.owner is None:
            self._toolTooltipUpdateTimer = None
            return
        self.Flush()
        self.AddTypeAndIcon()
        self.AddAbilityInfo()
        safetyLevel = self.owner.GetSafetyWarning()
        if safetyLevel is not None:
            self.AddSafetyLevelWarning(safetyLevel)

    def AddAbilityInfo(self):
        text = GetByMessageID(self.abilityTooltipID)
        label = self.AddRowWithText(text)

    def AddSafetyLevelWarning(self, safetyLevel):
        if safetyLevel == const.shipSafetyLevelNone:
            iconColor = CrimeWatchColors.Criminal.GetRGBA()
            text = GetByLabel('UI/Crimewatch/SafetyLevel/ModuleRestrictionTooltip', color=CrimeWatchColors.Criminal.GetHex())
        else:
            iconColor = CrimeWatchColors.Suspect.GetRGBA()
            text = GetByLabel('UI/Crimewatch/SafetyLevel/ModuleRestrictionTooltip', color=CrimeWatchColors.Suspect.GetHex())
        texturePath = 'res:/UI/Texture/Crimewatch/Crimewatch_SuspectCriminal.png'
        icon, label = self.AddRowWithIconAndText(text, texturePath, iconSize=16)
        icon.color.SetRGBA(*iconColor)

    def AddTypeAndIcon(self, iconSize = 26, minRowSize = 30):
        self.FillRow()
        self.AddSpacer(height=minRowSize, width=0)
        iconID = self.ability.iconID
        iconCont = Container(pos=(0,
         0,
         iconSize,
         iconSize), align=uiconst.CENTER)
        iconObj = Icon(parent=iconCont, pos=(0,
         0,
         iconSize,
         iconSize), icon=iconID, align=uiconst.TOPLEFT, ignoreSize=True)
        self.AddCell(iconCont, cellPadding=2)
        nameColSpan = self.columns - 3
        abilityName = GetByMessageID(self.abilityNameID)
        label = abilityText = '<b>%s</b>' % abilityName
        labelObj = self.AddLabelMedium(text=label, align=uiconst.CENTERLEFT, cellPadding=self.labelPadding, colSpan=nameColSpan)
        abilityShortcut = uicore.cmd.GetShortcutStringByFuncName('CmdActivateHighPowerSlot%i' % (self.slotID + 1))
        shortcutObj = ShortcutHint(text=abilityShortcut)
        shortcutObj.width += 10
        shortcutObj.padLeft = 10
        self.AddCell(shortcutObj)
        return (iconObj, labelObj)

    def AddRowWithText(self, text, minRowSize = 30):
        self.FillRow()
        self.AddSpacer(height=minRowSize, width=0)
        self.AddCell()
        label = self.AddLabelMedium(text=text, colSpan=self.columns - 2, align=uiconst.CENTERLEFT, cellPadding=self.labelPadding, wrapWidth=300)
        self.FillRow()
        return label

    def AddRowWithIconAndText(self, text, texturePath = None, iconID = None, iconSize = 24, minRowSize = 30):
        self.FillRow()
        self.AddSpacer(height=minRowSize, width=0)
        icon = self.AddIconCell(texturePath or iconID, iconSize=iconSize)
        label = self.AddLabelMedium(text=text, colSpan=self.columns - 2, align=uiconst.CENTERLEFT, cellPadding=self.labelPadding)
        self.FillRow()
        return (icon, label)

    def AddIconCell(self, texturePath = None, iconID = None, iconSize = 24):
        icon = Icon(pos=(0,
         0,
         iconSize,
         iconSize), align=uiconst.CENTER, ignoreSize=True, state=uiconst.UI_DISABLED, icon=texturePath or iconID)
        self.AddCell(icon)
        return icon
