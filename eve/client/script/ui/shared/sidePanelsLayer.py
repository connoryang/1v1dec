#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\sidePanelsLayer.py
import uicontrols
import uicls
import carbonui.const as uiconst

class SidePanels(uicls.LayerCore):
    __guid__ = 'uicls.SidePanelsLayer'
    __notifyevents__ = ['OnHideUI', 'OnShowUI']

    def ApplyAttributes(self, attributes):
        uicls.LayerCore.ApplyAttributes(self, attributes)
        self.inactivePanels = ['sidePanel']
        self.leftPush = 0
        self.rightPush = 0
        sm.RegisterNotify(self)

    def OnShowUI(self):
        for each in self.children:
            if each.align != uiconst.TOALL:
                each.display = True

    def OnHideUI(self):
        for each in self.children:
            if each.align != uiconst.TOALL:
                each.display = False

    def OnOpenView(self):
        sm.GetService('neocom').CreateNeocom()
        sm.GetService('notificationUIService').Show()

    def OnCloseView(self):
        sm.GetService('notificationUIService').Hide()

    def UpdateAlignment(self, *args, **kw):
        needsUpdate = False
        for c in self.children:
            if c._alignmentDirty:
                needsUpdate = True
                break

        ret = uicls.LayerCore.UpdateAlignment(self, *args, **kw)
        if needsUpdate:
            self.UpdateWindowPositions()
        return ret

    def UpdateWindowPositions(self):
        dockedLeft = []
        dockedLeftGap = []
        dockedRight = []
        dockedRightGap = []
        for wnd in uicore.registry.GetValidWindows():
            if getattr(wnd, 'isImplanted', False):
                continue
            if wnd.name == 'mapbrowser':
                continue
            if wnd.align != uiconst.TOPLEFT:
                continue
            if wnd.left == self.leftPush:
                dockedLeft.append(wnd)
            elif wnd.left == self.leftPush + uicontrols.Window.SNAP_DISTANCE:
                dockedLeftGap.append(wnd)
            elif wnd.left + wnd.width == uicore.desktop.width - self.rightPush:
                dockedRight.append(wnd)
            elif wnd.left + wnd.width == uicore.desktop.width - self.rightPush - uicontrols.Window.SNAP_DISTANCE:
                dockedRightGap.append(wnd)

        self.leftPush, self.rightPush = self.GetSideOffset()
        for wnd in dockedLeft:
            wnd.left = self.leftPush

        for wnd in dockedLeftGap:
            wnd.left = self.leftPush + uicontrols.Window.SNAP_DISTANCE

        for wnd in dockedRight:
            wnd.left = uicore.desktop.width - self.rightPush - wnd.width

        for wnd in dockedRightGap:
            wnd.left = uicore.desktop.width - self.rightPush - wnd.width - uicontrols.Window.SNAP_DISTANCE

        layers = (uicore.layer.inflight, uicore.layer.station, uicore.layer.target)
        for layer in layers:
            layer.padLeft = self.leftPush
            layer.padRight = self.rightPush

        sm.ScatterEvent('OnUpdateWindowPosition', self.leftPush, self.rightPush)

    def GetSideOffset(self):
        leftPush = 0
        rightPush = 0
        for c in self.children:
            if not c.display or c.name in self.inactivePanels:
                continue
            if c.align == uiconst.TOLEFT:
                leftPush += c.width + c.left
            elif c.align == uiconst.TORIGHT:
                rightPush += c.width + c.left

        leftPush = int(round(leftPush))
        rightPush = int(round(rightPush))
        return (leftPush, rightPush)
