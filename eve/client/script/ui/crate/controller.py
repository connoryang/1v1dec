#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\crate\controller.py
import collections
import crates
import localization
import signals

class LootController(object):

    def __init__(self, typeID, itemID, stacksize):
        self.typeID = typeID
        self.itemID = itemID
        self.stacksize = stacksize
        self.isOpening = False
        self._loot = None
        self.onOpen = signals.Signal()
        self.onFinish = signals.Signal()

    @property
    def staticData(self):
        return crates.CrateStorage()[self.typeID]

    @property
    def caption(self):
        return localization.GetByMessageID(self.staticData.nameID)

    @property
    def description(self):
        return localization.GetByMessageID(self.staticData.descriptionID)

    @property
    def animatedSplash(self):
        return self.staticData.animatedSplash

    @property
    def staticSplash(self):
        return self.staticData.staticSplash

    def OpenCrate(self):
        if self.stacksize <= 0:
            raise RuntimeError('No more containers')
        self.isOpening = True
        try:
            loot = sm.RemoteSvc('crateService').OpenCrate(self.itemID)
            self._loot = [ LootItem(*x) for x in loot ]
            self.stacksize -= 1
            self.onOpen()
        except Exception:
            self.isOpening = False
            raise

    def ClaimLoot(self, item):
        if not self._loot:
            raise RuntimeError('No loot to claim')
        if item not in self._loot:
            raise RuntimeError('Attempting to claim an invalid item')
        self._loot.remove(item)
        if not self._loot:
            self.isOpening = False

    @property
    def loot(self):
        return self._loot

    def Finish(self):
        self.onFinish()


LootItem = collections.namedtuple('LootItem', ['typeID', 'quantity', 'customInfo'])

def __SakeReloadHook():
    try:
        import form
        instance = form.CrateWindow.GetIfOpen()
        if instance:
            form.CrateWindow.Reload(instance)
    except Exception:
        import log
        log.LogException()
