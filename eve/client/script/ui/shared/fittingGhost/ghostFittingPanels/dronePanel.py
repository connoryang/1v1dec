#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\ghostFittingPanels\dronePanel.py
from carbon.common.script.util.format import FmtAmt
from carbonui import const as uiconst
from carbonui.primitives.sprite import Sprite
from dogma.attributes.format import GetFormattedAttributeAndValueAllowZero
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.fitting.panels.basePanel import BaseMenuPanel
from shipfitting.droneUtil import GetDroneRanges, GetDroneBandwidth
from localization import GetByLabel

class DronePanel(BaseMenuPanel):
    droneStats = (('bandwidth', 'res:/UI/Texture/Icons/56_64_5.png'),
     ('droneDps', 'res:/UI/Texture/Icons/drones.png'),
     ('droneRange', 'res:/UI/Texture/Icons/22_32_15.png'),
     ('controlRange', 'res:/UI/Texture/Icons/22_32_15.png'))

    def ApplyAttributes(self, attributes):
        BaseMenuPanel.ApplyAttributes(self, attributes)

    def LoadPanel(self, initialLoad = False):
        self.Flush()
        self.ResetStatsDicts()
        self.display = True
        parentGrid = self.GetValueParentGrid()
        iconSize = 32
        for configName, texturePath in self.droneStats:
            valueCont = self.GetValueCont(iconSize)
            parentGrid.AddCell(cellObject=valueCont)
            icon = Sprite(texturePath=texturePath, parent=valueCont, align=uiconst.CENTERLEFT, pos=(0,
             0,
             iconSize,
             iconSize), state=uiconst.UI_DISABLED)
            valueCont.hint = configName
            label = EveLabelMedium(text='', parent=valueCont, left=0, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT)
            self.statsLabelsByIdentifier[configName] = label
            self.statsIconsByIdentifier[configName] = icon
            self.statsContsByIdentifier[configName] = valueCont

        BaseMenuPanel.FinalizePanelLoading(self, initialLoad)

    def UpdateDroneStats(self):
        shipID = self.dogmaLocation.GetCurrentShipID()
        activeDrones = self.dogmaLocation.GetActiveDrones()
        bandwidthUsed, shipBandwidth = GetDroneBandwidth(shipID, self.dogmaLocation, activeDrones)
        bandwithUsedText = FmtAmt(bandwidthUsed)
        shipBandwidthText = GetFormattedAttributeAndValueAllowZero(const.attributeDroneBandwidth, shipBandwidth).value
        bandwidthText = '%s/%s' % (bandwithUsedText, shipBandwidthText)
        self.SetLabel('bandwidth', bandwidthText)
        minDroneRange, maxDroneRange = GetDroneRanges(shipID, self.dogmaLocation, activeDrones)
        minDroneRangeText = GetFormattedAttributeAndValueAllowZero(const.attributeMaxRange, minDroneRange).value
        if minDroneRange == maxDroneRange:
            droneRangeText = minDroneRangeText
        else:
            maxDroneRangeText = GetFormattedAttributeAndValueAllowZero(const.attributeMaxRange, minDroneRange).value
            droneRangeText = '%s<br>%s' % (minDroneRangeText, maxDroneRangeText)
        self.SetLabel('droneRange', droneRangeText)
        droneDps, drones = self.dogmaLocation.GetOptimalDroneDamage2(shipID, activeDrones)
        droneText = GetByLabel('UI/Fitting/FittingWindow/DpsLabel', dps=droneDps)
        self.SetLabel('droneDps', droneText)
        droneControlRange = self.dogmaLocation.GetAttributeValue(session.charid, const.attributeDroneControlDistance)
        controlRangeText = GetFormattedAttributeAndValueAllowZero(const.attributeDroneControlDistance, droneControlRange).value
        self.SetLabel('controlRange', controlRangeText)
