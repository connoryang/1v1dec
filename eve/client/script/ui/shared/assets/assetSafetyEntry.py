#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\assets\assetSafetyEntry.py
from carbon.common.script.sys.serviceConst import ROLE_GMH
from carbon.common.script.util.linkUtil import GetShowInfoLink
from carbonui import const as uiconst
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.baseListEntry import BaseListEntryCustomColumns
from eve.client.script.ui.control.buttons import Button
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.themeColored import LabelThemeColored, FillThemeColored
from eve.client.script.ui.shared.assets.assetSafetyDeliverWindow import AssetSafetyDeliverWindow
from localization import GetByLabel
from localization.formatters import FormatTimeIntervalShortWritten
import blue

class AssetSafetyEntry(BaseListEntryCustomColumns):
    default_name = 'AssetSafetyEntry'
    default_height = 34
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        BaseListEntryCustomColumns.ApplyAttributes(self, attributes)
        self.sr.label = EveLabelMedium(parent=self)
        self.sr.label.display = False
        safetyData = self.node.safetyData
        self.solarSystemID = safetyData['solarSystemID']
        self.assetWrapID = safetyData['assetWrapID']
        wrapName, systemName = AssetSafetyEntry.GetNameAndSystem(safetyData)
        solarSystemName = GetShowInfoLink(const.typeSolarSystem, systemName, self.solarSystemID)
        self.ejectTime = safetyData['ejectTime']
        self.daysUntilCanDeliverConst = safetyData['daysUntilCanDeliverConst']
        self.manualDeliveryTimestamp = self.ejectTime + self.daysUntilCanDeliverConst * const.DAY
        self.autoDeliveryTimestamp = self.ejectTime + safetyData['daysUntilAutoMoveConst'] * const.DAY
        self.nearestNPCStationInfo = safetyData['nearestNPCStationInfo']
        self.AddColumnText(wrapName)
        t = self.AddColumnText(solarSystemName)
        t.state = uiconst.UI_NORMAL
        self.AddColumnAssetSafetyDeliverButton()
        self.AddColumnAssetSafetyTimers()
        self.UpdateProgress()

    def GetMenu(self):
        menu = []
        if session.role & ROLE_GMH:
            subMenu = []
            subMenu.append(('Move Timer 5 days', self.MoveEjectTimeGM, (self.assetWrapID, 5)))
            subMenu.append(('Move Timer 30 days', self.MoveEjectTimeGM, (self.assetWrapID, 30)))
            menu.append(['GM Tools', subMenu])
        return menu

    def MoveEjectTimeGM(self, assetWrapID, days):
        sm.RemoteSvc('structureAssetSafety').MoveEjectTimeGM(assetWrapID, days)

    def GetDeliveryTimesLeft(self):
        now = blue.os.GetWallclockTime()
        solarSystemTimeLeft = self.manualDeliveryTimestamp - now
        autoDeliverTimeLeft = self.autoDeliveryTimestamp - now
        return (solarSystemTimeLeft, autoDeliverTimeLeft)

    def AddColumnAssetSafetyTimers(self):
        colContainer = self.AddColumnContainer()
        timerSprite = Sprite(name='timerSprite', parent=colContainer, align=uiconst.CENTERLEFT, pos=(0, 0, 24, 24), texturePath='res:/UI/Texture/classes/Inventory/hourglass.png')
        timerSprite.hint = GetByLabel('UI/Inventory/AssetSafety/AutoDeliveryHint')
        self.autoTimeLeft = EveLabelMedium(parent=colContainer, align=uiconst.CENTERLEFT, left=timerSprite.left + timerSprite.width + 4)
        stationText = GetShowInfoLink(self.nearestNPCStationInfo['typeID'], self.nearestNPCStationInfo['name'], self.nearestNPCStationInfo['itemID'])
        self.nearestNPCStationLabel = EveLabelMedium(parent=colContainer, align=uiconst.CENTERLEFT, text=stationText, left=135, state=uiconst.UI_NORMAL)

    def AddColumnAssetSafetyDeliverButton(self):
        solarSystemTimeLeft, autoDeliverTimeLeft = self.GetDeliveryTimesLeft()
        colContainer = self.AddColumnContainer()
        self.deliverBtn = DeliverButton(align=uiconst.CENTER, parent=colContainer, func=self.OnDeliverButton, label=GetByLabel('UI/Inventory/AssetSafety/DeliverTo'))
        self.deliverBtn.GetHint = self.GetDeliverBtnHint
        self.SetDeliverBtnState(solarSystemTimeLeft)

    def SetDeliverBtnState(self, solarSystemTimeLeft):
        if solarSystemTimeLeft > 0:
            self.deliverBtn.Disable()
            self.deliverBtn.disabled = False
        else:
            self.deliverBtn.Enable()

    def OnDeliverButton(self, *args):
        AssetSafetyDeliverWindow.Open(assetWrapID=self.assetWrapID, solarSystemID=self.solarSystemID, nearestNPCStationInfo=self.nearestNPCStationInfo, autoDeliveryTimestamp=self.autoDeliveryTimestamp, manualDeliveryTimestamp=self.manualDeliveryTimestamp)

    def GetDeliverBtnHint(self):
        solarSystemTimeLeft, autoDeliverTimeLeft = self.GetDeliveryTimesLeft()
        if solarSystemTimeLeft < 0:
            return GetByLabel('UI/Inventory/AssetSafety/DeliverBtnAvailableHint')
        else:
            formattedTimeLeft = FormatTimeIntervalShortWritten(solarSystemTimeLeft)
            return GetByLabel('UI/Inventory/AssetSafety/DeliverBtnNotAvailableNowHint', timeUntil=formattedTimeLeft)

    def UpdateProgress(self):
        solarSystemTimeLeft, autoDeliverTimeLeft = self.GetDeliveryTimesLeft()
        progress = 1 - solarSystemTimeLeft / (const.DAY * float(self.daysUntilCanDeliverConst))
        self.deliverBtn.SetProgress(progress)
        formattedTimeLeft = FormatTimeIntervalShortWritten(max(0L, autoDeliverTimeLeft))
        self.autoTimeLeft.text = formattedTimeLeft
        self.SetDeliverBtnState(solarSystemTimeLeft)

    @staticmethod
    def GetNameAndSystem(safetyData):
        return [safetyData['wrapName'], cfg.evelocations.Get(safetyData['solarSystemID']).name]

    @staticmethod
    def GetColumnSortValues(safetyData):
        name, systemName = AssetSafetyEntry.GetNameAndSystem(safetyData)
        sortValues = [name.lower(),
         systemName.lower(),
         safetyData['ejectTime'],
         safetyData['ejectTime']]
        return sortValues

    @staticmethod
    def GetHeaders():
        headers = [GetByLabel('UI/Common/Name'),
         GetByLabel('UI/Common/LocationTypes/SolarSystem'),
         GetByLabel('UI/Inventory/AssetSafety/ManualDelivery'),
         GetByLabel('UI/Inventory/AssetSafety/AutoDelivery')]
        return headers

    @staticmethod
    def GetMinimumColWidth():
        textWidth, textHeight = LabelThemeColored.MeasureTextSize(GetByLabel('UI/Inventory/AssetSafety/DeliverTo'))
        return {GetByLabel('UI/Inventory/AssetSafety/ManualDelivery'): textWidth + 30}

    @staticmethod
    def GetDefaultColumnWidth():
        return {GetByLabel('UI/Inventory/AssetSafety/AutoDelivery'): 500}


class DeliverButton(Button):
    default_name = 'deliverButton'

    def ApplyAttributes(self, attributes):
        Button.ApplyAttributes(self, attributes)
        self.progressFill = FillThemeColored(parent=self, name='progressFill', state=uiconst.UI_DISABLED, align=uiconst.TOLEFT_PROP, colorType=uiconst.COLORTYPE_UIHEADER, opacity=1.0)

    def SetProgress(self, progress):
        self.progressFill.width = min(1.0, max(0.0, progress))
