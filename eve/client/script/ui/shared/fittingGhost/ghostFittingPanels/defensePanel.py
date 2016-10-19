#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\ghostFittingPanels\defensePanel.py
from collections import defaultdict
from carbon.common.script.util.format import FmtAmt
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.util.various_unsorted import IsUnder, GetAttrs
from eve.client.script.ui.control.damageGaugeContainers import DamageGaugeContainerFitting
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelMedium, Label
from eve.client.script.ui.control.eveWindowUnderlay import WindowUnderlay
from eve.client.script.ui.shared.fitting.fittingUtil import PASSIVESHIELDRECHARGE, GetMultiplyColor2, ARMORREPAIRRATEACTIVE, HULLREPAIRRATEACTIVE, SHIELDBOOSTRATEACTIVE, FONTCOLOR_DEFAULT2, FONTCOLOR_HILITE2, GetDefensiveLayersInfo, GetShipAttributeWithDogmaLocation, PANEL_WIDTH
from eve.client.script.ui.shared.fittingGhost.fittingUtilGhost import GetColoredText
from eve.client.script.ui.station.fitting.fittingTooltipUtils import SetFittingTooltipInfo
from eve.client.script.ui.shared.fitting.panels.basePanel import BaseMenuPanel
from dogma import const as dogmaConst
from localization import GetByLabel, GetByMessageID
MAXDEFENCELABELWIDTH = 62
MAXDEFENCELABELHEIGHT = 32
MILLION = 1000000
SECONDS_DAY = 86400
BAR_COLORS = [(0.1, 0.37, 0.55, 1.0),
 (0.55, 0.1, 0.1, 1.0),
 (0.45, 0.45, 0.45, 1.0),
 (0.55, 0.37, 0.1, 1.0)]
resAttributeIDs = ((dogmaConst.attributeEmDamageResonance, 'ResistanceHeaderEM'),
 (dogmaConst.attributeThermalDamageResonance, 'ResistanceHeaderThermal'),
 (dogmaConst.attributeKineticDamageResonance, 'ResistanceHeaderKinetic'),
 (dogmaConst.attributeExplosiveDamageResonance, 'ResistanceHeaderExplosive'))
rowsInfo = [('UI/Common/Shield', 'shield', 'ui_1_64_13', 'UI/Fitting/FittingWindow/ShieldHPAndRecharge'), ('UI/Common/Armor', 'armor', 'ui_1_64_9', 'UI/Common/Armor'), ('UI/Fitting/Structure', 'structure', 'ui_2_64_12', 'UI/Fitting/Structure')]
DATASET_FOR_REPAIRERS = {ARMORREPAIRRATEACTIVE: ('UI/Fitting/FittingWindow/ArmorRepairRate',
                         (const.groupArmorRepairUnit, const.groupFueledArmorRepairer),
                         dogmaConst.attributeArmorDamageAmount,
                         const.attributeChargedArmorDamageMultiplier,
                         'ui_1_64_11'),
 HULLREPAIRRATEACTIVE: ('UI/Fitting/FittingWindow/HullRepairRate',
                        (const.groupHullRepairUnit,),
                        dogmaConst.attributeStructureDamageAmount,
                        None,
                        'ui_1337_64_22'),
 SHIELDBOOSTRATEACTIVE: ('UI/Fitting/FittingWindow/ShieldBoostRate',
                         (const.groupShieldBooster, const.groupFueledShieldBooster),
                         dogmaConst.attributeShieldBonus,
                         None,
                         'ui_2_64_3')}

