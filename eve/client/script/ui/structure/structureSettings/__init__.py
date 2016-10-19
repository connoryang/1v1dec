#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\structureSettings\__init__.py
from eve.client.script.ui.util.linkUtil import GetValueFromTextLink
import structures

def AreGroupNodes(dragData):
    if not dragData:
        return False
    firstNode = dragData[0]
    if firstNode.get('nodeType', None) == 'AccessGroupEntry':
        return True
    if firstNode.Get('__guid__', None) != 'TextLink':
        return False
    url = firstNode.Get('url', '')
    if url.startswith('accessGroup:'):
        return True
    return False


def GetGroupIDFromNode(node):
    if not AreGroupNodes([node]):
        return
    if node.get('nodeType', None) == 'AccessGroupEntry':
        return node.groupID
    if node.Get('__guid__', None) == 'TextLink':
        return GetValueFromTextLink(node, linkType='accessGroup:')


def CanHaveGroups(settingID):
    return settingID in structures.SETTINGS_VALUE_HAS_GROUPS
