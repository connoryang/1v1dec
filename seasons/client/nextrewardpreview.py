#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\seasons\client\nextrewardpreview.py
import carbonui.const as uiconst
import log
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from seasons.client.uiutils import fill_frame_background_color_for_container, get_reward_icon_in_size
REWARD_ICON_PADDING = 1
FRAME_COLOR = (1.0, 1.0, 1.0)
FRAME_OPACITY = 0.3
PREVIEW_ICON_SIZE = 128

class NextRewardPreview(Container):
    __notifyevents__ = ['OnSeasonalPointsUpdatedInClient', 'OnSeasonalGoalsResetInClient']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.season_service = attributes.season_service
        self.base_container = Container(name='base_container', parent=self, align=uiconst.CENTER, width=self.width, height=self.height)
        Frame(name='reward_frame', parent=self, bgParent=self.base_container, frameConst=uiconst.FRAME_BORDER1_CORNER0, opacity=FRAME_OPACITY, color=FRAME_COLOR)
        fill_frame_background_color_for_container(self.base_container)
        self._update_next_reward_icon()

    def _update_next_reward_icon(self):
        reward = self.season_service.get_next_reward()
        if not reward:
            reward = self.season_service.get_last_reward()
        try:
            self.reward_icon = get_reward_icon_in_size(reward_type_id=reward['reward_type_id'], size=PREVIEW_ICON_SIZE, name='reward_icon', parent=self.base_container, align=uiconst.TOALL, padding=REWARD_ICON_PADDING)
        except Exception:
            self.reward_icon = None
            log.LogError('Failed to load Scope Network next reward icon for item type %d' % reward['reward_type_id'])

    def OnSeasonalPointsUpdatedInClient(self, season_points):
        self._update_next_reward_icon()

    def OnSeasonalGoalsResetInClient(self):
        self._update_next_reward_icon()
