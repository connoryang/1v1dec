#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\util\linkUtil.py


def GetShowInfoLink(typeID, text, itemID = None):
    if itemID:
        return '<a href="showinfo:%s//%s">%s</a>' % (typeID, itemID, text)
    else:
        return '<a href="showinfo:%s">%s</a>' % (typeID, text)
