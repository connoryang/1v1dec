#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\neocom\contracts\contractDraggableIcon.py
from carbonui.primitives.container import Container
from utillib import KeyVal

class ContractDraggableIcon(Container):
    __guid__ = 'xtriui.ContractDraggableIcon'
    isDragObject = True

    def Startup(self, icon, contract, contractTitle):
        self.contract = contract
        self.contractTitle = contractTitle

    def GetDragData(self, *args):
        entry = KeyVal()
        entry.solarSystemID = self.contract.startSolarSystemID
        entry.contractID = self.contract.contractID
        entry.name = self.contractTitle
        entry.__guid__ = 'listentry.ContractEntry'
        return [entry]
