#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\notifications\client\oreMinedNotificationAdapter.py


class OreMinedNotificationAdapter(object):
    __notifyevents__ = ['OnOreMined']

    def __init__(self, loggerService):
        self.loggerService = loggerService

    def OnOreMined(self, dataDict):
        oreType = dataDict['oreType']
        volume = dataDict['volume']
        amount = dataDict['amount']
        self.loggerService.AddMiningMessage(oreType, volume, amount)
