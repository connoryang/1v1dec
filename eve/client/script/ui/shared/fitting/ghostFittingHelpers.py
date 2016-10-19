#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fitting\ghostFittingHelpers.py


def TryGhostFitItemOnMouseAction(node, oldWindow = True):
    from eve.client.script.ui.shared.fitting.fittingWnd import FittingWindow2
    wnd2 = FittingWindow2.GetIfOpen()
    if wnd2 is not None:
        wnd2.GhostFitItem(node)
    if sm.IsServiceRunning('fittingSvc') and sm.GetService('fittingSvc').IsGhostFittingEnabled():
        from eve.client.script.ui.shared.fittingGhost.fittingWndGhost import FittingWindowGhost
        ghostFittingWnd = FittingWindowGhost.GetIfOpen()
        if ghostFittingWnd is not None:
            ghostFittingWnd.GhostFitItem(node)
