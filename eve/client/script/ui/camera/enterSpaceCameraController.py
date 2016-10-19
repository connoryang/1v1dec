#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\enterSpaceCameraController.py
from eve.client.script.ui.camera.baseCameraController import BaseCameraController
import evecamera

class EnterSpaceCameraController(BaseCameraController):
    cameraID = evecamera.CAM_ENTERSPACE

    def OnMouseUp(self, *args):
        self.SwitchToPrimaryCamera()

    def OnMouseMove(self, *args):
        if uicore.uilib.leftbtn:
            self.SwitchToPrimaryCamera()

    def OnMouseWheel(self, *args):
        self.SwitchToPrimaryCamera()

    def SwitchToPrimaryCamera(self):
        self.GetCamera().SwitchToPrimaryCamera()
