#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\fsd\mapReduce\defaultWalker.py
import os
import tempfile

def ListSubDirs(path):
    for directoryContent in os.listdir(path):
        if os.path.isdir(os.path.join(path, directoryContent)):
            yield directoryContent


def ListFilesInDir(path):
    for directoryContent in os.listdir(path):
        if os.path.isfile(os.path.join(path, directoryContent)):
            yield directoryContent


class FileLoadingException(Exception):
    pass


class MapReduceDirectoryWalker(object):

    def __init__(self, rootPath, fileLoader, tempPath):
        self.rootPath = rootPath
        self.fileLoader = fileLoader
        if not os.path.exists(tempPath):
            os.makedirs(tempPath)
        self.tempPath = tempfile.mkdtemp(dir=tempPath)
        self.openTemporaryFiles = {}
        self.temporaryFiles = {}

    def GetRoot(self):
        return self.rootPath

    def GetFilesInDirectory(self, absolutePath):
        return ListFilesInDir(absolutePath)

    def GetSubDirectories(self, absolutePath):
        return ListSubDirs(absolutePath)

    def GetFileContents(self, absolutePath):
        with open(absolutePath, 'r') as f:
            try:
                return self.fileLoader(f)
            except Exception as e:
                raise FileLoadingException(str(e))

    def GetTemporaryFileForWriting(self, filename, mode):
        fullpath = os.path.join(self.tempPath, filename)
        if not os.path.exists(os.path.dirname(fullpath)):
            os.makedirs(os.path.dirname(fullpath))
        f = open(fullpath, 'wb')
        self.openTemporaryFiles[filename] = f
        return f

    def CloseTemporaryWriteFiles(self):
        for i, v in self.openTemporaryFiles.iteritems():
            self.temporaryFiles[i] = v.close()

        self.openTemporaryFiles = {}

    def OpenTemporaryFileForReading(self, filename):
        return open(os.path.join(self.tempPath, filename), 'rb')

    def IsFolderIncluded(self, directoryFileContents):
        return True
