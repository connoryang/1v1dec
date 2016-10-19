#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\autoexec_common.py
import os
import sys
import blue
from carbon.common.script.sys.buildversion import GetBuildVersionAsInt
import logmodule
import sysinfo
import platform
import stdlogutils.logserver as stdlogserver
stdlogserver.InitLoggingToLogserver(stdlogserver.GetLoggingLevelFromPrefs())
try:
    import marshalstrings
except ImportError:
    pass

def ReturnFalse():
    return False


def LogStarting(mode):
    startedat = '%s %s version %s build %s starting %s %s' % (boot.appname,
     mode,
     boot.version,
     boot.build,
     blue.os.FormatUTC()[0],
     blue.os.FormatUTC()[2])
    print startedat
    logmodule.general.Log(startedat, logmodule.LGNOTICE)
    logmodule.general.Log('Python version: ' + sys.version, logmodule.LGNOTICE)
    if blue.sysinfo.isTransgaming:
        logmodule.general.Log('Transgaming? yes')
    else:
        logmodule.general.Log('Transgaming? no')
    if blue.sysinfo.isTransgaming:
        logmodule.general.Log('TG OS: ' + blue.win32.TGGetOS(), logmodule.LGNOTICE)
        logmodule.general.Log('TG SI: ' + repr(blue.win32.TGGetSystemInfo()), logmodule.LGNOTICE)
    if blue.sysinfo.isWine:
        logmodule.general.Log('Running on Wine', logmodule.LGNOTICE)
        logmodule.general.Log('Wine host OS: %s' % blue.sysinfo.wineHostOs, logmodule.LGNOTICE)
    logmodule.general.Log('Process bits: ' + repr(blue.sysinfo.processBitCount), logmodule.LGNOTICE)
    logmodule.general.Log('Wow64 process? ' + ('yes' if blue.sysinfo.processBitCount != blue.sysinfo.systemBitCount else 'no'), logmodule.LGNOTICE)
    if blue.sysinfo.os.platform == blue.OsPlatform.WINDOWS:
        logmodule.general.Log('System info: ' + repr(blue.win32.GetSystemInfo()), logmodule.LGNOTICE)
        if blue.sysinfo.processBitCount != blue.sysinfo.systemBitCount:
            logmodule.general.Log('Native system info: ' + repr(blue.win32.GetNativeSystemInfo()), logmodule.LGNOTICE)
    logmodule.general.Log(repr(sysinfo.get_os_platform_major_minor_patch()))


def LogStarted(mode):
    startedat = '%s %s version %s build %s started %s %s' % (boot.appname,
     mode,
     boot.version,
     boot.build,
     blue.os.FormatUTC()[0],
     blue.os.FormatUTC()[2])
    print strx(startedat)
    logmodule.general.Log(startedat, logmodule.LGINFO)
    logmodule.general.Log(startedat, logmodule.LGNOTICE)
    logmodule.general.Log(startedat, logmodule.LGWARN)
    logmodule.general.Log(startedat, logmodule.LGERR)


try:
    blue.SetBreakpadBuildNumber(GetBuildVersionAsInt())
    if blue.sysinfo.isTransgaming:
        blue.SetCrashKeyValues(u'OS', u'Mac')
    elif blue.sysinfo.isWine:
        host = blue.sysinfo.wineHostOs
        if host.startswith('Darwin'):
            platform = u'MacWine'
        else:
            platform = u'Linux'
        blue.SetCrashKeyValues(u'OS', platform)
    else:
        blue.SetCrashKeyValues(u'OS', u'Win')
except RuntimeError:
    pass

logdestination = prefs.ini.GetValue('networkLogging', '')
if logdestination:
    networklogport = prefs.ini.GetValue('networkLoggingPort', 12201)
    networklogThreshold = prefs.ini.GetValue('networkLoggingThreshold', 1)
    blue.EnableNetworkLogging(logdestination, networklogport, boot.role, networklogThreshold)
fileLoggingDirectory = None
fileLoggingThreshold = 0
args = blue.pyos.GetArg()
for arg in args:
    if arg.startswith('/fileLogDirectory'):
        try:
            fileLoggingDirectory = arg.split('=')[1]
        except IndexError:
            fileLoggingDirectory = None

if not fileLoggingDirectory:
    fileLoggingDirectory = prefs.ini.GetValue('fileLogDirectory', None)
    fileLoggingThreshold = int(prefs.ini.GetValue('fileLoggingThreshold', 1))
if fileLoggingDirectory:
    if not hasattr(blue, 'EnableFileLogging'):
        print 'File Logging configured but not supported'
    else:
        fileLoggingDirectory = os.path.normpath(fileLoggingDirectory)
        blue.EnableFileLogging(fileLoggingDirectory, boot.role, fileLoggingThreshold)

def setup_sentry(raven_impl, dsn, tags, environment = None, context = None, ignore_exceptions = None):
    if tags is None:
        tags = {}
    if context is None:
        context = {}
    tags['branch'] = boot.codename
    tags['role'] = boot.role
    tags['version'] = boot.version
    tags['sync'] = boot.sync
    tags['build'] = boot.build
    os_info = sysinfo.get_os_platform_major_minor_patch()
    readable = sysinfo.HUMAN_PLATFORMS[os_info['osPlatform']]
    tags['os'] = readable['os']
    tags['os_runtime'] = readable['runtime']
    tags['os_major'] = os_info['osMajor']
    tags['os_minor'] = os_info['osMinor']
    tags['os_patch'] = os_info['osPatch']
    tags['os_bit'] = os_info['osBit']
    tags['process_bit'] = blue.sysinfo.processBitCount
    dsn_override = None
    try:
        dsn_override = prefs.GetValue('sentry_dsn', None)
    except Exception as e:
        pass

    if dsn_override is not None:
        dsn = dsn_override
    context['platform.uname()'] = platform.uname()
    context.update(sysinfo.getProcessorInfo())
    raven_impl.raven_client(dsn=dsn, tags=tags, release=boot.build, environment=environment, context=context, ignore_exceptions=ignore_exceptions)
    logmodule.raven_client = raven_impl.capture_exception
