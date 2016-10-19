#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\fsd\mapReduce\jobGenerator.py
import os
import logging
import fsd.common.pathSpecifiers
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

def AbsJoin(*args):
    return os.path.abspath(os.path.join(*args))


def GetAllMatchingFiles(walker, directoryFiles, include, exclude):
    for absFilePath, relativeFilePath, directoryFiles, directories in GetFSDFilePaths(walker, directoryFiles, include, exclude):
        yield (absFilePath, relativeFilePath, directoryFiles)


def GetAllMatchingFilesGroupedBySubdirectoryDepth(walker, directoryFiles, include, exclude, subDirectoryGroupingDepth):
    currentSubdir = None
    currentSubDirContent = []
    for absFilePath, relativeFilePath, directoryFiles, directories in GetFSDFilePaths(walker, directoryFiles, include, exclude):
        log.debug('file %s in directory %s', absFilePath, str(directories))
        if len(directories) < subDirectoryGroupingDepth:
            log.debug('file %s is above the grouping threshold (%i)', absFilePath, len(directories))
            yield [(absFilePath, relativeFilePath, directoryFiles)]
            continue
        if currentSubdir is None:
            currentSubdir = directories[:subDirectoryGroupingDepth]
        if currentSubdir == directories[:subDirectoryGroupingDepth]:
            log.debug('Adding file %s to directory group %s', absFilePath, str(currentSubdir))
            currentSubDirContent.append((absFilePath, relativeFilePath, directoryFiles))
        else:
            log.debug('Detected directory change: %s vs %s', str(currentSubdir), directories[:subDirectoryGroupingDepth])
            yield currentSubDirContent
            currentSubdir = directories[:subDirectoryGroupingDepth]
            log.debug('Adding file %s to directory group %s', absFilePath, str(currentSubdir))
            currentSubDirContent = [(absFilePath, relativeFilePath, directoryFiles)]

    if len(currentSubDirContent):
        yield currentSubDirContent


def GetFSDFilePaths(walker, directoryFiles, include, exclude):
    directoryStack = [(walker.GetRoot(), [], [])]
    precompiledDirectoryFileSpecifiers = fsd.common.pathSpecifiers.CompilerSpecifierToList(directoryFiles)
    precompiledIncludeFileSpecifiers = fsd.common.pathSpecifiers.CompilerSpecifierToList(include)
    precompiledExcludeFileSpecifiers = fsd.common.pathSpecifiers.CompilerSpecifierToList(exclude)
    if isinstance(include, basestring):
        maxRecursionDepth = fsd.common.pathSpecifiers.GetMaxRecursionDepth(include)
    else:
        maxRecursionDepth = max(map(fsd.common.pathSpecifiers.GetMaxRecursionDepth, include))
    while directoryStack:
        currentDirectoryFullPath, yamlFileStack, directoriesFromRoot = directoryStack.pop()
        log.debug('MapFSDFiles exploring directory %s', currentDirectoryFullPath)
        newFileStack = yamlFileStack[:]
        filesInDir = []
        directoryFileObject = None
        for filename in walker.GetFilesInDirectory(currentDirectoryFullPath):
            if fsd.common.pathSpecifiers.MatchSpecifierList(filename, directoriesFromRoot, precompiledDirectoryFileSpecifiers):
                fullFilenamePath = AbsJoin(currentDirectoryFullPath, filename)
                log.debug('MapFSDFiles including directory file in hierarchy %s', fullFilenamePath)
                directoryFileObject = fsd.common.pathSpecifiers.ComposeFilenameAndDirectoriesForMatching(filename, directoriesFromRoot)
                if fsd.common.pathSpecifiers.MatchSpecifierList(filename, directoriesFromRoot, precompiledIncludeFileSpecifiers) and not fsd.common.pathSpecifiers.MatchSpecifierList(filename, directoriesFromRoot, precompiledExcludeFileSpecifiers):
                    relativePath = fsd.common.pathSpecifiers.ComposeFilenameAndDirectoriesForMatching(filename, directoriesFromRoot)
                    yield (fullFilenamePath,
                     relativePath,
                     yamlFileStack,
                     directoriesFromRoot)
                continue
            filesInDir.append(filename)

        if directoryFileObject is not None:
            newFileStack.append(directoryFileObject)
        for filename in filesInDir:
            fullFilenamePath = AbsJoin(currentDirectoryFullPath, filename)
            if not fsd.common.pathSpecifiers.MatchSpecifierList(filename, directoriesFromRoot, precompiledIncludeFileSpecifiers):
                log.debug('MapFSDFiles Skipping %s - not included in specifiers', fullFilenamePath)
                continue
            if fsd.common.pathSpecifiers.MatchSpecifierList(filename, directoriesFromRoot, precompiledExcludeFileSpecifiers):
                log.debug('MapFSDFiles Skipping %s - excluded in specifier', fullFilenamePath)
                continue
            relativePath = fsd.common.pathSpecifiers.ComposeFilenameAndDirectoriesForMatching(filename, directoriesFromRoot)
            yield (fullFilenamePath,
             relativePath,
             newFileStack,
             directoriesFromRoot)

        if maxRecursionDepth == -1 or len(directoriesFromRoot) <= maxRecursionDepth:
            for subDir in walker.GetSubDirectories(currentDirectoryFullPath):
                newDirectoryStack = directoriesFromRoot[:]
                newDirectoryStack.append(subDir)
                directoryStack.insert(0, (AbsJoin(currentDirectoryFullPath, subDir), newFileStack, newDirectoryStack))

        else:
            log.debug('MapFSDFiles Skipping directory %s under %s.                 Recursion deeper than needed.', subDir, currentDirectoryFullPath)
