#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\neocom\neocom\neocomWalletUpdater.py
from eve.client.script.ui.control.tooltips import TooltipPersistentPanel, COLOR_NUMBERVALUE_POSITIVE, COLOR_NUMBERVALUE_NEGATIVE, COLOR_NUMBERVALUE
import uthread
import blue
import eve.client.script.ui.control.pointerPanel as pointerPanel
import util
import localization

class WalletUpdater(object):

    def __init__(self, startBalance = 50000, transaction = 1500, finishedCallBack = None):
        self.startBalance = startBalance * 1.0
        self.transaction = transaction * 1.0
        self.balanceValueLabel = None
        self.initialDelay = 1000
        self.showTime = 5000
        self.showFractions = False
        self.tooltipPanel = None
        self.finishedCallback = finishedCallBack

    def _FindWalletButton(self, neocom):
        for button in neocom.buttonCont.children:
            if button.name is 'wallet':
                return button

    def ShowBalanceChange(self, neocom):
        button = self._FindWalletButton(neocom)
        if button:
            parent = uicore.layer.menu
            self.tooltipPanel = TooltipPersistentPanel(parent=parent, owner=button, idx=0, width=220)
            self._LoadTooltipPanel(self.tooltipPanel)
            uthread.new(self._AnimationChain)

    def _AnimationChain(self):
        uicore.animations.FadeIn(self.tooltipPanel, duration=0.2)
        uicore.animations.FadeTo(self.transactionValueLabel, duration=0.2)
        uicore.animations.MoveInFromRight(self.transactionValueLabel)
        uthread.new(self._AnimateTransaction)
        uthread.new(self._WaitAndClose)

    def _LoadTooltipPanel(self, tooltipPanel):
        showFractions = self.showFractions
        tooltipPanel.LoadGeneric2ColumnTemplate()
        l, v = tooltipPanel.AddLabelValue(label=self._GetTransactionLabel(self.transaction), value='%s' % self._GetPrefix(self.transaction) + util.FmtISK(self.transaction, showFractionsAlways=showFractions), valueColor=self._GetValueColor(self.transaction))
        self.transactionValueLabel = v
        spacer = tooltipPanel.AddSpacer(width=180, height=1, colSpan=2, rowSpan=1)
        spacer.color = (0.5, 0.5, 0.5, 1.0)
        label, value = tooltipPanel.AddLabelValue(label=localization.GetByLabel('Tooltips/Neocom/Balance'), value=util.FmtISK(self.startBalance, showFractionsAlways=showFractions), valueColor=COLOR_NUMBERVALUE)
        self.balanceValueLabel = value
        self.spacer = spacer

    def _AnimateTransaction(self):
        blue.synchro.Sleep(self.initialDelay)
        difference = self.transaction
        totalIterations = 20
        for i in range(totalIterations):
            increment = (i + 1) / (1.0 * totalIterations)
            value = self.startBalance + difference * increment
            self.balanceValueLabel.SetText(util.FmtISK(value, showFractionsAlways=self.showFractions))
            blue.synchro.Sleep(25)

    def _WaitAndClose(self):
        blue.synchro.Sleep(self.showTime)
        pointerPanel.FadeOutPanelAndClose(self.tooltipPanel)
        if self.finishedCallback:
            self.finishedCallback()

    def _GetValueColor(self, value):
        if value > 0:
            return COLOR_NUMBERVALUE_POSITIVE
        else:
            return COLOR_NUMBERVALUE_NEGATIVE

    def _GetPrefix(self, value):
        if value > 0:
            return '+'
        else:
            return ''

    def _GetTransactionLabel(self, value):
        if value > 0:
            return localization.GetByLabel('Tooltips/Neocom/WalletCredit')
        else:
            return localization.GetByLabel('Tooltips/Neocom/WalletDebit')
