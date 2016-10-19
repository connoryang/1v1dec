#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\notifications\client\bountyNotificationAdapter.py


class BountyNotificationAdapter(object):
    __notifyevents__ = ['OnBountyAddedToPayout']

    def __init__(self, loggerService):
        self.loggerService = loggerService

    def OnBountyAddedToPayout(self, dataDict):
        amount = dataDict['amount']
        payoutTimestamp = dataDict['payoutTime']
        enemyTypeID = dataDict['enemyTypeID']
        self.loggerService.AddBountyMessage(amount, payoutTimestamp, enemyTypeID)
