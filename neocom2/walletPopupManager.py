#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\neocom2\walletPopupManager.py


class WalletPopupManager(object):

    def __init__(self, settingsContainer, neocom, uiClass, compressionEnabled = True):
        self.isShowingWalletPopup = False
        self.waitingTransactionMessages = []
        self.settingsContainer = settingsContainer
        self.uiClass = uiClass
        self.neocom = neocom
        self.usingCompression = compressionEnabled

    def TurnOnCompression(self):
        self.usingCompression = True

    def OnPersonalAccountChangedClient(self, originalBalance, transaction):
        threshold = self.settingsContainer.Get('iskNotifyThreshold', 0)
        enabled = self.settingsContainer.Get('walletShowBalanceUpdates', True)
        if enabled and abs(transaction) >= threshold:
            self.waitingTransactionMessages.append((originalBalance, transaction))

    def ShowWalletPopup(self, originalBalance, transaction):
        self.isShowingWalletPopup = True
        self.ShowTheActualThing(originalBalance, transaction)

    def ShowTheActualThing(self, originalbalance, transaction):
        updater = self.uiClass(startBalance=originalbalance, transaction=transaction, finishedCallBack=self.OnWalletFinished)
        updater.ShowBalanceChange(self.neocom)

    def OnWalletFinished(self):
        self.isShowingWalletPopup = False
        self.ProcessWaitingTransactions()

    def ProcessWaitingTransactions(self):
        if not self.isShowingWalletPopup and len(self.waitingTransactionMessages) > 0:
            if self.usingCompression:
                balance, transaction = self.waitingTransactionMessages[0]
                totalTransaction = sum((pair[1] for pair in self.waitingTransactionMessages))
                self.waitingTransactionMessages = []
                self.ShowWalletPopup(balance, totalTransaction)
            else:
                balance, transaction = self.waitingTransactionMessages.pop(0)
                self.ShowWalletPopup(balance, transaction)
