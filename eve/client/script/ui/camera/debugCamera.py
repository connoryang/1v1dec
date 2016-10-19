#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\debugCamera.py
from eve.client.script.ui.camera.tacticalCamera import TacticalCamera
import evecamera
DEFAULT_EYEDIST = 40000
FREE_ORBIT_DIST = 250
LOOKAT_DIST = 50000

class DebugCamera(TacticalCamera):
    name = 'DebugCamera'
    cameraID = evecamera.CAM_DEBUG
    minFov = 0.01
    maxFov = 1.0
    default_fov = 1.0

    def LookAt(self, itemID, *args, **kwargs):
        TacticalCamera.LookAt(self, itemID, *args, **kwargs)
        self.SetFovTarget(self.default_fov)
