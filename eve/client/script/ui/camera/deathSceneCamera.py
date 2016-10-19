#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\deathSceneCamera.py
from eve.client.script.ui.camera.baseSpaceCamera import BaseSpaceCamera
import blue
import geo2
import evecamera

class DeathSceneCamera(BaseSpaceCamera):
    cameraID = evecamera.CAM_DEATHSCENE
    name = 'DeathSceneCamera'

    def OnActivated(self, **kwargs):
        BaseSpaceCamera.OnActivated(self, **kwargs)
        duration = max(blue.os.desiredSimDilation, 0.2) * 1.75
        self._eyePosition = geo2.Vec3Scale(self.GetLookAtDirection(), -30.0)
        eyePos1 = geo2.Vec3Scale(self.GetLookAtDirection(), 8.0)
        uicore.animations.MorphVector3(self, '_eyePosition', self._eyePosition, eyePos1, duration=duration)
        uicore.animations.MorphScalar(self, 'fov', startVal=self.fov, endVal=0.55, duration=duration)
