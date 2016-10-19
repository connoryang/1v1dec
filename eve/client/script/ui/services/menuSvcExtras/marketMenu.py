#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\services\menuSvcExtras\marketMenu.py
import form
import structures
import util

def MultiSell(invItems):
    sm.GetService('marketutils').StartupCheck()
    wnd = form.SellItems.GetIfOpen()
    if wnd is not None:
        wnd.AddPreItems(invItems[0])
        wnd.Maximize()
    else:
        itemsToSell = invItems[0]
        itemLocationID = sm.GetService('invCache').GetStationIDOfItem(itemsToSell[0][0])
        if not util.IsStation(itemLocationID):
            sm.RemoteSvc('structureSettings').CharacterCheckService(itemLocationID, structures.SERVICE_MARKET)
        form.SellItems.Open(preItems=invItems[0])
