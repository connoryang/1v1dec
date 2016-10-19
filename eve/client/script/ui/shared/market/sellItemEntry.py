#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\market\sellItemEntry.py
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.buttons import ButtonIcon
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.control.eveSinglelineEdit import SinglelineEdit
from eve.client.script.ui.shared.industry.views.errorFrame import ErrorFrame
from eve.client.script.ui.shared.market.buySellItemContainerBase import BuySellItemContainerBase
from eve.client.script.ui.shared.market.deltaContainer import SellDeltaContainer
from eve.client.script.ui.util.uix import GetTechLevelIcon
from eve.common.script.util.eveFormat import FmtISK
import evetypes
from localization import GetByLabel
NA_CHAR = '-'

class SellItemContainer(BuySellItemContainerBase):
    __guid__ = 'uicls.SellItemContainer'
    belowColor = '<color=0xffff5050>'
    aboveColor = '<color=0xff00ff00>'
    totaLabelPath = 'UI/Market/MarketQuote/AskTotal'

    def ApplyAttributes(self, attributes):
        self.item = attributes.item
        self.typeID = self.item.typeID
        BuySellItemContainerBase.ApplyAttributes(self, attributes)
        self.adjustQtyAndPriceTimer = None
        self.isUpdating = False
        self.singleton = self.item.singleton
        self.itemID = self.item.itemID
        self.itemName = evetypes.GetName(self.typeID)
        self.brokersFee = 0.0
        self.salesTax = 0.0
        self.totalSum = 0.0
        self.stationID = attributes.stationID
        self.limits = self.quoteSvc.GetSkillLimits(self.stationID)
        self.solarSystemID = attributes.solarSystemID
        self.regionID = self.GetRegionID()
        self.locationID = self.item.locationID
        self.bestBid = attributes.bestBid
        self.bestPrice = attributes.bestPrice
        self.totalStrikethroughLine = None
        self.priceAmountWarning = None
        self.deltaCont = Container(parent=self, align=uiconst.TORIGHT, width=30)
        theRestCont = Container(name='theRestCont', parent=self, align=uiconst.TOALL)
        self.totalCont = Container(name='totalCont', parent=theRestCont, align=uiconst.TORIGHT_PROP, width=0.3)
        self.priceCont = Container(name='priceCont', parent=theRestCont, align=uiconst.TORIGHT_PROP, width=0.22)
        self.qtyCont = Container(name='qtyCont', parent=theRestCont, align=uiconst.TORIGHT_PROP, width=0.15)
        self.itemCont = Container(name='itemCont', parent=theRestCont, align=uiconst.TORIGHT_PROP, width=0.33)
        self.deleteCont = Container(name='deleteCont', parent=self.itemCont, align=uiconst.TORIGHT, width=24)
        self.deleteButton = ButtonIcon(texturePath='res:/UI/Texture/Icons/73_16_210.png', pos=(0, 0, 16, 16), align=uiconst.CENTERRIGHT, parent=self.deleteCont, hint=GetByLabel('UI/Generic/RemoveItem'), idx=0, func=self.RemoveItem)
        self.deleteCont.display = False
        self.textCont = Container(name='textCont', parent=self.itemCont, align=uiconst.TOALL)
        self.errorBg = ErrorFrame(bgParent=self)
        self.DrawItem()
        self.DrawQty()
        self.DrawPrice()
        self.DrawTotal()
        self.DrawDelta()
        self.estimatedSellCount = self.GetSellCountEstimate()
        self.SetTotalSumAndLabel()
        self.brokersFeePerc = self.limits.GetBrokersFeeForLocation(self.stationID)
        self.UpdateBrokersFee()
        self.GetSalesTax()
        self.ShowNoSellOrders()
        self.UpdateOrderStateInUI()

    def GetRegionID(self):
        return cfg.mapSystemCache.Get(session.solarsystemid2).regionID

    def OnDurationChanged(self, duration):
        self.OnChange()

    def ShowNoSellOrders(self, force = False):
        if self.IsImmediateOrder() and (self.bestBid is None or force):
            uicore.animations.FadeIn(self.errorBg, 0.35, duration=0.3)

    def GetDuration(self):
        from eve.client.script.ui.shared.market.sellMulti import SellItems
        wnd = SellItems.GetIfOpen()
        if not wnd:
            return
        return wnd.durationCombo.GetValue()

    def DrawQty(self):
        qty = self.item.stacksize
        self.qtyEdit = SinglelineEdit(name='qtyEdit', parent=self.qtyCont, align=uiconst.TOTOP, top=11, padLeft=4)
        self.qtyEdit.IntMode(*(1, long(qty)))
        self.qtyEdit.SetValue(qty)
        self.qtyEdit.OnChange = self.OnChange
        self.qtyEdit.hint = GetByLabel('UI/Common/Quantity')

    def DrawPrice(self):
        self.priceEdit = SinglelineEdit(name='priceEdit', parent=self.priceCont, align=uiconst.TOTOP, top=11, padLeft=8)
        self.priceEdit.FloatMode(*(0.01, 9223372036854.0, 2))
        self.priceEdit.SetValue(self.bestPrice)
        self.priceEdit.OnChange = self.OnChange
        self.priceEdit.hint = GetByLabel('UI/Market/MarketQuote/AskPrice')

    def DrawDelta(self):
        self.deltaContainer = SellDeltaContainer(parent=self.deltaCont, delta=self.GetDelta(), func=self.OpenMarket, align=uiconst.CENTERRIGHT)
        self.deltaContainer.LoadTooltipPanel = self.LoadDeltaTooltip
        self.UpdateDelta()

    def GetTradeWndClass(self):
        from eve.client.script.ui.shared.market.sellMulti import SellItems
        return SellItems

    def LoadDeltaTooltip(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric2ColumnTemplate()
        tooltipPanel.cellPadding = (4, 1, 4, 1)
        tooltipPanel.AddLabelLarge(text=GetByLabel('UI/Market/MarketQuote/AskPrice'))
        tooltipPanel.AddLabelLarge(text=FmtISK(self.priceEdit.GetValue()), align=uiconst.CENTERRIGHT)
        tooltipPanel.AddSpacer(1, 8, colSpan=tooltipPanel.columns)
        tooltipPanel.AddLabelMedium(text='%s %s' % (GetByLabel('UI/Market/MarketQuote/RegionalAdverage'), self.GetDeltaText()))
        tooltipPanel.AddLabelMedium(text=FmtISK(self.averagePrice), align=uiconst.CENTERRIGHT)
        tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Market/MarketQuote/BestRegional'))
        bestMatch = tooltipPanel.AddLabelMedium(text='', align=uiconst.CENTERRIGHT)
        bestMatchDetails = tooltipPanel.AddLabelSmall(text='', align=uiconst.CENTERRIGHT, colSpan=tooltipPanel.columns)
        if not self.bestBid:
            bestMatch.text = GetByLabel('UI/Contracts/ContractEntry/NoBids')
            bestMatchDetails.text = GetByLabel('UI/Market/MarketQuote/ImmediateWillFail')
            bestMatch.color = (1.0, 0.275, 0.0, 1.0)
            bestMatchDetails.color = (1.0, 0.275, 0.0, 1.0)
        else:
            bestMatch.text = FmtISK(self.bestBid.price)
            bestMatchText, volRemaining = self.GetBestMatchText()
            bestMatchDetails.text = bestMatchText
            bestMatchDetails.SetAlpha(0.6)
            if volRemaining:
                vol = tooltipPanel.AddLabelSmall(text=volRemaining, align=uiconst.CENTERRIGHT, colSpan=tooltipPanel.columns)
                vol.SetAlpha(0.6)

    def GetBestMatchText(self):
        jumps = max(self.bestBid.jumps - max(0, self.bestBid.range), 0)
        minVolumeText = None
        if jumps == 0 and self.stationID == self.bestBid.stationID:
            jumpText = GetByLabel('UI/Market/MarketQuote/ItemsInSameStation')
        else:
            jumpText = GetByLabel('UI/Market/MarketQuote/JumpsFromThisSystem', jumps=jumps)
        if self.bestBid.minVolume > 1 and self.bestBid.volRemaining >= self.bestBid.minVolume:
            minVolumeText = GetByLabel('UI/Market/MarketQuote/SimpleMinimumVolume', min=self.bestBid.minVolume)
        return (GetByLabel('UI/Market/MarketQuote/SellQuantity', volRemaining=long(self.bestBid.volRemaining), jumpText=jumpText), minVolumeText)

    def DrawItem(self):
        iconCont = Container(parent=self.textCont, align=uiconst.TOLEFT, width=32, padding=4)
        self.iconInnerCont = Container(name='iconInnerCont', parent=iconCont, align=uiconst.CENTERLEFT, pos=(0, 0, 32, 32))
        self.wheel = LoadingWheel(parent=self.iconInnerCont, pos=(0, 0, 48, 48), align=uiconst.CENTER, idx=0)
        self.wheel.display = False
        self.techIcon = Sprite(parent=self.iconInnerCont, pos=(0, 0, 16, 16), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        self.icon = Icon(parent=self.iconInnerCont, typeID=self.typeID, state=uiconst.UI_DISABLED, ignoreSize=True, pos=(0, 0, 32, 32))
        GetTechLevelIcon(self.techIcon, 1, self.typeID)
        itemName = GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=self.itemName, info=('showinfo', self.typeID, self.item.itemID))
        self.itemNameLabel = Label(text=itemName, parent=self.textCont, left=40, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL, autoFadeSides=35, fontsize=12)

    def UpdateBrokersFee(self):
        fee = self.quoteSvc.BrokersFee(self.stationID, self.totalSum, self.brokersFeePerc)
        feeAmount = fee.amt
        self.brokersFee = feeAmount

    def GetSalesTax(self):
        tax = self.totalSum * self.limits['acc']
        self.salesTax = tax

    def GetTotalSum(self):
        self.GetTotalSumAndDisplaySum()
        return self.totalSum

    def GetTotalSumAndDisplaySum(self):
        price = self.GetPrice()
        qty = self.GetQty()
        sumToDisplay = price * qty
        totalSum = sumToDisplay
        if self.IsImmediateOrder():
            if self.estimatedSellCount == 0:
                totalSum = 0
            elif self.estimatedSellCount < qty:
                sumToDisplay = self.estimatedSellCount * price
                totalSum = sumToDisplay
        self.totalSum = totalSum
        return (totalSum, sumToDisplay)

    def UpdateTotalSumLabel(self, totalSum, sumToDisplay):
        self.totalLabel.text = FmtISK(sumToDisplay)
        if sumToDisplay != totalSum:
            self.ConstructTotalStrikethroughLine()
            self.totalStrikethroughLine.width = self.totalLabel.textwidth
        else:
            self.ChangeTotalStrikethroughDisplay(display=False)

    def OnChange(self, *args):
        if self.adjustQtyAndPriceTimer:
            self.adjustQtyAndPriceTimer.KillTimer()
        self.adjustQtyAndPriceTimer = AutoTimer(200, self.AdjustQtyAndPrice_thread, *args)
        self.SetItemLoading()

    def AdjustQtyAndPrice_thread(self, *args):
        self.adjustQtyTimer = None
        if self.destroyed:
            return
        self.estimatedSellCount = self.GetSellCountEstimate()
        self.SetTotalSumAndLabel()
        self.UpdateBrokersFee()
        self.GetSalesTax()
        self.deltaContainer.display = True
        self.UpdateDelta()
        self.wheel.display = False
        self.isUpdating = False
        if self.parentEditFunc:
            self.parentEditFunc(args)
        self.UpdateOrderStateInUI()

    def SetItemLoading(self):
        self.totalLabel.text = NA_CHAR
        self.deltaContainer.display = False
        self.wheel.display = True
        self.isUpdating = True

    def SetTotalSumAndLabel(self):
        totalSum, displaySum = self.GetTotalSumAndDisplaySum()
        self.UpdateTotalSumLabel(totalSum, displaySum)

    def UpdateOrderStateInUI(self):
        duration = self.GetDuration()
        if duration != 0:
            self.ChangePriceAmountWarningDisplay(display=False)
            self.HideNoSellOrders()
            return
        qty = self.GetQty()
        if self.estimatedSellCount == 0:
            self.ShowNoSellOrders(force=True)
            self.ChangePriceAmountWarningDisplay(display=False)
        elif self.estimatedSellCount < qty:
            self.HideNoSellOrders()
            self.PrepareWarningInfo(self.estimatedSellCount, qty)
        else:
            self.HideNoSellOrders()
            self.ChangePriceAmountWarningDisplay(display=False)

    def PrepareWarningInfo(self, estimatedSellCount, qtyToSell):
        self.ConstructPriceAmountWarning()
        self.ConstructQtyBg()
        self.ChangePriceAmountWarningDisplay(display=True)
        self.priceAmountWarning.info = (estimatedSellCount, qtyToSell)

    def GetPrice(self):
        price = self.priceEdit.GetValue()
        return price

    def GetQty(self):
        qty = self.qtyEdit.GetValue()
        return qty

    def GetQtyToSell(self):
        qty = self.GetQty()
        if self.IsImmediateOrder():
            return min(self.estimatedSellCount, qty)
        else:
            return qty

    def IsImmediateOrder(self):
        isImmediate = self.GetDuration() == 0
        return isImmediate

    def SetQtyAndPrice(self, newQty, newPrice):
        self.qtyEdit.SetValue(newQty)
        self.priceEdit.SetValue(newPrice)
        self.OnChange()

    def GetSellCountEstimate(self):
        return self.quoteSvc.GetSellCountEstimate(self.typeID, self.stationID, self.GetPrice(), self.GetQty())

    def MakeSingle(self):
        self.height = 80
        self.qtyCont.width = 0
        self.itemCont.width = 0.42
        self.totalCont.width = 0.36
        self.itemNameLabel.fontsize = 14
        self.totalLabel.fontsize = 14
        self.itemNameLabel.left = 72
        self.icon.SetSize(64, 64)
        self.wheel.SetSize(64, 64)
        self.iconInnerCont.SetSize(64, 64)
        self.priceEdit.padLeft = 4
        self.priceEdit.align = uiconst.TOBOTTOM
        self.qtyEdit.top = 20
        self.priceEdit.top = 20
        self.qtyEdit.SetParent(self.priceCont)
        if self.priceAmountWarning:
            self.priceAmountWarning.top = -10

    def RemoveSingle(self):
        self.height = 40
        self.qtyCont.width = 0.15
        self.itemCont.width = 0.33
        self.totalCont.width = 0.3
        self.itemNameLabel.fontsize = 12
        self.totalLabel.fontsize = 12
        self.itemNameLabel.left = 40
        self.icon.SetSize(32, 32)
        self.wheel.SetSize(48, 48)
        self.iconInnerCont.SetSize(32, 32)
        self.priceEdit.align = uiconst.TOTOP
        self.qtyEdit.top = 11
        self.priceEdit.top = 11
        self.priceEdit.padLeft = 8
        self.qtyEdit.SetParent(self.qtyCont)
        if self.priceAmountWarning:
            self.priceAmountWarning.top = 0

    def ConstructPriceAmountWarning(self):
        if self.priceAmountWarning:
            return None
        cont = Container(name='priceAmountWarning', parent=self.itemCont, align=uiconst.TORIGHT, left=-4, width=16, idx=0)
        self.priceAmountWarning = Sprite(parent=cont, pos=(0, 0, 16, 16), align=uiconst.CENTER, texturePath='res:/ui/texture/icons/44_32_7.png')
        self.priceAmountWarning.SetRGB(1.0, 0.3, 0.3, 0.8)
        self.priceAmountWarning.info = (None, None)
        self.priceAmountWarning.GetHint = self.GetWarningHint

    def ConstructQtyBg(self):
        if getattr(self.qtyEdit, 'warningBg', None):
            return
        warningBg = Fill(bgParent=self.qtyEdit, color=(1, 0, 0, 0.3))
        self.qtyEdit.warningBg = warningBg

    def ConstructTotalStrikethroughLine(self):
        if self.totalStrikethroughLine:
            return
        self.totalStrikethroughLine = Line(parent=self.totalCont, align=uiconst.CENTERRIGHT, pos=(2, 0, 0, 1), idx=0, color=(1, 1, 1, 0.8))

    def ChangeTotalStrikethroughDisplay(self, display = False):
        if self.totalStrikethroughLine:
            self.totalStrikethroughLine.display = display

    def ChangePriceAmountWarningDisplay(self, display = False):
        if self.priceAmountWarning:
            self.priceAmountWarning.display = display
        if getattr(self.qtyEdit, 'warningBg', None):
            self.qtyEdit.warningBg.display = display

    def GetWarningHint(self):
        estimatedSellCount, qtyToSell = self.priceAmountWarning.info
        if estimatedSellCount is None or qtyToSell is None:
            return
        txt = GetByLabel('UI/Market/MarketQuote/QtyPriceWarning', estimatedSellNum=int(estimatedSellCount), tryingToSellNum=qtyToSell)
        return txt
