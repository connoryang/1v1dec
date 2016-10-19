#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\hangarCameraController.py
import evecamera
import math
from eve.client.script.ui.camera.baseCameraController import BaseCameraController
from eve.client.script.ui.camera.cameraUtil import CheckInvertZoom, GetPowerOfWithSign
import carbonui.const as uiconst

class HangarCameraController(BaseCameraController):
    cameraID = evecamera.CAM_HANGAR

    def OnMouseMove(self, *args):
        camera = self.GetCamera()
        kOrbit = evecamera.ORBIT_MOVE_DIST
        if uicore.uilib.leftbtn and uicore.uilib.rightbtn:
            kZoom = 0.005
            self._Zoom(-uicore.uilib.dy, kZoom)
            if math.fabs(uicore.uilib.dx) > 1:
                if self.IsCameraRotated():
                    camera.Rotate(0.01 * uicore.uilib.dx, 0.0)
                else:
                    camera.Orbit(0.01 * uicore.uilib.dx, 0.0)
        elif uicore.uilib.leftbtn:
            camera.Orbit(kOrbit * uicore.uilib.dx, kOrbit * uicore.uilib.dy)
        elif uicore.uilib.rightbtn:
            kRotate = 0.005 * camera.fov
            camera.Rotate(kRotate * uicore.uilib.dx, kRotate * uicore.uilib.dy)

    def OnMouseWheel(self, *args):
        k = 0.0005
        self._Zoom(uicore.uilib.dz, k)

    def _Zoom(self, dz, k):
        camera = self.GetCamera()
        dz = CheckInvertZoom(dz)
        dz = GetPowerOfWithSign(dz)
        if uicore.uilib.Key(uiconst.VK_MENU) or self.IsCameraRotated():
            camera.FovZoom(k * dz)
        else:
            camera.Zoom(k * dz)

    def OnGlobalRightMouseUp(self, obj, eventID, (vkey, flag)):
        if vkey != 1:
            return True
        camera = self.GetCamera()
        camera.ResetRotate()
        camera.ResetFOV()

    def OnMouseDown(self, button, *args):
        ret = BaseCameraController.OnMouseDown(self, button, *args)
        if button == 1:
            uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self.OnGlobalRightMouseUp)
        return ret

    def IsCameraRotated(self):
        return uicore.uilib.rightbtn and self.GetCamera().IsRotated()
