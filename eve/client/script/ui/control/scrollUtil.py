#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\control\scrollUtil.py
import itertools

class TabFinder(object):

    def GetTabStops(self, nodes, headertabs, entryClass, idx = None):
        columnWidthsInNodes = [ entryClass.GetColWidths(node, idx) for node in nodes ]
        maxContentWidths = [ max(x) for x in zip(*columnWidthsInNodes) ]
        headerWidths = uicore.font.GetTabstopsAsWidth(uicore.font.MeasureTabstops(headertabs))
        return self._GetMaxTabStops(maxContentWidths, headerWidths)

    def _GetMaxTabStops(self, maxContentWidth, headerWidths):
        maxColWidth = [ max(z) for z in itertools.izip_longest(*[maxContentWidth, headerWidths]) ]
        newTabStops = self._FindMaxTabstopsFromWidths(maxColWidth)
        return newTabStops

    def _FindMaxTabstopsFromWidths(self, maxColWidth):
        newTabStops = []
        currentLeft = 0
        for eachColWidth in maxColWidth:
            currentLeft += eachColWidth
            newTabStops.append(currentLeft)

        return newTabStops
