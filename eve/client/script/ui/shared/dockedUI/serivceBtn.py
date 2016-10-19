#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\dockedUI\serivceBtn.py
from eve.client.script.ui.control.buttons import BigButton
from localization import GetByLabel

class StationServiceBtn(BigButton):

    def ApplyAttributes(self, attributes):
        BigButton.ApplyAttributes(self, attributes)
        self.Startup(self.width, self.height, iconOpacity=0.75)
        serviceInfo = attributes.serviceInfo
        self.cmdStr = serviceInfo.command
        self.maskStationServiceIDs = serviceInfo.maskServiceIDs
        self.serviceID = serviceInfo.serviceID
        self.serviceStatus = attributes.serviceStatus
        self.serviceEnabled = True
        self.displayName = serviceInfo.label
        self.callback = attributes.callback
        if hasattr(serviceInfo, 'iconID'):
            self.SetTexturePath(serviceInfo.iconID)
        else:
            self.SetTexturePath(serviceInfo.texturePath)

    def OnClick(self, *args):
        BigButton.OnClick(self, *args)
        if self.callback:
            self.callback(self)

    def EnableBtn(self):
        self.Enable()
        self.serviceStatus = GetByLabel('UI/Station/Lobby/Enabled')
        self.serviceEnabled = True

    def DisableBtn(self):
        self.Disable()
        self.serviceStatus = GetByLabel('UI/Station/Lobby/Disabled')
        self.serviceEnabled = False
