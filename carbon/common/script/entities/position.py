#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\entities\position.py
import carbon.common.script.cef.componentViews.positionComponent as positionComponent
import collections
import geo2
import service
import GameWorld
import sys
STATE_CREATED = 0
STATE_UNREGISTERED = -1
STATE_REGISTERED = 1

class PositionService(service.Service):
    __guid__ = 'svc.position'
    __componentTypes__ = [positionComponent.PositionComponentView.GetComponentCodeName()]

    def CreateComponent(self, name, state):
        c = GameWorld.PositionComponent()
        try:
            c.position = state['position']
        except KeyError:
            sys.exc_clear()

        try:
            r = state['rotation']
            if len(r) == 3:
                r = geo2.QuaternionRotationSetYawPitchRoll(*r)
            c.rotation = r
        except KeyError:
            sys.exc_clear()

        return c

    def PrepareComponent(self, sceneID, entityID, component):
        self.entityService.entitySceneManager.PrepareComponent(entityID, sceneID, component)

    def SetupComponent(self, entity, component):
        pass

    def RegisterComponent(self, entity, component):
        component.state = STATE_REGISTERED

    def UnRegisterComponent(self, entity, component):
        component.state = STATE_UNREGISTERED

    def PackUpForClientTransfer(self, component):
        state = {}
        state['position'] = component.position
        state['rotation'] = component.rotation
        return state

    def PackUpForSceneTransfer(self, component, destinationSceneID = None):
        return self.PackUpForClientTransfer(component)

    def UnPackFromSceneTransfer(self, component, entity, state):
        component.position = state['position']
        component.rotation = state['rotation']
        return component

    def ReportState(self, component, entity):
        state = collections.OrderedDict()
        state['position'] = ', '.join([ '%.3f' % f for f in component.position ])
        state['rotation'] = component.rotation
        return state
