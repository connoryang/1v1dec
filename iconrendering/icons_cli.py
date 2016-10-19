#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\iconrendering\icons_cli.py
import logging
import argparse
import os
import sys
import shutil
import string
import yaml
import _appsetup
import devenv
import devenv.respathutils as respathutils
import fsdauthoringutils
import osutils
import stdlogutils
import ccpp4
import imgdiff
import iconrendering
import iconrendering.rendermanagement as rendermanagement
L = logging.getLogger('iec_cli_%s' % os.getpid())
DEBUG = False
CLEANUP = False
CHECKOUT = False
TOLERANCE = 0.01
RENDER_PATH = os.path.abspath(os.path.join(devenv.EVEROOT, 'client/res/UI/Texture/Icons/renders/'))

def GetTmpRenderPath():
    return RENDER_PATH + '_tmp'


def ParseOpts():
    parser = argparse.ArgumentParser(description='Render icons for assets. These are the icons used by the client.\nWhen rendering you can specify --checkout argument to actually check out files from Perforce and update them.\nWithout that flag renders will go into a temporary folder in path: %s\n\nBy default all icons are rendered, the --respath argument can be used to render a single asset.\nFor debugging purposes --takeonly can be used to limit the number of assets that gets rendered\n.' % GetTmpRenderPath())
    parser.add_argument('--debug', default=DEBUG, action='store_true', help='Output debug information.')
    parser.add_argument('--takeonly', type=int, default=0, help='Only render this many of each type. Useful when debugging.')
    parser.add_argument('--checkout', default=CHECKOUT, help='Choose whether to check out the changes made.Defaults to False.')
    parser.add_argument('--cleanup', default=CLEANUP, help='Choose whether to delete the output render folder.Defaults to False.')
    parser.add_argument('--respath', default='', help='Only generate icons related to a specific graphic resource path.')
    parser.add_argument('--dna', default='', help='Only generate icons related to a specific dna of the form hull:faction:race.')
    return parser.parse_args()


def Main():
    opts = ParseOpts()
    loglevel = logging.DEBUG if opts.debug else logging.INFO
    logging.basicConfig(level=loglevel, filename=stdlogutils.GetTimestampedFilename2(iconrendering.APPNAME), format=stdlogutils.Fmt.NTLM)
    streamh = logging.StreamHandler(sys.stdout)
    streamh.setFormatter(stdlogutils.Fmt.FMT_NTLM)
    L.addHandler(streamh)
    renderFolder = GetTmpRenderPath()
    if os.path.exists(renderFolder):
        osutils.SafeRmTree(renderFolder)
    resmapper = fsdauthoringutils.GraphicsCache(devenv.EVEROOT)
    invmapper = None
    _appsetup.CreateTrinityApp()
    mgr = rendermanagement.RenderManager(resmapper, invmapper, L, renderFolder, opts.takeonly)
    if opts.respath or opts.dna:
        mgr.RenderSingle(resPath=opts.respath, dnaString=opts.dna)
    else:
        mgr.RenderInGameIcons()
    if opts.checkout:
        L.debug('P4 Checkout started.')
        p4 = ccpp4.P4Init()
    dest_dict = GetDestDirs(renderFolder)
    before = set(map(string.lower, dest_dict.keys()))
    after = GetFiles(renderFolder)
    added = list(after.difference(before))
    deleted = list(before.difference(after))
    filesToCompare = list(after.intersection(before))
    changed = []
    for fileName in filesToCompare:
        iconResPath = dest_dict[fileName]
        renderPath = os.path.join(renderFolder, fileName)
        iconPath = respathutils.ExpandResPath(iconResPath, respathutils.GetClientRes())
        if os.path.exists(iconPath):
            diffResult = imgdiff.ImgDiff(iconPath, renderPath, normal=False, alpha=False)
            error = diffResult['Color']['MeanAbsoluteError']
            if error > TOLERANCE:
                changed.append(fileName)
        else:
            changed.append(fileName)

    if opts.checkout:
        for fileName in added + changed:
            iconResPath = dest_dict[fileName]
            iconPath = respathutils.ExpandResPath(iconResPath, respathutils.GetClientRes())
            renderPath = os.path.join(renderFolder, fileName)
            L.debug('P4 Edit or Add: %s', fileName)
            p4.EditOrAdd(iconPath)
            icon_dir = os.path.dirname(iconPath)
            if not os.path.exists(icon_dir):
                os.makedirs(icon_dir)
            if os.path.exists(renderPath):
                shutil.copy(renderPath, iconPath)

        allfiles = added + changed
        GetPath = lambda fileName: respathutils.ExpandResPath(dest_dict[fileName], respathutils.GetClientRes())
        if not (opts.takeonly or opts.respath):
            for deletedFile in deleted:
                L.debug('P4 Deleting: %s', deletedFile)
                p4.run_delete(GetPath(deletedFile))

            allfiles = allfiles + deleted
        osfiles = map(GetPath, allfiles)
        depotFiles = map(lambda wh: wh['depotFile'], p4.run_where(osfiles))
        if len(depotFiles):
            c = p4.Change(description='Ingame Icon generation.', files=depotFiles, save=False)
            changeno = p4.SaveChange(c)
        L.debug('P4 Checkout done.')
    if opts.cleanup:
        osutils.SafeRmTree(renderFolder)


