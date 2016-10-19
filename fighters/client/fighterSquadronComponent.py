#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\fighters\client\fighterSquadronComponent.py
import logging
from fighters.client import GetSquadronSizeFromSlimItem
from spacecomponents.client.messages import MSG_ON_SLIM_ITEM_UPDATED, MSG_ON_ADDED_TO_SPACE, MSG_ON_TARGET_BRACKET_ADDED, MSG_ON_TARGET_BRACKET_REMOVED
from spacecomponents.common.components.component import Component
logger = logging.getLogger(__name__)

class FighterSquadronComponent(Component):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        super(FighterSquadronComponent, self).__init__(itemID, typeID, attributes, componentRegistry)
        self.SubscribeToMessage(MSG_ON_ADDED_TO_SPACE, self.OnAddedToSpace)
        self.SubscribeToMessage(MSG_ON_SLIM_ITEM_UPDATED, self.OnSlimItemUpdated)
        self.SubscribeToMessage(MSG_ON_TARGET_BRACKET_ADDED, self.OnTargetBracketAdded)
        self.SubscribeToMessage(MSG_ON_TARGET_BRACKET_REMOVED, self.OnTargetBracketRemoved)
        self.targetBracket = None
        self.squadronSize = None

    def OnAddedToSpace(self, slimItem):
        logger.debug('FighterSquadronComponent.OnAddedToSpace %d', self.itemID)
        self.OnSlimItemUpdated(slimItem)

    def OnSlimItemUpdated(self, slimItem):
        self.squadronSize = GetSquadronSizeFromSlimItem(slimItem)
        self.UpdateTargetBracket()

    def OnTargetBracketAdded(self, targetBracket):
        logger.debug('Target bracket added %d', self.itemID)
        self.targetBracket = targetBracket
        self.UpdateTargetBracket()

    def UpdateTargetBracket(self):
        if self.targetBracket:
            self.targetBracket.SetSquadronSize(self.squadronSize)

    def OnTargetBracketRemoved(self):
        logger.debug('Target bracket removed %d', self.itemID)
        self.targetBracket = None
