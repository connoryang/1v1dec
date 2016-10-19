#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\station\pvptrade\tradeUtil.py
from eve.client.script.ui.services.menuSvcExtras.invItemFunctions import DeliverToStructure
from eve.common.script.sys.eveCfg import IsEvePlayerCharacter

def TryInitiateTrade(charID, nodes):
    if charID == session.charid:
        return
    if not IsEvePlayerCharacter(charID):
        return
    if session.stationid or session.structureid:
        return sm.StartService('pvptrade').StartTradeSession(charID, tradeItems=nodes)
