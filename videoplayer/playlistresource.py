#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\videoplayer\playlistresource.py
import logging
import random
import re
import urllib
import blue
import trinity
import videoplayer
import uthread2
_error_handlers = set()
_state_change_handlers = set()
_play_list_finished_handlers = set()

def _is_low_quality():
    return trinity.GetShaderModel() == 'SM_3_0_LO'


class _VideoPlaylistController(object):

    def __init__(self):
        self.video = None
        self.weak_texture = None
        self.generate_mips = False
        self.constructor_params = {}
        self.playlist = None
        self.low_quality_texture_path = None
        self.destroyed = False

    def init(self, width, height, playlist, low_quality_texture_path = None, **kwargs):
        self.destroyed = False
        self.low_quality_texture_path = low_quality_texture_path
        self.generate_mips = kwargs.pop('generate_mips', False)
        self.constructor_params = kwargs
        self.playlist = playlist(**kwargs)

        def texture_destroyed():
            self._destroy()

        texture = trinity.TriTextureRes()
        self.weak_texture = blue.BluePythonWeakRef(texture)
        self.weak_texture.callback = texture_destroyed
        if not self.low_quality_texture_path or not _is_low_quality():
            uthread2.start_tasklet(self.play_next)
        else:
            self._create_low_quality_render_job()
        return texture

    def _create_low_quality_render_job(self):
        lq = blue.resMan.GetResource(self.low_quality_texture_path)

        def check():
            while True:
                if self.destroyed or not self.low_quality_texture_path or not _is_low_quality():
                    return
                if lq.isGood:
                    try:
                        self.weak_texture.object.CreateFromTexture(lq)
                    except:
                        pass

                    return
                blue.synchro.SleepWallclock(100)

        uthread2.start_tasklet(check)

    def play_next(self):
        if self.destroyed:
            return
        try:
            item = self.playlist.next()
        except StopIteration:
            for each in _play_list_finished_handlers:
                each(self.constructor_params, self.weak_texture.object)

            self._destroy()
            return

        if item.lower().startswith('http'):
            stream = blue.BlueNetworkStream(item)
        else:
            if blue.remoteFileCache.FileExists(item) and not blue.paths.FileExistsLocally(item):
                blue.paths.GetFileContentsWithYield(item)
            if self.destroyed:
                return
            stream = blue.paths.open(item, 'rb')
        self.video = videoplayer.VideoPlayer(stream, None)
        self.video.bgra_texture = self.weak_texture.object
        self.video.on_state_change = self._on_state_change
        self.video.on_create_textures = self._on_video_info_ready
        self.video.on_error = self._on_error

    def _on_state_change(self, player):
        if self.destroyed:
            return
        logging.debug('Video player state changed to %s', videoplayer.State.GetNameFromValue(player.state))
        for each in _state_change_handlers:
            each(player, self.constructor_params, self.weak_texture.object)

        if player.state == videoplayer.State.DONE:
            uthread2.start_tasklet(self.play_next)

    def _on_error(self, player):
        try:
            player.validate()
        except RuntimeError as e:
            logging.exception('Video player error')
            for each in _error_handlers:
                each(player, e, self.constructor_params, self.weak_texture.object)

            uthread2.start_tasklet(self.play_next)

    def _on_video_info_ready(self, _, width, height):
        if self.weak_texture.object:
            self.weak_texture.object.__init__(width, height, 1, trinity.PIXEL_FORMAT.B8G8R8A8_UNORM)

    def _destroy(self):
        if self.video:
            self.video.bgra_texture = None
            self.video.on_state_change = None
            self.video.on_create_textures = None
            self.video.on_error = None
        self.video = None
        self.destroyed = True
        if self.weak_texture is not None:
            self.weak_texture.callback = None


def _url_to_dict(param_string):
    params = {}
    expr = re.compile('\\?((\\w+)=([^&]*))(&?(\\w+)=([^&]*))*')
    match = expr.match(param_string)
    if match:
        for i in xrange(1, len(match.groups()), 3):
            if match.group(i) is not None:
                params[match.group(i + 1)] = str(urllib.unquote(match.group(i + 2)))

    return params


def register_resource_constructor(name, width, height, playlist, low_quality_texture_path = None):

    def play(param_string):
        try:
            rj = _VideoPlaylistController()
            return rj.init(width, height, playlist, low_quality_texture_path, **_url_to_dict(param_string))
        except:
            logging.exception('Exception in video playlist resource constructor')

    blue.resMan.RegisterResourceConstructor(name, play)


def register_error_handler(error_handler):
    _error_handlers.add(error_handler)


def unregister_error_handler(error_handler):
    _error_handlers.remove(error_handler)


def register_state_change_handler(state_change_handler):
    _state_change_handlers.add(state_change_handler)


def unregister_state_change_handler(state_change_handler):
    _state_change_handlers.remove(state_change_handler)


def register_playlist_finished_handler(playlist_finished_handler):
    _play_list_finished_handlers.add(playlist_finished_handler)


def unregister_playlist_finished_handler(playlist_finished_handler):
    _play_list_finished_handlers.remove(playlist_finished_handler)


def shuffled_videos(*res_path):
    paths = []
    for path in res_path:
        if not path.lower().startswith('http') and blue.paths.isdir(path):
            for each in blue.paths.listdir(path):
                if each.lower().endswith('.webm'):
                    paths.append('%s/%s' % (path, each))

        else:
            paths.append(path)

    def inner(**kwargs):
        random.shuffle(paths)
        index = 0
        while True:
            yield paths[index]
            index = (index + 1) % len(paths)

    return inner
