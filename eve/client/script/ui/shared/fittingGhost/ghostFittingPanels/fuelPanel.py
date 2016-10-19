#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\ghostFittingPanels\fuelPanel.py
from carbon.common.script.util.format import FmtDist
from carbonui.primitives.sprite import Sprite
from dogma import const as dogmaConst
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.fitting.panels.attributePanel import AttributePanel
from eve.client.script.ui.shared.fittingGhost.fittingUtilGhost import GetColoredText
from eve.client.script.ui.station.fitting.fittingTooltipUtils import SetFittingTooltipInfo
from eve.common.lib import appConst
from localization import GetByLabel
import carbonui.const as uiconst

class FuelPanel(AttributePanel):
    fuelInfo = ('fuel', '', 'FuelUsage')

    def LoadPanel(self, initialLoad = False):
        AttributePanel.LoadPanel(self, initialLoad)
        parentGrid = self.GetValueParentGrid()
        self.AddFuelUsage(parentGrid)
        AttributePanel.FinalizePanelLoading(self, initialLoad)

    def AddFuelUsage(self, parentGrid):
        iconSize = 32
        alignID, texturePath, tooltipName = self.fuelInfo
        c = self.GetValueCont(iconSize)
        parentGrid.AddCell(cellObject=c)
        icon = Sprite(texturePath=texturePath, parent=c, align=uiconst.CENTERLEFT, pos=(0,
         0,
         iconSize,
         iconSize), state=uiconst.UI_DISABLED)
        SetFittingTooltipInfo(targetObject=c, tooltipName=tooltipName)
        label = EveLabelMedium(text='', parent=c, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT)
        self.statsLabelsByIdentifier[alignID] = label
        self.statsIconsByIdentifier[alignID] = icon
        self.statsContsByIdentifier[alignID] = c

    def UpdateFuelPanel(self):
        self.SetFuelUsageText()

    def SetFuelUsageText(self):
        fuelPerDay = self.controller.GetFuelUsage()
        text = GetByLabel('UI/Fitting/FittingWindow/FuelPerDay', unitsPerDay=fuelPerDay.value)
        coloredText = GetColoredText(isBetter=fuelPerDay.isBetterThanBefore, text=text)
        self.SetLabel(self.fuelInfo[0], coloredText)
