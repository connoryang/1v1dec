#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\ghostFittingPanels\offensePanel.py
from carbonui import const as uiconst
from carbonui.primitives.sprite import Sprite
from dogma.attributes.format import GetFormattedAttributeAndValueAllowZero
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.station.fitting.fittingTooltipUtils import SetFittingTooltipInfo
from eve.client.script.ui.shared.fitting.panels.basePanel import BaseMenuPanel
from localization import GetByLabel
import uthread

class OffensePanel(BaseMenuPanel):
    damageStats = (('turretDps', 'res:/UI/Texture/Icons/26_64_1.png', 'DamagePerSecondTurrets'),
     ('droneDps', 'res:/UI/Texture/Icons/drones.png', 'DamagePerSecondDrones'),
     ('missileDps', 'res:/UI/Texture/Icons/81_64_16.png', 'DamagePerSecondMissiles'),
     ('alphaStrike', '', 'AlpaStrike'))
    iconSize = 26

    def ApplyAttributes(self, attributes):
        BaseMenuPanel.ApplyAttributes(self, attributes)

    def LoadPanel(self, initialLoad = False):
        self.Flush()
        self.ResetStatsDicts()
        self.display = True
        parentGrid = self.GetValueParentGrid()
        for dps, texturePath, tooltipName in self.damageStats:
            c = self.GetValueCont(self.iconSize)
            parentGrid.AddCell(cellObject=c)
            icon = Sprite(texturePath=texturePath, parent=c, align=uiconst.CENTERLEFT, pos=(0,
             0,
             self.iconSize,
             self.iconSize), state=uiconst.UI_DISABLED)
            SetFittingTooltipInfo(targetObject=c, tooltipName=tooltipName)
            label = EveLabelMedium(text='', parent=c, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT)
            self.statsLabelsByIdentifier[dps] = label
            self.statsIconsByIdentifier[dps] = icon
            self.statsContsByIdentifier[dps] = c

        BaseMenuPanel.FinalizePanelLoading(self, initialLoad)

    def UpdateOffenseStats(self):
        uthread.new(self._UpdateOffenseStats)

    def _UpdateOffenseStats(self):
        itemID = self.dogmaLocation.GetCurrentShipID()
        dpsInfo = self.dogmaLocation.GetTurretAndMissileDps(itemID)
        turretDpsText = GetByLabel('UI/Fitting/FittingWindow/DpsLabel', dps=dpsInfo.turretDps)
        if getattr(dpsInfo, 'turretDpsWithReload', 0) and dpsInfo.turretDpsWithReload != dpsInfo.turretDps:
            turretDpsText += ' (%.1f)' % dpsInfo.turretDpsWithReload
        self.SetLabel('turretDps', turretDpsText)
        missileDpsText = GetByLabel('UI/Fitting/FittingWindow/DpsLabel', dps=dpsInfo.missileDps)
        if getattr(dpsInfo, 'missileDpsWithReload', 0) and dpsInfo.missileDpsWithReload != dpsInfo.missileDps:
            missileDpsText += ' (%.1f)' % dpsInfo.missileDpsWithReload
        self.SetLabel('missileDps', missileDpsText)
        activeDrones = self.dogmaLocation.GetActiveDrones()
        droneDps, drones = self.dogmaLocation.GetOptimalDroneDamage2(itemID, activeDrones)
        droneText = GetByLabel('UI/Fitting/FittingWindow/DpsLabel', dps=droneDps)
        self.SetLabel('droneDps', droneText)
        alphaStrike = self.dogmaLocation.GetAlphaStrike()
        alphaText = GetFormattedAttributeAndValueAllowZero(const.attributeDamage, alphaStrike).value
        self.SetLabel('alphaStrike', alphaText)
        totalDps = dpsInfo.turretDps + dpsInfo.missileDps + droneDps
        totalDpsText = GetByLabel('UI/Fitting/FittingWindow/DpsLabel', dps=totalDps)
        self.SetStatusText(totalDpsText)
