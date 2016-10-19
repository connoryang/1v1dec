#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\seasons\client\currenteventbanner.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from seasons.client.const import SEASON_CURRENT_BANNER_HEIGHT, SEASON_CURRENT_BANNER_WIDTH

class CurrentEventBanner(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        banner_texture = attributes.banner_texture
        size_factor = float(attributes.parent.width) / float(SEASON_CURRENT_BANNER_WIDTH)
        self.height = float(SEASON_CURRENT_BANNER_HEIGHT) * size_factor
        self.width = float(SEASON_CURRENT_BANNER_WIDTH) * size_factor
        Sprite(name='current_event_banner', parent=self, texturePath=banner_texture, align=uiconst.TOALL)
