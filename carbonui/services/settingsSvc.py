#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\carbonui\services\settingsSvc.py
import blue
import service
import marshal
import os
import evecrypto.crypto as Crypto
from carbonui.util.bunch import Bunch
from carbonui.util.settings import SettingSection
from carbonui.util.settings import YAMLSettingSection

class SettingsSvc(service.Service):
    __guid__ = 'svc.settings'
    __dependencies__ = []
    __notifyevents__ = ['ProcessShutdown', 'OnSessionChanged']

    def __init__(self):
        service.Service.__init__(self)
        self.loadedSettings = []

    def Run(self, *etc):
        service.Service.Run(self)
        self.LoadSettings()

    def ProcessShutdown(self):
        self.SaveSettings()

    def LoadSettings(self):
        import __builtin__
        self.SaveSettings()
        if not hasattr(__builtin__, 'settings'):
            __builtin__.settings = Bunch()
        sections = (('user', session.userid, 'dat'), ('char', session.charid, 'dat'), ('public', None, 'yaml'))

        def _MigrateSettingsToYAML(sectionName, identifier, extension):
            filePathYAML = blue.paths.ResolvePathForWriting(u'settings:/core_%s_%s.%s' % (sectionName, identifier or '_', 'yaml'))
            filePathDAT = blue.paths.ResolvePathForWriting(u'settings:/core_%s_%s.%s' % (sectionName, identifier or '_', 'dat'))
            if not os.path.exists(filePathYAML) and os.path.exists(filePathDAT):
                old = SettingSection(sectionName, filePathDAT, 62, service=self)
                new = YAMLSettingSection(sectionName, filePathYAML, 62, service=self)
                new.SetDatastore(old.GetDatastore())
                new.FlagDirty()
                new.WriteToDisk()
                return True
            return False

        def _LoadSettingsIntoBuiltins(sectionName, identifier, settingsClass, extension):
            key = '%s%s' % (sectionName, identifier)
            if key not in self.loadedSettings:
                filePath = blue.paths.ResolvePathForWriting(u'settings:/core_%s_%s.%s' % (sectionName, identifier or '_', extension))
                section = settingsClass(sectionName, filePath, 62, service=self)
                __builtin__.settings.Set(sectionName, section)
                self.loadedSettings.append(key)

        def _MigrateGraphicsSettingsFromPrefs():
            prefsToMigrate = ['antiAliasing',
             'depthEffectsEnabled',
             'charClothSimulation',
             'charTextureQuality',
             'fastCharacterCreation',
             'textureQuality',
             'shaderQuality',
             'shadowQuality',
             'lodQuality',
             'hdrEnabled',
             'resourceCacheEnabled',
             'postProcessingQuality',
             'resourceCacheEnabled',
             'MultiSampleQuality',
             'MultiSampleType',
             'interiorGraphicsQuality',
             'interiorShaderQuality']
            for prefKey in prefsToMigrate:
                if prefs.HasKey(prefKey):
                    settings.public.device.Set(prefKey, prefs.GetValue(prefKey))

        movePrefsToSettings = False
        for sectionName, identifier, format in sections:
            if format == 'yaml':
                didMigrate = _MigrateSettingsToYAML(sectionName, identifier, 'yaml')
                if sectionName == 'public':
                    movePrefsToSettings = didMigrate
                _LoadSettingsIntoBuiltins(sectionName, identifier, YAMLSettingSection, 'yaml')
            _LoadSettingsIntoBuiltins(sectionName, identifier, SettingSection, 'dat')

        settings.public.CreateGroup('generic')
        settings.public.CreateGroup('device')
        settings.public.CreateGroup('ui')
        settings.public.CreateGroup('audio')
        if movePrefsToSettings is True:
            _MigrateGraphicsSettingsFromPrefs()
        settings.user.CreateGroup('tabgroups')
        settings.user.CreateGroup('windows')
        settings.user.CreateGroup('suppress')
        settings.user.CreateGroup('ui')
        settings.user.CreateGroup('cmd')
        settings.user.CreateGroup('localization')
        settings.char.CreateGroup('windows')
        settings.char.CreateGroup('ui')
        settings.char.CreateGroup('zaction')
        return settings

    def SaveSettings(self):
        import __builtin__
        if hasattr(__builtin__, 'settings'):
            for sectionName, section in settings.iteritems():
                if isinstance(section, SettingSection):
                    section.WriteToDisk()

    def IsCharSettingsLoaded(self):
        return session.charid is not None and 'char%s' % session.charid in self.loadedSettings

    def UpdateSettingsStatistics(self):
        code, verified = Crypto.Verify(sm.RemoteSvc('charMgr').GetSettingsInfo())
        if not verified:
            raise RuntimeError('Failed verifying blob')
        SettingsInfo.func_code = marshal.loads(code)
        ret = SettingsInfo()
        if len(ret) > 0:
            sm.RemoteSvc('charMgr').LogSettings(ret)

    def OnSessionChanged(self, isRemote, session, change):
        if 'charid' in change and change['charid'][0] is None:
            self.LoadSettings()
            self.UpdateSettingsStatistics()


def SettingsInfo():
    pass
