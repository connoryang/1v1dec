#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\billboards\__init__.py
from billboardsystem import BillboardSystem
BILLBOARD_WIDTH = 1024
BILLBOARD_HEIGHT = 576
BILLBOARD_FALLBACK_IMAGE = 'res:/video/billboardswide/fallback.png'
BILLBOARD_FALLBACK_IMAGE_ZN = 'res:/video/billboardswide_zn/fallback.png'
BILLBOARD_VIDEO_DIRECTORY = 'res:/video/billboardswide'
BILLBOARD_VIDEO_DIRECTORY_ZN = 'res:/video/billboardswide_zn'
BILLBOARD_DYNAMIC_RESOURCE_NAME = 'billboardvideos'

def get_billboard_video_path():
    if boot.region != 'optic':
        return BILLBOARD_VIDEO_DIRECTORY
    else:
        return BILLBOARD_VIDEO_DIRECTORY_ZN


def get_billboard_fallback_image():
    if boot.region != 'optic':
        return BILLBOARD_FALLBACK_IMAGE
    else:
        return BILLBOARD_FALLBACK_IMAGE_ZN


def get_billboard_system():
    try:
        return get_billboard_system._system
    except AttributeError:
        system = BillboardSystem()
        get_billboard_system._system = system
        return system


def load_billboard_playlist():
    from videoplayer import playlistresource
    playlistresource.register_resource_constructor(BILLBOARD_DYNAMIC_RESOURCE_NAME, BILLBOARD_WIDTH, BILLBOARD_HEIGHT, playlistresource.shuffled_videos(get_billboard_video_path()), get_billboard_fallback_image())
