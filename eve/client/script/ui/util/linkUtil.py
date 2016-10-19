#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\util\linkUtil.py
from carbonui.util.stringManip import GetAsUnicode
SHOW_INFO = 'showinfo:'

def IsLink(text):
    textAsUnicode = GetAsUnicode(text)
    if textAsUnicode.find('<url') != -1:
        return True
    if textAsUnicode.find('<a href') != -1:
        return True
    return False


def GetCharIDFromTextLink(node):
    validTypeIDs = const.characterTypeByBloodline.values()
    return GetItemIDFromTextLink(node, validTypeIDs)


def GetTextLinkUrl(node, linkType = SHOW_INFO):
    if node.Get('__guid__', None) != 'TextLink':
        return
    url = node.Get('url', '')
    if not url.startswith(linkType):
        return
    return url


def GetItemIDFromTextLink(node, validTypeIDs, linkType = SHOW_INFO):
    url = GetTextLinkUrl(node, linkType)
    if url is None:
        return
    typeIDAndItemID = url.replace(linkType, '')
    parts = typeIDAndItemID.split('//')
    typeID = int(parts[0])
    if validTypeIDs and typeID not in validTypeIDs:
        return
    itemID = int(parts[-1])
    return itemID


def GetTypeIDFromTextLink(node):
    return GetValueFromTextLink(node, linkType=SHOW_INFO)


def GetValueFromTextLink(node, linkType = SHOW_INFO):
    url = GetTextLinkUrl(node, linkType=linkType)
    if url is None:
        return
    typeIDAndItemID = url.replace(linkType, '')
    parts = typeIDAndItemID.split('//')
    typeID = int(parts[0])
    return typeID
