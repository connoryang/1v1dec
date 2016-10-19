#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\parklife\turret.py
import service
import states as state
import blue

class TurretSvc(service.Service):
    __exportedcalls__ = {}
    __notifyevents__ = ['OnStateChange',
     'ProcessTargetChanged',
     'OnGodmaItemChange',
     'ProcessShipEffect',
     'ProcessActiveShipChanged',
     'OnChargeBeingLoadedToModule']
    __dependencies__ = []
    __guid__ = 'svc.turret'
    __servicename__ = 'turret'
    __displayname__ = 'Turret Service'

    def Run(self, memStream = None):
        self.LogInfo('Starting Turret Service')

    def Startup(self):
        pass

    def Stop(self, memStream = None):
        pass

    def OnStateChange(self, itemID, flag, *args):
        if flag == state.targeting:
            pass
        if flag != state.activeTarget:
            return
        ship = sm.GetService('michelle').GetBall(eve.session.shipid)
        rest = len(sm.GetService('target').GetTargets()) == 0
        for turretSet in getattr(ship, 'turrets', []):
            if rest:
                turretSet.Rest()
            elif not turretSet.IsShooting():
                turretSet.SetTarget(eve.session.shipid, itemID)
                turretSet.TakeAim(itemID)

    def OnGodmaItemChange(self, item, change):
        ball = sm.GetService('michelle').GetBall(eve.session.shipid)
        if ball is None:
            return
        targetSvc = sm.GetService('target')
        if targetSvc is None:
            return
        if item.groupID in const.turretModuleGroups:
            ball.UnfitHardpoints()
            ball.FitHardpoints()
            targets = targetSvc.GetTargets()
            if len(targets) > 0:
                for turretSet in ball.turrets:
                    turretSet.SetTargetsAvailable(True)
                    turretSet.SetTarget(None, targetSvc.GetActiveTargetID())

    def ProcessTargetChanged(self, what, tid, reason):
        ship = sm.GetService('michelle').GetBall(eve.session.shipid)
        if ship is None:
            return
        if not hasattr(ship, 'turrets'):
            return
        blue.synchro.Yield()
        targets = sm.GetService('target').GetTargets()
        for turretSet in ship.turrets:
            turretSet.SetTargetsAvailable(len(targets) != 0)

    def ProcessShipEffect(self, godmaStm, effectState):
        if effectState.effectName == 'online':
            ship = sm.GetService('michelle').GetBall(eve.session.shipid)
            if ship is not None:
                turret = None
                for moduleID in getattr(ship, 'modules', []):
                    if moduleID == effectState.itemID:
                        turret = ship.modules[moduleID]

                if turret is not None:
                    if effectState.active:
                        turret.Online()
                    else:
                        turret.Offline()

    def ProcessActiveShipChanged(self, shipID, oldShipID):
        bp = sm.GetService('michelle').GetBallpark()
        if bp:
            try:
                ship = bp.balls[shipID]
            except KeyError:
                return

            try:
                ship.UnfitHardpoints()
                ship.FitHardpoints()
            except AttributeError:
                self.LogInfo("Ship didn't have attribute fitted. Probably still being initialized", shipID)

    def OnChargeBeingLoadedToModule(self, moduleIDs, chargeTypeID, reloadTime):
        ship = sm.GetService('michelle').GetBall(eve.session.shipid)
        if ship is not None:
            for launcherID in moduleIDs:
                if launcherID in ship.modules:
                    turret = ship.modules[launcherID]
                    if turret is not None:
                        turret.Reload()
