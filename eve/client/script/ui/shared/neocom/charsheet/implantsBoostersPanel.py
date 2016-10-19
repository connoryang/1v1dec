#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\neocom\charsheet\implantsBoostersPanel.py
import evetypes
from carbonui.primitives.container import Container
from carbonui.util.sortUtil import SortListOfTuples
from eve.client.script.ui.control import entries
from eve.client.script.ui.control.eveScroll import Scroll
from eve.common.script.sys.eveCfg import IconFile
from localization import GetByLabel
import blue

class ImplantsBoostersPanel(Container):
    default_name = 'ImplantsBoostersPanel'
    __notifyevents__ = ['OnGodmaItemChange']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.scroll = Scroll(parent=self, padding=(0, 4, 0, 4))

    def LoadPanel(self, *args):
        mygodma = self.GetMyGodmaItem(session.charid)
        if not mygodma:
            return
        implants = mygodma.implants
        boosters = mygodma.boosters
        godma = sm.GetService('godma')
        implants = SortListOfTuples([ (getattr(godma.GetType(implant.typeID), 'implantness', None), implant) for implant in implants ])
        boosters = SortListOfTuples([ (getattr(godma.GetType(booster.boosterTypeID), 'boosterness', None), booster) for booster in boosters ])
        scrolllist = []
        if implants:
            scrolllist.append(entries.Get('Header', {'label': GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Augmentations/Implants', implantCount=len(implants))}))
            for booster in implants:
                scrolllist.append(entries.Get('ImplantEntry', {'implant_booster': booster,
                 'label': evetypes.GetName(booster.typeID)}))

            if boosters:
                scrolllist.append(entries.Get('Divider'))
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        staticMgr = dogmaLocation.dogmaStaticMgr
        if boosters:
            scrolllist.append(entries.Get('Header', {'label': GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Augmentations/Boosters', boosterCount=len(boosters))}))
            for booster in boosters:
                scrolllist.append(entries.Get('ImplantEntry', {'implant_booster': booster,
                 'label': evetypes.GetName(booster.boosterTypeID)}))
                boosterEffects = staticMgr.GetPassiveFilteredEffectsByType(booster.boosterTypeID)
                for effectID in boosterEffects:
                    eff = cfg.dgmeffects.Get(effectID)
                    chanceAttributeID = staticMgr.effects[effectID].fittingUsageChanceAttributeID
                    if chanceAttributeID and effectID in booster.sideEffectIDs:
                        scrolllist.append(entries.Get('IconEntry', {'line': 1,
                         'hint': eff.displayName,
                         'text': None,
                         'label': eff.displayName,
                         'icon': IconFile(eff.iconID),
                         'selectable': 0,
                         'iconoffset': 32,
                         'iconsize': 22,
                         'linecolor': (1.0, 1.0, 1.0, 0.125)}))

                scrolllist.append(entries.Get('Divider'))

        self.scroll.sr.id = 'charsheet_implantandboosters'
        self.scroll.Load(fixedEntryHeight=32, contentList=scrolllist, noContentHint=GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Augmentations/NoImplantOrBoosterInEffect'))

    def GetMyGodmaItem(self, itemID):
        ret = sm.GetService('godma').GetItem(itemID)
        while ret is None and not self.destroyed:
            blue.pyos.synchro.SleepWallclock(500)
            ret = sm.GetService('godma').GetItem(itemID)

        return ret

    def OnGodmaItemChange(self, item, change):
        if const.ixLocationID in change and item.categoryID == const.categoryImplant and item.flagID in [const.flagBooster, const.flagImplant]:
            sm.GetService('neocom').Blink('charactersheet')
            if self.showing == 'myimplants_boosters':
                self.LoadImplantsAndBoostersPanel()
