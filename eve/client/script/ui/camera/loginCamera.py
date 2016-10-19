#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\loginCamera.py
from eve.client.script.ui.camera.baseCamera import Camera
import evecamera

class LoginCamera(Camera):
    name = 'LoginCamera'
    cameraID = evecamera.CAM_LOGIN
    default_fov = 0.8
    default_eyePosition = (0.0, 0.0, 22.0)
