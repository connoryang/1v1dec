#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\seasons\client\uiutils.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveIcon import Icon
from evetypes import GetIconID
SEASON_CURRENT_BANNER_HEIGHT = 341
SEASON_CURRENT_BANNER_WIDTH = 607
SEASON_DEFAULT_BACKGROUND_FILL_COLOR = (0, 0, 0, 0.35)
CHALLENGES_HEADER_BACKGROUND_FILL_COLOR = (1, 1, 1, 0.1)
SEASON_DEFAULT_BORDER_LINE_WEIGHT = 1
SEASON_DEFAULT_BORDER_LINE_COLOR = (118 / 255.0,
 163 / 255.0,
 255 / 255.0,
 0.7)
SEASONS_THEME_BACKGROUND_COLOR = (118 / 255.0,
 163 / 255.0,
 255 / 255.0,
 0.15)
SEASON_FRAME_BACKGROUND_FILL_COLOR = (0, 0, 0, 0.75)
SEASON_THEME_TEXT_COLOR_HIGHLIGHTED = (1, 1, 1, 1)
SEASON_THEME_TEXT_COLOR_REGULAR = (1, 1, 1, 0.75)
SEASON_THEME_TEXT_COLOR_INACTIVE = (1, 1, 1, 0.5)
SEASON_POINTS_CORNER_GRADIENT_OPACITY = 0.5
SEASON_FRAME_CORNER_GRADIENT = 'res:/UI/Texture/classes/Seasons/cornerGradient.png'
SEASON_LINE_BREAK_GRADIENT = 'res:/UI/Texture/classes/Seasons/lineBreakGradient.png'
ORIGINAL_ICON_SIZE = 64

def fill_default_background_color_for_container(container):
    fill_container_with_color(container, SEASON_DEFAULT_BACKGROUND_FILL_COLOR)


def fill_frame_background_color_for_container(container):
    fill_container_with_color(container, SEASON_FRAME_BACKGROUND_FILL_COLOR)


def fill_header_background_color_for_container(container):
    fill_container_with_color(container, CHALLENGES_HEADER_BACKGROUND_FILL_COLOR)


def fill_container_with_color(container, color):
    Fill(bgParent=container, color=color)


def fill_container_with_color_and_opacity(container, color, opacity):
    Fill(bgParent=container, color=color, opacity=opacity)


def add_base_border_line_to_container(container, alignment):
    Line(parent=container, align=alignment, weight=SEASON_DEFAULT_BORDER_LINE_WEIGHT, color=SEASON_DEFAULT_BORDER_LINE_COLOR)


def get_agent_icon(name, parent, align, size, agent_id):
    agent_icon = Icon(name=name, parent=parent, align=align, size=size, ignoreSize=True)
    sm.GetService('photo').GetPortrait(agent_id, size, agent_icon)
    return agent_icon


def add_season_points_corner_gradient(parent_container, season_points_gradient_left):
    season_points_corner_gradient_container = Container(name='season_points_corner_gradient_container', parent=parent_container, align=uiconst.TOLEFT_NOPUSH, width=parent_container.width, height=parent_container.height)
    Sprite(name='season_points_corner_gradient', parent=season_points_corner_gradient_container, texturePath=SEASON_FRAME_CORNER_GRADIENT, align=uiconst.TOPLEFT, width=parent_container.width, height=parent_container.height, opacity=SEASON_POINTS_CORNER_GRADIENT_OPACITY, useSizeFromTexture=True, left=season_points_gradient_left)


def get_reward_icon_in_size(reward_type_id, size, name, parent, align, padding = 0):
    icon_id = GetIconID(reward_type_id)
    reward_icon_texture = cfg.icons.Get(icon_id).iconFile
    reward_icon_texture_preview_size = get_reward_icon_texture_in_size(reward_icon_texture, size)
    return Sprite(name=name, parent=parent, align=align, padding=padding, texturePath=reward_icon_texture_preview_size)


def get_reward_icon_texture_in_size(reward_icon_texture, size):
    return reward_icon_texture.replace('_%d' % ORIGINAL_ICON_SIZE, '_%d' % size)
