#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\dockedUI\__init__.py
from eve.common.script.sys.eveCfg import IsDockedInStructure

def ReloadLobbyWnd():
    lobbyClass = GetLobbyClass()
    lobbyClass.CloseIfOpen()
    OpenLobbyWnd()


def OpenLobbyWnd():
    lobbyClass = GetLobbyClass()
    if UsingNewLobbyClass():
        if session.stationid2:
            from eve.client.script.ui.shared.dockedUI.controllers.stationController import StationController
            lobbyClass.Open(controller=StationController())
        elif IsDockedInStructure():
            from eve.client.script.ui.shared.dockedUI.controllers.structureController import StructureController
            lobbyClass.Open(controller=StructureController(itemID=session.structureid))
    elif session.stationid2:
        lobbyClass.Open()


def GetLobbyClass():
    if UsingNewLobbyClass():
        from eve.client.script.ui.shared.dockedUI.lobbyWnd import LobbyWnd
        return LobbyWnd
    else:
        from eve.client.script.ui.station.lobby import Lobby
        return Lobby


def UsingNewLobbyClass():
    return settings.user.ui.Get('test_useNeLobby', True)
