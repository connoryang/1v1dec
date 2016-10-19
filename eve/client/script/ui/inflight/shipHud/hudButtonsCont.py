#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\shipHud\hudButtonsCont.py
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.inflight.shipHud.leftSideButton import LeftSideButtonScanner, LeftSideButtonTactical, LeftSideButtonAutopilot, LeftSideButtonZoomIn, LeftSideButtonZoomOut, LeftSideButtonCameraOrbit, LeftSideButtonCameraTactical, LeftSideButtonCameraPOV, LeftSideButtonStructureAmmoHold
from eve.client.script.ui.inflight.shipHud.leftSideButtons.leftSideButtonCargo import LeftSideButtonCargo
import telemetry
from eve.common.script.sys.eveCfg import IsControllingStructure
COL1 = 0
COL2 = 28
COL3 = 56
HEIGHT = 16

class HudButtonsCont(ContainerAutoSize):
    default_name = 'HudButtonsCont'
    isAutoSizeEnabled = False

    @telemetry.ZONE_METHOD
    def InitButtons(self):
        self.Flush()
        LeftSideButtonCameraTactical(parent=self, left=COL1, top=HEIGHT)
        LeftSideButtonCameraOrbit(parent=self, left=COL1, top=3 * HEIGHT)
        LeftSideButtonCameraPOV(parent=self, left=COL1, top=5 * HEIGHT)
        self.AddCargoBtn(COL2)
        LeftSideButtonTactical(parent=self, left=COL2, top=2 * HEIGHT)
        LeftSideButtonScanner(parent=self, left=COL2, top=4 * HEIGHT)
        self.autopilotBtn = LeftSideButtonAutopilot(parent=self, left=COL2, top=6 * HEIGHT)
        showZoomBtns = settings.user.ui.Get('showZoomBtns', 0)
        if showZoomBtns:
            LeftSideButtonZoomIn(parent=self, left=COL3, top=HEIGHT)
            LeftSideButtonZoomOut(parent=self, left=COL3, top=3 * HEIGHT)
        if IsControllingStructure():
            self.autopilotBtn.Disable()
        else:
            self.autopilotBtn.Enable()
        self.EnableAutoSize()
        self.DisableAutoSize()

    def AddCargoBtn(self, left):
        if IsControllingStructure():
            cargoClass = LeftSideButtonStructureAmmoHold
        else:
            cargoClass = LeftSideButtonCargo
        cargoClass(parent=self, left=left, top=0)
