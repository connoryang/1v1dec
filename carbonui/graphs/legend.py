#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\carbonui\graphs\legend.py
from packages.carbonui.primitives.container import Container

class Legend(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.legendItems = []

    def AddElement(self, element):
        legendItem = element.GetLegend(self)
        self.legendItems.append(legendItem)
