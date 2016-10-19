#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\squadrons\fighterInvCont.py
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.inflight.squadrons.shipFighterState import GetShipFighterState
from eve.client.script.ui.inflight.squadrons.squadronManagementCont import FighterLaunchControlCont
from fighters.client import GetFighterTubesForShip, GetLightSupportHeavySlotsForShip, SquadronIsLight, SquadronIsHeavy, SquadronIsSupport
import invCont
import carbonui.const as uiconst
from localization import GetByLabel
USED_SLOT = 'res:/UI/Texture/classes/CarrierBay/typeSlotFilled.png'
UNUSED_SLOT = 'res:/UI/Texture/classes/CarrierBay/typeSlotEmpty.png'

class FighterInvCont(invCont._InvContBase):
    __guid__ = 'invCont.FighterInvCont'
    __invControllerClass__ = None
    __notifyevents__ = invCont._InvContBase.__notifyevents__ + ['ProcessActiveShipChanged']

    def ApplyAttributes(self, attributes):
        self.squadrons = []
        invCont._InvContBase.ApplyAttributes(self, attributes)

    def ConstructUI(self):
        if self.IsCurrentShip():
            self.ConstructFighterManagementUI()
        invCont._InvContBase.ConstructUI(self)

    def ConstructFighterManagementUI(self):
        self.shipFighterState = GetShipFighterState()
        topCont = Container(parent=self, align=uiconst.TOTOP, height=216)
        inSpace = Container(parent=topCont, align=uiconst.TOTOP, height=20)
        self.lightSquadrons = SquadronLightContainer(parent=inSpace)
        self.supportSquadrons = SquadronSupportContainer(parent=inSpace)
        self.heavySquadrons = SquadronHeavyContainer(parent=inSpace)
        self.squadronsCont = Container(parent=topCont, align=uiconst.TOALL)
        self.numOfTubes = GetFighterTubesForShip()
        self.ConstructSquadrons()
        self.ConstructSquadronTypes()
        self.UpdateSquadronTypes()
        self.GetTypeIDs()
        self.shipFighterState.signalOnFighterTubeStateUpdate.connect(self.OnFighterTubeStateUpdate)

    def _OnClose(self, *args):
        if self.IsCurrentShip():
            self.shipFighterState.signalOnFighterTubeStateUpdate.disconnect(self.OnFighterTubeStateUpdate)
        invCont._InvContBase._OnClose(self, args)

    def IsCurrentShip(self):
        return self.itemID == session.shipid

    def ConstructSquadrons(self):
        for i, tubeFlagID in enumerate(const.fighterTubeFlags):
            if i < self.numOfTubes:
                squadron = FighterLaunchControlCont(parent=self.squadronsCont, tubeFlagID=tubeFlagID, left=2)
                self.squadrons.append(squadron)

    def ConstructSquadronTypes(self):
        light, support, heavy = GetLightSupportHeavySlotsForShip()
        if heavy:
            self.heavySquadrons.SetTotalSlots(heavy)
        else:
            self.heavySquadrons.display = False
        if support:
            self.supportSquadrons.SetTotalSlots(support)
        else:
            self.supportSquadrons.display = False
        if light:
            self.lightSquadrons.SetTotalSlots(light)
        else:
            self.lightSquadrons.display = False

    def OnFighterTubeStateUpdate(self, *args):
        self.UpdateSquadronTypes()

    def UpdateSquadronTypes(self):
        heavy, support, light = self.GetSquadronTypes()
        self.heavySquadrons.SetUsedSlots(heavy)
        self.supportSquadrons.SetUsedSlots(support)
        self.lightSquadrons.SetUsedSlots(light)

    def GetSquadronTypes(self):
        heavy = 0
        support = 0
        light = 0
        typeIDs = self.GetTypeIDs()
        for typeID in typeIDs:
            if SquadronIsHeavy(typeID):
                heavy += 1
            elif SquadronIsSupport(typeID):
                support += 1
            elif SquadronIsLight(typeID):
                light += 1

        return (heavy, support, light)

    def GetTypeIDs(self):
        squadronTypeIDs = []
        for i, tubeFlagID in enumerate(const.fighterTubeFlags):
            if i < self.numOfTubes:
                fighterInTube = self.shipFighterState.GetFightersInTube(tubeFlagID)
                if fighterInTube is not None:
                    squadronTypeIDs.append(fighterInTube.typeID)
                fighterInSpace = self.shipFighterState.GetFightersInSpace(tubeFlagID)
                if fighterInSpace is not None:
                    squadronTypeIDs.append(fighterInSpace.typeID)

        return squadronTypeIDs

    def ProcessActiveShipChanged(self, shipID, oldShipID):
        self.Flush()
        self.ConstructUI()


class SquadronTypeContainer(ContainerAutoSize):
    default_texturePath = None
    default_padTop = 2
    default_padBottom = 2
    default_padRight = 6
    default_align = uiconst.TOLEFT
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        self.totalSlots = 0
        Sprite(parent=self, width=16, height=16, texturePath=self.default_texturePath, align=uiconst.TOLEFT, state=uiconst.UI_DISABLED)
        self.slotsUsedText = EveLabelSmall(parent=self, align=uiconst.TOLEFT)

    def SetTotalSlots(self, numSlots):
        self.totalSlots = numSlots

    def SetUsedSlots(self, numUsed):
        self.slotsUsedText.text = ':%i/%i' % (int(numUsed), int(self.totalSlots))


class SquadronHeavyContainer(SquadronTypeContainer):
    default_texturePath = 'res:/UI/Texture/classes/CarrierBay/iconFighterHeavy.png'
    default_hint = GetByLabel('UI/Fighters/Class/Heavy')


class SquadronSupportContainer(SquadronTypeContainer):
    default_texturePath = 'res:/UI/Texture/classes/CarrierBay/iconFighterMedium.png'
    default_hint = GetByLabel('UI/Fighters/Class/Support')


class SquadronLightContainer(SquadronTypeContainer):
    default_texturePath = 'res:/UI/Texture/classes/CarrierBay/iconFighterLight.png'
    default_hint = GetByLabel('UI/Fighters/Class/Light')
