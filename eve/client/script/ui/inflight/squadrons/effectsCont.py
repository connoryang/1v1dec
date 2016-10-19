#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\squadrons\effectsCont.py
import carbonui.const as uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.inflight.shipHud.ewarContainer import HINTS
from eve.client.script.ui.inflight.squadrons.shipFighterState import GetShipFighterState
import evetypes
from localization import GetByLabel
from localization.util import Sort

class EffectsCont(ContainerAutoSize):
    default_width = 20
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_PICKCHILDREN
    MAXNUMBERINHINT = 6

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        self.fighterID = attributes.fighterID
        self.tubeFlagID = attributes.tubeFlagID
        self.effectsOnFighter = None
        self.shipFighterState = GetShipFighterState()
        self.ewarIcons = {}
        self.controller = attributes.controller
        self.BuildEffectsData()

    def BuildEffectsData(self):
        effectsOnFighter = self.controller.GetIncomingEwarEffects(self.fighterID)
        graphicIDs = []
        stateSvc = sm.GetService('state')
        for effect in effectsOnFighter:
            sourceModuleID, sourceShipID, jammingType = effect
            graphicID = stateSvc.GetEwarGraphicID(jammingType)
            graphicIDs.append((graphicID, jammingType))

        self.AddEffects(graphicIDs)

    def AddEffects(self, graphicIDs):
        for graphicID, icon in self.ewarIcons.iteritems():
            if not graphicIDs or graphicID not in graphicIDs:
                icon.display = False

        if graphicIDs:
            for graphicID, jammingType in graphicIDs:
                if graphicID in self.ewarIcons:
                    icon = self.ewarIcons[graphicID]
                    icon.display = True
                else:
                    icon = self.MakeIcon(graphicID)
                    self.ewarIcons[graphicID] = icon
                icon.hint = self.GetIconHint(jammingType)
                icon.GetMenu = (self.GetIconMenu, jammingType)

    def MakeIcon(self, graphicID):
        return Icon(parent=self, align=uiconst.TOBOTTOM, state=uiconst.UI_NORMAL, width=20, height=20, graphicID=graphicID, ignoreSize=True)

    def GetIconMenu(self, jammingType, *args):
        attackers = self.FindWhoIsJammingMe(jammingType)
        m = []
        svc = sm.StartService('michelle')
        menuSvc = sm.StartService('menu')
        for shipID, num in attackers.iteritems():
            invItem = svc.GetBallpark().GetInvItem(shipID)
            if invItem:
                if invItem.charID:
                    attackerName = cfg.eveowners.Get(invItem.charID).name
                else:
                    attackerName = evetypes.GetName(invItem.typeID)
                m += [[attackerName, ('isDynamic', menuSvc.CelestialMenu, (invItem.itemID,
                    None,
                    invItem,
                    0,
                    invItem.typeID))]]

        m = Sort(m, key=lambda x: x[0])
        return m

    def HideEffects(self):
        self.display = False

    def ShowEffects(self):
        self.display = True

    def UpdateFighterID(self, fighterID):
        self.fighterID = fighterID
        self.BuildEffectsData()

    def GetIconHint(self, jammingType):
        hintList = self.GetEwarHintList(jammingType)
        hint = '<br>'.join(hintList)
        return hint

    def GetEwarHintList(self, jammingType):
        attackers = self.FindWhoIsJammingMe(jammingType)
        hintList = []
        extraAttackers = 0
        for shipID, num in attackers.iteritems():
            if len(hintList) >= self.MAXNUMBERINHINT:
                extraAttackers = len(attackers) - len(hintList)
                break
            self.AddEwarAttackerText(hintList, shipID, num)

        hintList = Sort(hintList)
        self.AddExtraAttackers(hintList, extraAttackers)
        ewarHint = self.GetEwarHintCaption(jammingType)
        hintList.insert(0, ewarHint)
        return hintList

    def GetEwarHintCaption(self, jammingType):
        ewarHintPath = HINTS.get(jammingType, None)
        if ewarHintPath is not None:
            ewarHint = GetByLabel(ewarHintPath)
        else:
            ewarHint = ''
        return ewarHint

    def AddEwarAttackerText(self, hintList, sourceID, numModules):
        invItem = sm.GetService('michelle').GetBallpark().GetInvItem(sourceID)
        if invItem:
            attackerShipTypeID = invItem.typeID
            if invItem.charID:
                attackerID = invItem.charID
                hintList.append(GetByLabel('UI/Inflight/EwarAttacker', attackerID=attackerID, attackerShipID=attackerShipTypeID, num=numModules))
            else:
                hintList.append(GetByLabel('UI/Inflight/EwarAttackerNPC', attackerShipID=attackerShipTypeID, num=numModules))

    def AddExtraAttackers(self, hintList, extraAttackers):
        if extraAttackers > 0:
            hintList.append(GetByLabel('UI/Inflight/AndMorewarAttackers', num=extraAttackers))

    def FindWhoIsJammingMe(self, jammingType):
        effectsOnFighter = self.controller.GetIncomingEwarEffects(self.fighterID)
        attackers = {}
        for effect in effectsOnFighter:
            sourceModuleID, sourceShipID, _jammingType = effect
            if jammingType != _jammingType:
                continue
            numberOfTimes = attackers.get(sourceShipID, 0)
            numberOfTimes += 1
            attackers[sourceShipID] = numberOfTimes

        return attackers
