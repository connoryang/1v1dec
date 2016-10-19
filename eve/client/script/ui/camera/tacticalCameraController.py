#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\tacticalCameraController.py
import math
from eve.client.script.ui.camera.cameraUtil import SetShipDirection, GetZoomDz, CheckInvertZoom, GetPanVectorForZoomToCursor
from eve.client.script.ui.camera.baseCameraController import BaseCameraController
import evecamera
import carbonui.const as uiconst
DIST_ORBIT_SWITCH = 20000

class TacticalCameraController(BaseCameraController):
    cameraID = evecamera.CAM_TACTICAL

    def OnMouseMove(self, *args):
        camera = self.GetCamera()
        if uicore.uilib.leftbtn and uicore.uilib.rightbtn:
            if camera.IsAttached() and math.fabs(uicore.uilib.dx) > 1:
                camera.Orbit(0.01 * uicore.uilib.dx, 0.0)
            dz = CheckInvertZoom(uicore.uilib.dy)
            self._Zoom(dz, -0.005, zoomToCursor=False)
        elif uicore.uilib.rightbtn:
            k = 3.0
            camera.Pan(-k * uicore.uilib.dx, k * uicore.uilib.dy, 0)
        elif uicore.uilib.leftbtn:
            k = evecamera.ORBIT_MOVE_DIST if camera.IsAttached() else 0.006
            camera.Orbit(k * uicore.uilib.dx, k * uicore.uilib.dy)

    def OnMouseWheel(self, *args):
        camera = self.GetCamera()
        dz = GetZoomDz()
        k = 0.0005
        self._Zoom(dz, k, zoomToCursor=True)

    def OnDblClick(self, *args):
        if uicore.uilib.rightbtn or uicore.uilib.mouseTravel > 6:
            return
        SetShipDirection(self.GetCamera())

    def _Zoom(self, dz, k, zoomToCursor):
        self.RecordZoomForAchievements(dz)
        camera = self.GetCamera()
        if uicore.uilib.Key(uiconst.VK_MENU):
            camera.FovZoom(k * dz)
        elif camera.IsAttached() or camera.IsTracking():
            camera.Zoom(k * dz)
        elif zoomToCursor:
            x, y, z = GetPanVectorForZoomToCursor(camera.fov)
            k = 1.5 * dz
            camera.Pan(k * x, k * y, k * z)
        else:
            k = 20.0
            camera.Pan(0, 0, -k * dz)
