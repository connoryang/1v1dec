#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\extras\tourneyUISvc.py
import service
import carbonui.const as uiconst
import tourneyBanUI

class TourneyUISvc(service.Service):
    __guid__ = 'svc.tourneyUISvc'
    __notifyevents__ = ['OnTournamentPerformBan', 'OnChangeFleetBoss']

    def OnTournamentPerformBan(self, banID, numBans, curBans, deadline, respondToNodeID, tourneyID):
        self.LogInfo('OnTourneyBan recv', banID, numBans, curBans, deadline, respondToNodeID)
        banWindow = tourneyBanUI.TourneyBanUI
        banWindow.CloseIfOpen()
        tourneyMgr = sm.RemoteSvc('tourneyMgr')
        tournamentShipDetails = tourneyMgr.QueryShipList(tourneyID)
        shipList = tournamentShipDetails['allowedShipList']
        banBox = banWindow.Open()
        banBox.Execute(banID, numBans, curBans, deadline, respondToNodeID, shipList)
        banBox.ShowModal()

    def OnChangeFleetBoss(self, charID, respondToNodeID):
        self.LogInfo('OnChangeFleetBoss received', charID, respondToNodeID)
        response = eve.Message('CustomQuestion', {'header': 'Team Captain Selection',
         'question': '{} has nominated you as a Team Member for a Tournament Match. Do you accept?             <br><br>Accepting means they will be able to see your fleet composition.'.format(cfg.eveowners.Get(charID).name)}, uiconst.YESNO)
        if response == uiconst.ID_YES:
            machoNet = sm.GetService('machoNet')
            remoteTourneyMgr = machoNet.ConnectToRemoteService('tourneyMgr', respondToNodeID)
            remoteTourneyMgr.ExecuteMemberChange()