class DefensePanel(BaseMenuPanel):
    col1Width = 90

    def ApplyAttributes(self, attributes):
        BaseMenuPanel.ApplyAttributes(self, attributes)

    def LoadPanel(self, initialLoad = False):
        self.Flush()
        self.ResetStatsDicts()
        self.display = True
        tRow = Container(name='topRow', parent=self, align=uiconst.TOTOP, height=32, padTop=5)
        self.AddBestRepairPicker(tRow)
        self.AddColumnHeaderIcons(tRow)
        for idx in xrange(len(rowsInfo)):
            self.AddRow(idx)

        BaseMenuPanel.FinalizePanelLoading(self, initialLoad)

    def AddBestRepairPicker(self, tRow):
        self.bestRepairPickerPanel = None
        bestPar = Container(name='bestPar', parent=tRow, align=uiconst.TOPLEFT, height=32, width=self.col1Width, state=uiconst.UI_NORMAL)
        bestPar.OnClick = self.ExpandBestRepair
        SetFittingTooltipInfo(targetObject=bestPar, tooltipName='ActiveDefenses')
        expandIcon = Icon(name='expandIcon', icon='ui_38_16_229', parent=bestPar, state=uiconst.UI_DISABLED, align=uiconst.BOTTOMRIGHT)
        numPar = Container(name='numPar', parent=bestPar, pos=(4, 17, 11, 11), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED)
        numLabel = EveLabelMedium(text='', parent=numPar, atop=-1, state=uiconst.UI_DISABLED, align=uiconst.CENTER, shadowOffset=(0, 0))
        Fill(parent=numPar, color=BAR_COLORS[1])
        self.activeBestRepairNumLabel = numLabel
        icon = Icon(parent=bestPar, state=uiconst.UI_DISABLED, width=32, height=32)
        statusLabel = Label(name='statusLabel', text='', parent=bestPar, left=icon.left + icon.width, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT)
        self.activeBestRepairLabel = statusLabel
        self.activeBestRepairParent = bestPar
        self.activeBestRepairIcon = icon

    def AddColumnHeaderIcons(self, tRow):
        step = (PANEL_WIDTH - self.col1Width) / 4
        left = self.col1Width
        for attributeID, tooltipName in resAttributeIDs:
            attribute = cfg.dgmattribs.Get(attributeID)
            icon = Icon(graphicID=attribute.iconID, parent=tRow, pos=(left + (step - 32) / 2 + 4,
             0,
             32,
             32), idx=0, hint=attribute.displayName)
            SetFittingTooltipInfo(icon, tooltipName=tooltipName, includeDesc=True)
            left += step

    def AddRow(self, idx):
        labelPath, what, iconNo, labelHintPath = rowsInfo[idx]
        rowName = 'row_%s' % what
        row = Container(name='row_%s' % rowName, parent=self, align=uiconst.TOTOP, height=32)
        mainIcon = Icon(icon=iconNo, parent=row, pos=(0, 0, 32, 32), ignoreSize=True)
        mainIcon.hint = GetByLabel(labelPath)
        statusLabel = Label(text='', parent=row, left=mainIcon.left + mainIcon.width, state=uiconst.UI_NORMAL, align=uiconst.CENTERLEFT, width=62)
        statusLabel.hint = GetByLabel(labelHintPath)
        self.statsLabelsByIdentifier[what] = statusLabel
        dmgContainer = Container(parent=row, name='dmgContainer', left=self.col1Width)
        gaugeCont = DamageGaugeContainerFitting(parent=dmgContainer)
        self.statsContsByIdentifier[what] = gaugeCont

    def SetEffectiveHpHeader(self):
        effectiveHpInfo = self.controller.GetEffectiveHp()
        text = GetByLabel('UI/Fitting/FittingWindow/ColoredEffectiveHp', color='', effectiveHp=effectiveHpInfo.value)
        coloredText = GetColoredText(isBetter=effectiveHpInfo.isBetterThanBefore, text=text)
        self.SetStatusText(coloredText)

    def UpdateDefensePanel(self):
        self.SetEffectiveHpHeader()
        allDefensiveLayersInfo = GetDefensiveLayersInfo(self.controller)
        for whatLayer, layerInfo in allDefensiveLayersInfo.iteritems():
            hpInfo = layerInfo.hpInfo
            isRechargable = layerInfo.isRechargable
            layerResistancesInfo = layerInfo.resistances
            if not hpInfo:
                continue
            self.SetDefenseLayerText(hpInfo, whatLayer, isRechargable)
            self.UpdateGaugesForLayer(layerResistancesInfo, whatLayer)

    def UpdateGaugesForLayer(self, layerResistancesInfo, whatLayer):
        dmgGaugeCont = self.statsContsByIdentifier.get(whatLayer, None)
        for dmgType, valueInfo in layerResistancesInfo.iteritems():
            value = valueInfo.value
            if self.state != uiconst.UI_HIDDEN and dmgGaugeCont:
                text = GetByLabel('UI/Fitting/FittingWindow/ColoredResistanceLabel', number=100 - int(value * 100))
                coloredText = GetColoredText(isBetter=valueInfo.isBetterThanBefore, text=text)
                attributeInfo = cfg.dgmattribs.Get(valueInfo.attributeID)
                tooltipTitleID = attributeInfo.tooltipTitleID
                if tooltipTitleID:
                    tooltipText = GetByMessageID(attributeInfo.tooltipTitleID)
                else:
                    tooltipText = attributeInfo.displayName
                info = {'value': 1.0 - value,
                 'valueText': coloredText,
                 'text': tooltipText,
                 'dmgType': dmgType}
                dmgGaugeCont.UpdateGauge(info, animate=True)

    def SetDefenseLayerText(self, statusInfo, what, isRechargable):
        label = self.statsLabelsByIdentifier.get(what, None)
        if not label:
            return
        hpText = self._GetFormattedValue(statusInfo.value)
        text = None
        if isRechargable:
            rechargeTimeInfo = self.controller.GetRechargeRate()
            rechargeValue = rechargeTimeInfo.value
            if rechargeValue < SECONDS_DAY:
                text = GetByLabel('UI/Fitting/FittingWindow/ColoredHitpointsAndRechargeTime2', hp=hpText, rechargeTime=int(rechargeValue * 0.001), startColorTag1='', startColorTag2='', endColorTag='')
        if text is None:
            text = GetByLabel('UI/Fitting/FittingWindow/ColoredHp2', hp=hpText)
        coloredText = GetColoredText(isBetter=statusInfo.isBetterThanBefore, text=text)
        maxTextHeight = MAXDEFENCELABELHEIGHT
        maxTextWidth = MAXDEFENCELABELWIDTH
        textWidth, textHeight = label.MeasureTextSize(coloredText)
        fontsize = label.default_fontsize
        while textWidth > maxTextWidth or textHeight > maxTextHeight:
            fontsize -= 1
            textWidth, textHeight = label.MeasureTextSize(coloredText, fontsize=fontsize)

        label.fontsize = fontsize
        label.text = coloredText

    def _GetFormattedValue(self, value):
        if value > 100 * MILLION:
            fmt = 'sn'
        else:
            fmt = 'ln'
        valueText = FmtAmt(int(value), fmt=fmt)
        return valueText

    def ExpandBestRepair(self, *args):
        if self.bestRepairPickerPanel is not None:
            self.PickBestRepair(None)
            return
        self.sr.bestRepairPickerCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self.OnGlobalMouseUp_BestRepair)
        bestRepairParent = self.activeBestRepairParent
        l, t, w, h = bestRepairParent.GetAbsolute()
        bestRepairPickerPanel = Container(parent=uicore.desktop, name='bestRepairPickerPanel', align=uiconst.TOPLEFT, width=150, height=100, left=l, top=t + h, state=uiconst.UI_NORMAL, idx=0, clipChildren=1)
        subpar = Container(parent=bestRepairPickerPanel, name='subpar', align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN, pos=(0, 0, 0, 0))
        active = settings.user.ui.Get('activeBestRepair', PASSIVESHIELDRECHARGE)
        top = 0
        mw = 32
        for flag, hint, iconNo in ((ARMORREPAIRRATEACTIVE, GetByLabel('UI/Fitting/FittingWindow/ArmorRepairRate'), 'ui_1_64_11'),
         (HULLREPAIRRATEACTIVE, GetByLabel('UI/Fitting/FittingWindow/HullRepairRate'), 'ui_1337_64_22'),
         (PASSIVESHIELDRECHARGE, GetByLabel('UI/Fitting/FittingWindow/PassiveShieldRecharge'), 'ui_22_32_7'),
         (SHIELDBOOSTRATEACTIVE, GetByLabel('UI/Fitting/FittingWindow/ShieldBoostRate'), 'ui_2_64_3')):
            entry = Container(name='entry', parent=subpar, align=uiconst.TOTOP, height=32, state=uiconst.UI_NORMAL)
            icon = Icon(icon=iconNo, parent=entry, state=uiconst.UI_DISABLED, pos=(0, 0, 32, 32), ignoreSize=True)
            label = Label(text=hint, parent=entry, left=icon.left + icon.width, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT)
            entry.OnClick = (self.PickBestRepair, entry)
            entry.OnMouseEnter = (self.OnMouseEnterBestRepair, entry)
            entry.bestRepairFlag = flag
            entry.sr.hilite = Fill(parent=entry, state=uiconst.UI_HIDDEN)
            if active == flag:
                Fill(parent=entry, color=(1.0, 1.0, 1.0, 0.125))
            top += 32
            mw = max(label.textwidth + label.left + 6, mw)

        bestRepairPickerPanel.width = mw
        bestRepairPickerPanel.height = 32
        bestRepairPickerPanel.opacity = 0.0
        WindowUnderlay(bgParent=bestRepairPickerPanel)
        self.bestRepairPickerPanel = bestRepairPickerPanel
        uicore.effect.MorphUI(bestRepairPickerPanel, 'height', top, 250.0)
        uicore.effect.MorphUI(bestRepairPickerPanel, 'opacity', 1.0, 250.0, float=1)

    def UpdateBestRepair(self, item, multiplyShieldCapacity, multiplyShieldRecharge):
        if not self.panelLoaded:
            return
        activeRepairLabel = self.activeBestRepairLabel
        activeBestRepairParent = self.activeBestRepairParent
        activeBestRepairNumLabel = self.activeBestRepairNumLabel
        activeBestRepairIcon = self.activeBestRepairIcon
        if not activeRepairLabel:
            return
        activeBestRepair = settings.user.ui.Get('activeBestRepair', PASSIVESHIELDRECHARGE)
        if activeBestRepair == PASSIVESHIELDRECHARGE:
            self.UpdatePassiveShieldRecharge(multiplyShieldCapacity, multiplyShieldRecharge)
        else:
            hintPath, groupIDs, repairAttributeID, chargeMultiplierAttributeID, iconNum = self.GetDataSetForRepairers(activeBestRepair)
            hint = GetByLabel(hintPath)
            activeBestRepairParent.hint = hint
            modulesAndCharges = self.FindModulesAndChargesByGroups(groupIDs)
            color = FONTCOLOR_DEFAULT2
            if item and item.groupID in groupIDs:
                modulesAndCharges += [(item, None)]
                color = FONTCOLOR_HILITE2
            if modulesAndCharges:
                totalHpPerSec = self.GetTotalHpPerSec(modulesAndCharges, repairAttributeID, chargeMultiplierAttributeID)
                if totalHpPerSec:
                    text = GetByLabel('UI/Fitting/FittingWindow/ColoredPassiveRepairRate', hpPerSec=totalHpPerSec)
                    activeRepairText = self.GetTextWithColor(color, text)
                    activeRepairLabel.text = activeRepairText
                else:
                    activeRepairLabel.text = 0
                text = GetByLabel('UI/Fitting/FittingWindow/ColoredBestRepairNumber', numberOfModules=len(modulesAndCharges))
                activeBestRepairNumText = self.GetTextWithColor(color, text)
                activeBestRepairNumLabel.bold = True
                activeBestRepairNumLabel.text = activeBestRepairNumText
                activeBestRepairNumLabel.parent.state = uiconst.UI_DISABLED
            else:
                activeRepairLabel.text = GetByLabel('UI/Fitting/FittingWindow/NoModule')
                activeBestRepairNumLabel.text = GetByLabel('UI/Fitting/FittingWindow/NoModuleNumber')
                activeBestRepairNumLabel.parent.state = uiconst.UI_DISABLED
            activeBestRepairIcon.LoadIcon(iconNum, ignoreSize=True)

    def FindModulesAndChargesByGroups(self, groupIDs):
        modulesAndCharges = []
        modulesByFlagID = self.controller.GetFittedModulesByFlagID()
        for eachFlag in const.fittingFlags:
            module = modulesByFlagID.get((eachFlag, False), None)
            if not module:
                continue
            if module.groupID not in groupIDs:
                continue
            charge = modulesByFlagID.get((eachFlag, True), None)
            modulesAndCharges.append((module, charge))

        return modulesAndCharges

    def GetDataSetForRepairers(self, activeBestRepair):
        return DATASET_FOR_REPAIRERS[activeBestRepair]

    def GetTextWithColor(self, color, text):
        activeRepairText = '<color=%s>' % color
        activeRepairText += text
        activeRepairText += '</color>'
        return activeRepairText

    def UpdatePassiveShieldRecharge(self, multiplyShieldCapacity, multiplyShieldRecharge):
        shieldCapacity = self.GetShipAttribute(dogmaConst.attributeShieldCapacity)
        shieldRR = self.GetShipAttribute(dogmaConst.attributeShieldRechargeRate)
        activeRepairText = '<color=%s>' % hex(GetMultiplyColor2(multiplyShieldRecharge))
        hpPerSec = int(2.5 * (shieldCapacity * multiplyShieldCapacity) / (shieldRR * multiplyShieldRecharge / 1000.0))
        activeRepairText += GetByLabel('UI/Fitting/FittingWindow/ColoredPassiveRepairRate', hpPerSec=hpPerSec)
        activeRepairText += '</color>'
        self.activeBestRepairLabel.text = activeRepairText
        self.activeBestRepairParent.hint = GetByLabel('UI/Fitting/FittingWindow/PassiveShieldRecharge')
        self.activeBestRepairNumLabel.parent.state = uiconst.UI_HIDDEN
        shieldIconID = cfg.dgmattribs.Get(dogmaConst.attributeShieldCapacity).iconID
        self.activeBestRepairIcon.LoadIcon(shieldIconID, ignoreSize=True)

    def GetTotalHpPerSec(self, modulesAndCharges, repairAttributeID, chargeMultiplierAttributeID = None):
        hpsAndDurations = []
        totalPerSec = 0

        def GetHpPerSec(hpValue, durationValue):
            return hpValue / (durationValue / 1000.0)

        for module, charges in modulesAndCharges:
            dogmaItem = self.dogmaLocation.dogmaItems.get(module.itemID, None)
            include = self.IncludeModuleInHpCalculation(dogmaItem)
            if not include:
                continue
            shipID = self.dogmaLocation.GetCurrentShipID()
            if dogmaItem and dogmaItem.locationID == shipID:
                duration = self.dogmaLocation.GetAccurateAttributeValue(dogmaItem.itemID, dogmaConst.attributeDuration)
                hp = self.dogmaLocation.GetAccurateAttributeValue(dogmaItem.itemID, repairAttributeID)
                multiplier = 1.0
                if charges and chargeMultiplierAttributeID:
                    multiplier = self.dogmaLocation.GetAccurateAttributeValue(dogmaItem.itemID, chargeMultiplierAttributeID)
                hp *= multiplier
                totalPerSec += GetHpPerSec(hp, duration)
                hpsAndDurations.append((hp, duration))
            else:
                duration = self.dogmaLocation.dogmaStaticMgr.GetTypeAttribute2(module.typeID, dogmaConst.attributeDuration)
                hp = self.dogmaLocation.dogmaStaticMgr.GetTypeAttribute2(module.typeID, repairAttributeID)
                if charges:
                    multiplier = self.dogmaLocation.dogmaStaticMgr.GetTypeAttribute2(module.typeID, chargeMultiplierAttributeID)
                    hp *= multiplier
                totalPerSec += GetHpPerSec(hp, duration)

        return totalPerSec

    def IncludeModuleInHpCalculation(self, module):
        if not sm.GetService('fittingSvc').IsShipSimulated():
            return True
        if not module:
            return False
        typeEffectInfo = sm.GetService('ghostFittingSvc').GetDefaultAndOverheatEffect(module.typeID)
        if not typeEffectInfo.defaultEffect or not typeEffectInfo.isActivatable:
            return True
        if not module.IsActive():
            return False
        return True

    def GetShipAttribute(self, attributeID):
        dogmaLocation = self.controller.GetDogmaLocation()
        shipID = dogmaLocation.GetCurrentShipID()
        return GetShipAttributeWithDogmaLocation(dogmaLocation, shipID, attributeID)

    def OnGlobalMouseUp_BestRepair(self, fromwhere, *etc):
        if self.bestRepairPickerPanel:
            if uicore.uilib.mouseOver == self.bestRepairPickerPanel or IsUnder(fromwhere, self.bestRepairPickerPanel) or fromwhere == self.activeBestRepairParent:
                import log
                log.LogInfo('Combo.OnGlobalClick Ignoring all clicks from comboDropDown')
                return 1
        if self.bestRepairPickerPanel and not self.bestRepairPickerPanel.destroyed:
            self.bestRepairPickerPanel.Close()
        self.bestRepairPickerPanel = None
        if self.sr.bestRepairPickerCookie:
            uicore.event.UnregisterForTriuiEvents(self.sr.bestRepairPickerCookie)
        self.sr.bestRepairPickerCookie = None
        return 0

    def PickBestRepair(self, entry):
        if entry:
            settings.user.ui.Set('activeBestRepair', entry.bestRepairFlag)
            self.controller.UpdateStats()
        if self.bestRepairPickerPanel and not self.bestRepairPickerPanel.destroyed:
            self.bestRepairPickerPanel.Close()
        self.bestRepairPickerPanel = None
        if self.sr.bestRepairPickerCookie:
            uicore.event.UnregisterForTriuiEvents(self.sr.bestRepairPickerCookie)
        self.sr.bestRepairPickerCookie = None

    def OnMouseEnterBestRepair(self, entry):
        for each in entry.parent.children:
            if GetAttrs(each, 'sr', 'hilite'):
                each.sr.hilite.state = uiconst.UI_HIDDEN

        entry.sr.hilite.state = uiconst.UI_DISABLED
