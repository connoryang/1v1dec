#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\__init__.py
from eve.client.script.ui.camera.cameraOld import CameraOld
from eve.client.script.ui.camera.capitalHangarCamera import CapitalHangarCamera
from eve.client.script.ui.camera.deathSceneCamera import DeathSceneCamera
from eve.client.script.ui.camera.debugCamera import DebugCamera
from eve.client.script.ui.camera.enterSpaceCamera import EnterSpaceCamera
from eve.client.script.ui.camera.jumpCamera import JumpCamera
from eve.client.script.ui.camera.loginCamera import LoginCamera
from eve.client.script.ui.camera.shipOrbitCamera import ShipOrbitCamera
from eve.client.script.ui.camera.shipPOVCamera import ShipPOVCamera
from eve.client.script.ui.camera.starmapCamera import StarmapCamera
from eve.client.script.ui.camera.systemMapCamera2 import SystemMapCamera2
from eve.client.script.ui.camera.tacticalCamera import TacticalCamera
from eve.client.script.ui.camera.hangarCamera import HangarCamera
from eve.client.script.ui.camera.undockCamera import UndockCamera
import evecamera
cameraClsByCameraID = {evecamera.CAM_SHIPORBIT: ShipOrbitCamera,
 evecamera.CAM_HANGAR: HangarCamera,
 evecamera.CAM_CAPITALHANGAR: CapitalHangarCamera,
 evecamera.CAM_PLANET: CameraOld,
 evecamera.CAM_STARMAP: StarmapCamera,
 evecamera.CAM_SYSTEMMAP: SystemMapCamera2,
 evecamera.CAM_TACTICAL: TacticalCamera,
 evecamera.CAM_SHIPPOV: ShipPOVCamera,
 evecamera.CAM_JUMP: JumpCamera,
 evecamera.CAM_DEBUG: DebugCamera,
 evecamera.CAM_DEATHSCENE: DeathSceneCamera,
 evecamera.CAM_LOGIN: LoginCamera,
 evecamera.CAM_UNDOCK: UndockCamera,
 evecamera.CAM_ENTERSPACE: EnterSpaceCamera}
