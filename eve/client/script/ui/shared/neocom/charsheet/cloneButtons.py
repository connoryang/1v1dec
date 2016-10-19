#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\neocom\charsheet\cloneButtons.py
from carbonui import const as uiconst
from eve.client.script.ui.control.themeColored import LineThemeColored
import localization
import uicontrols
__author__ = 'arnarb'

class CloneButtons(uicontrols.SE_BaseClassCore):
    __guid__ = 'listentry.CloneButtons'
    default_showHilite = False

    def Startup(self, args):
        jumpText = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/JumpCloneScroll/Jump')
        self.sr.JumpBtn = uicontrols.Button(parent=self, label=jumpText, align=uiconst.CENTER, func=self.OnClickJump)
        destroyLabel = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/JumpCloneScroll/Destroy')
        self.sr.DecomissionBtn = uicontrols.Button(parent=self, label=destroyLabel, align=uiconst.CENTER, func=self.OnClickDecomission)
        LineThemeColored(parent=self, align=uiconst.TOBOTTOM, opacity=0.4)

    def Load(self, node):
        self.sr.node = node
        self.locationID = node.locationID
        self.jumpCloneID = node.jumpCloneID
        self.sr.JumpBtn.width = self.sr.DecomissionBtn.width = max(self.sr.JumpBtn.width, self.sr.DecomissionBtn.width)
        self.sr.JumpBtn.left = -self.sr.JumpBtn.width / 2
        self.sr.DecomissionBtn.left = self.sr.DecomissionBtn.width / 2
        self.sr.JumpBtn.Disable()
        self.sr.DecomissionBtn.Disable()
        validLocation = self.locationID in cfg.evelocations
        if validLocation:
            self.sr.DecomissionBtn.Enable()
            if session.stationid or session.structureid:
                self.sr.JumpBtn.Enable()

    def GetHeight(self, *args):
        node, _ = args
        node.height = 32
        return node.height

    def OnClickJump(self, *args):
        sm.GetService('clonejump').CloneJump(self.locationID)

    def OnClickDecomission(self, *args):
        sm.GetService('clonejump').DestroyInstalledClone(self.jumpCloneID)
