#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\evegraphics\fsd\base.py
import os
try:
    import fsd.schemas.binaryLoader as binaryLoader
except ImportError:
    import site
    branchRoot = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
    site.addsitedir(os.path.abspath(os.path.join(branchRoot, 'packages')))
    import fsd.schemas.binaryLoader as binaryLoader

class BuiltDataLoader(object):
    __binary__ = None
    __resBuiltFile__ = None
    __autobuildBuiltFile__ = None

    @classmethod
    def __LoadBinaryFromResFolder(cls):
        data = binaryLoader.LoadFSDDataForCFG(cls.__resBuiltFile__)
        if data is None:
            raise ImportError
        return data

    @classmethod
    def __LoadBinaryFromAutobuildFolder(cls):
        import devenv
        pathRelativeToBranchRoot = cls.__autobuildBuiltFile__
        autobuildFilePath = os.path.abspath(os.path.join(devenv.BRANCHROOT, pathRelativeToBranchRoot))
        return binaryLoader.LoadFSDDataInPython(autobuildFilePath)

    @classmethod
    def __LoadBinary(cls):
        try:
            return cls.__LoadBinaryFromResFolder()
        except ImportError:
            return cls.__LoadBinaryFromAutobuildFolder()

    @classmethod
    def GetData(cls):
        if cls.__binary__ is None:
            cls.__binary__ = cls.__LoadBinary()
        return cls.__binary__

    @classmethod
    def ReloadData(cls):
        cls.__binary__ = None
        try:
            cls.__LoadBinaryFromResFolder()
            import devenv
            import blue
            import shutil, os, stat
            autobuildFilePath = os.path.abspath(os.path.join(devenv.BRANCHROOT, cls.__autobuildBuiltFile__))
            resFilePath = blue.paths.ResolvePath(cls.__resBuiltFile__)
            os.chmod(resFilePath, stat.S_IWRITE)
            shutil.copyfile(autobuildFilePath, resFilePath)
        except ImportError:
            pass
