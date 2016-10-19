#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\ghostFittingEffectCompiler.py
from eve.client.script.dogma.clientEffectCompiler import ClientEffectCompiler
from eve.client.script.ui.shared.fittingGhost.pythonEffects import Attack, OnlineEffect, Powerboost, Mine, FakeCargoScan, FakePointDefense, FakeTargetHostile, FakeEmpWave, FakeSurveyScan
from eve.common.script.dogma.pythonEffects.bastionMode import BaseBastionMode
from eve.common.script.dogma.pythonEffects.emergencyHullEnergizer import BaseEmergencyHullEnergizer
from eve.common.script.dogma.pythonEffects.microJumpDrive import BaseMicroJumpDrive
from eve.common.script.dogma.pythonEffects.microJumpPortalDrive import BaseMicroJumpPortalDrive
from eve.common.script.dogma.pythonEffects.propulsionModules import Afterburner, Microwarpdrive
from eve.common.script.dogma.pythonEffects.warpDisruptSphere import BaseWarpDisruptSphere
import telemetry

class GhostFittingEffectCompiler(ClientEffectCompiler):
    __guid__ = 'svc.ghostFittingEffectCompiler'

    def GetDogmaStaticMgr(self):
        return sm.GetService('clientDogmaStaticSvc')

    def GetPythonForOperand(self, operand, arg1, arg2, val):
        if 'env' not in self.evalDict:

            class Env:

                def __getattr__(self, attrName):
                    return 'env.%s' % attrName

            self.evalDict['env'] = Env()

    @telemetry.ZONE_METHOD
    def SetupEffects(self):
        ClientEffectCompiler.SetupEffects(self)
        self.SetupPythonEffects(PYTHON_EFFECTS)

    @telemetry.ZONE_METHOD
    def SetupDogmaEffects(self):
        return self.CopyEffects()

    @telemetry.ZONE_METHOD
    def CopyEffects(self):
        clientEffectCompiler = sm.GetService('clientEffectCompiler')
        for effectID, effect in clientEffectCompiler.effects.iteritems():
            self.effects[effectID] = effect


PYTHON_EFFECTS = [Attack,
 OnlineEffect,
 Powerboost,
 Mine,
 BaseMicroJumpDrive,
 BaseMicroJumpPortalDrive,
 BaseWarpDisruptSphere,
 BaseEmergencyHullEnergizer,
 BaseBastionMode,
 Afterburner,
 Microwarpdrive,
 FakeCargoScan,
 FakePointDefense,
 FakeTargetHostile,
 FakeEmpWave,
 FakeSurveyScan]
