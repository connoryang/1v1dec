#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\station\pvptrade\pvptradesvc.py
import service
import form
import uicontrols

class PVPTradeService(service.Service):
    __guid__ = 'svc.pvptrade'
    __notifyevents__ = ['OnTradeInitiate',
     'OnTradeCancel',
     'OnTradeStateToggle',
     'OnTradeMoneyOffer',
     'OnTradeComplete']

    def _ShowTradeSessionWindow(self, tradeSession, charID, tradeItems):
        windowID = self.GetWindowIDForTradeSession(tradeSession)
        checkWnd = uicontrols.Window.GetIfOpen(windowID=windowID)
        if checkWnd and not checkWnd.destroyed:
            checkWnd.Maximize()
        else:
            self.OnTradeInitiate(charID, tradeSession, tradeItems)

    def StartTradeSession(self, charID, tradeItems = None):
        tradeSession = sm.RemoteSvc('trademgr').InitiateTrade(charID)
        self._ShowTradeSessionWindow(tradeSession, charID, tradeItems)

    def GetWindowIDForTradeSession(self, tradeSession):
        tradeContainerID = tradeSession.List().tradeContainerID
        return self.GetWindowID(tradeContainerID)

    def GetWindowID(self, tradeContainerID = None):
        windowID = ('tradeWnd', tradeContainerID)
        return windowID

    def OnTradeInitiate(self, charID, tradeSession, tradeItems = None):
        self.LogInfo('OnInitiate', charID, tradeSession)
        windowID = self.GetWindowIDForTradeSession(tradeSession)
        checkWnd = uicontrols.Window.GetIfOpen(windowID=windowID)
        if checkWnd:
            return
        form.PVPTrade.Open(windowID=windowID, tradeSession=tradeSession, tradeItems=tradeItems)

    def OnTradeCancel(self, containerID):
        windowID = self.GetWindowID(containerID)
        w = uicontrols.Window.GetIfOpen(windowID=windowID)
        if w:
            w.OnCancel()

    def OnTradeStateToggle(self, containerID, state):
        windowID = self.GetWindowID(containerID)
        w = uicontrols.Window.GetIfOpen(windowID=windowID)
        if w:
            w.OnStateToggle(state)

    def OnTradeMoneyOffer(self, containerID, money):
        windowID = self.GetWindowID(containerID)
        w = uicontrols.Window.GetIfOpen(windowID=windowID)
        if w:
            w.OnMoneyOffer(money)

    def OnTradeComplete(self, containerID):
        windowID = self.GetWindowID(containerID)
        w = uicontrols.Window.GetIfOpen(windowID=windowID)
        if w:
            w.OnTradeComplete()
