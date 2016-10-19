#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\debugCameraController.py
import math
from eve.client.script.ui.camera.cameraUtil import SetShipDirection, GetZoomDz, GetPanVectorForZoomToCursor, CheckInvertZoom
from eve.client.script.ui.camera.baseCameraController import BaseCameraController
import evecamera
import carbonui.const as uiconst

class DebugCameraController(BaseCameraController):
    cameraID = evecamera.CAM_DEBUG

    def OnMouseMove(self, *args):
        camera = self.GetCamera()
        if uicore.uilib.leftbtn and uicore.uilib.rightbtn:
            k = 20.0
            if camera.IsAttached():
                camera.Zoom(-0.005 * uicore.uilib.dy)
                if math.fabs(uicore.uilib.dx) > 1:
                    camera.Orbit(0.01 * uicore.uilib.dx, 0.0)
            else:
                camera.Pan(0, 0, -k * CheckInvertZoom(uicore.uilib.dy))
        elif uicore.uilib.rightbtn:
            k = 3.0
            camera.Pan(-k * uicore.uilib.dx, k * uicore.uilib.dy, 0)
        elif uicore.uilib.leftbtn:
            k = evecamera.ORBIT_MOVE_DIST
            camera.Orbit(k * uicore.uilib.dx, k * uicore.uilib.dy)

    def OnMouseWheel(self, *args):
        k = 0.0005
        dz = GetZoomDz()
        self._Zoom(dz, k)

    def _Zoom(self, dz, k):
        camera = self.GetCamera()
        dz = GetZoomDz()
        if uicore.uilib.Key(uiconst.VK_MENU):
            camera.FovZoom(k * dz)
        elif camera.IsAttached():
            k = 0.0005
            camera.Zoom(k * dz)
        else:
            k = 1.0 * dz
            x, y, z = GetPanVectorForZoomToCursor(camera.fov)
            camera.Pan(k * x, k * y, k * z)