def GetFiles(root):
    return set(map(string.lower, os.listdir(root)))


GRAPHICID_DATA = os.path.join(devenv.EVEROOT, 'staticData\\graphicIDs\\graphicIDs.staticdata')
CONTENTRES = respathutils.GetContentRes().lower()
RES_ROOT = CONTENTRES
DX9_ROOT = os.path.join(RES_ROOT, 'dx9')

def GetDestDirs(render_path):
    files = os.listdir(render_path)
    icon_dict = {}
    icon_dest_dict = {}
    for icon_filename in files:
        graphicID = icon_filename.split('_')[0]
        if int(graphicID) in icon_dict:
            icon_dict[int(graphicID)].append(icon_filename.lower())
        else:
            icon_dict[int(graphicID)] = [icon_filename.lower()]

    graphicid_file = open(GRAPHICID_DATA, 'r')
    graphicids = yaml.load(graphicid_file.read())
    graphicid_file.close()
    assetdirs = {}
    for dirpath, dirnames, filenames in os.walk(DX9_ROOT):
        for filename in filenames:
            if 'sofhull_' in filename.lower() and 'redesign' not in dirpath.lower():
                assetdirs[filename.lower()] = dirpath.replace(RES_ROOT, 'res:').replace('\\', '/').lower()

    for currID in icon_dict.keys():
        if 'sofHullName' in graphicids[currID]:
            sof_hull_name = graphicids[currID].get('sofHullName', '')
            if sof_hull_name:
                if 'state' in sof_hull_name.lower():
                    red_name = 'sofhull_' + '_'.join(sof_hull_name.lower().split('_')[:-2]) + '.red'
                    destdir = get_icon_dir(assetdirs, red_name)
                else:
                    red_name = 'sofhull_' + sof_hull_name.lower() + '.red'
                    destdir = get_icon_dir(assetdirs, red_name)
        else:
            graphic_file = graphicids[currID].get('graphicFile', '')
            if graphic_file:
                destdir = os.path.join(os.path.dirname(graphic_file).lower(), 'icons')
            else:
                continue
        for icon_name in icon_dict[currID]:
            print icon_name
            icon_dest_dict[icon_name] = os.path.join(destdir, icon_name)

    return icon_dest_dict


def get_icon_dir(assetdirs, red_name):
    asset_dir = assetdirs.get(red_name)
    if not asset_dir:
        return None
    redpath = respathutils.ExpandResPath(os.path.join(asset_dir, red_name), respathutils.GetContentRes())
    redfile = open(redpath, 'r')
    reddict = yaml.load(redfile.read())
    geomdir = os.path.dirname(reddict['geometryResFilePath'])
    destdir = os.path.join(geomdir, 'icons')
    return destdir


if __name__ == '__main__':
    try:
        Main()
    except Exception:
        logging.getLogger().error('Unhandled error!', exc_info=True)
        raise
