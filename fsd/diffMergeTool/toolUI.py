#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\fsd\diffMergeTool\toolUI.py
import sys
from PySide import QtGui
from PySide import QtCore
from fsd.diffMergeTool.treeview import TreeViewWidget
from fsd.common.fsdYamlExtensions import FsdYamlDumper
import yaml
import unicodedata
import time
import threading
from fsd.diffMerge.frameworkInterface import FsdDiffMerger
from fsd.diffMerge.frameworkInterface import InsertItemToDictionaryAtLocation
from fsd.diffMerge.diffObjects import AreEqual
DOES_NOT_EXIST_STRING = '(DOES NOT EXIST)'

class DroppableQTextEdit(QtGui.QTextEdit):

    def __init__(self, parent = None):
        super(DroppableQTextEdit, self).__init__(parent)

    def dragEnterEvent(self, e):
        pass

    def dropEvent(self, e):
        self.setText(e.mimeData().text())


class FsdDiffMergeUI(QtGui.QWidget):

    def LoadArgument(self, argument, target):
        with open(argument, 'rb') as f:
            target.setText(f.read().decode('utf-8'))

    def _HandleCommandLineArguments(self, arguments):
        self.resultFile = None
        if arguments:
            if len(arguments) == 2:
                self.LoadArgument(arguments[0], self.top.mine)
                self.LoadArgument(arguments[1], self.top.theirs)
                self.top.hide()
                self.bottomRight.tabs.removePage(self.bottomRight.changeTab)
                self.bottomLeft.numberOfChanges.hide()
                self.bottomLeft.numberOfAdds.hide()
                self.SafeMerge()
            elif len(arguments) == 4:
                self.LoadArgument(arguments[0], self.top.base)
                self.LoadArgument(arguments[1], self.top.mine)
                self.LoadArgument(arguments[2], self.top.theirs)
                self.resultFile = arguments[3]
                self.top.hide()
                self.SafeMerge()
            else:
                print 'Unsupported argument count (%s), starting up normally' % str(len(arguments))

    def __init__(self, arguments):
        super(FsdDiffMergeUI, self).__init__()
        self.setAcceptDrops(True)
        self.merger = None
        self.InitUI()
        self._HandleCommandLineArguments(arguments)

    def _SetupTop(self):
        self.top = QtGui.QFrame(self)
        self.top.setFrameShape(QtGui.QFrame.StyledPanel)
        self.top.grid = QtGui.QGridLayout()
        self.top.grid.setSpacing(10)
        baseLabel = QtGui.QLabel('Base')
        mineLabel = QtGui.QLabel('Mine')
        theirLabel = QtGui.QLabel('Theirs')
        loadMineButton = QtGui.QPushButton('Browse')
        loadMineButton.clicked.connect(self.LoadFileToMine)
        loadBaseButton = QtGui.QPushButton('Browse')
        loadBaseButton.clicked.connect(self.LoadFileToBase)
        loadTheirsButton = QtGui.QPushButton('Browse')
        loadTheirsButton.clicked.connect(self.LoadFileToTheirs)
        mergeButton = QtGui.QPushButton('Safe Merge', self)
        mergeButton.clicked.connect(self.SafeMerge)
        self.top.base = DroppableQTextEdit()
        self.top.mine = DroppableQTextEdit()
        self.top.theirs = DroppableQTextEdit()
        self.top.grid.addWidget(mineLabel, 0, 0, 1, 1)
        self.top.grid.addWidget(loadMineButton, 0, 1, 1, 1)
        self.top.grid.addWidget(baseLabel, 0, 2, 1, 1)
        self.top.grid.addWidget(loadBaseButton, 0, 3, 1, 1)
        self.top.grid.addWidget(theirLabel, 0, 4, 1, 1)
        self.top.grid.addWidget(loadTheirsButton, 0, 5, 1, 1)
        self.top.grid.addWidget(self.top.mine, 1, 0, 1, 2)
        self.top.grid.addWidget(self.top.base, 1, 2, 1, 2)
        self.top.grid.addWidget(self.top.theirs, 1, 4, 1, 2)
        self.top.grid.addWidget(mergeButton, 2, 2, 1, 2)
        self.top.setLayout(self.top.grid)

    def _SetupBottomLeft(self):
        self.bottomLeft = QtGui.QFrame(self)
        self.bottomLeft.setFrameShape(QtGui.QFrame.StyledPanel)
        conflictLabel = QtGui.QLabel("<font color='#888888'>Conflicts</font>")
        changeLabel = QtGui.QLabel("<font color='#888888'>Changes</font>")
        addLabel = QtGui.QLabel("<font color='#888888'>Adds</font>")
        self.bottomLeft.numberOfAdds = QtGui.QLabel('')
        self.bottomLeft.numberOfChanges = QtGui.QLabel('')
        self.bottomLeft.numberOfConflicts = QtGui.QLabel('')
        self.bottomLeft.undoButton = QtGui.QPushButton('Undo', self)
        self.bottomLeft.undoButton.setEnabled(False)
        self.bottomLeft.undoList = []
        self.bottomLeft.undoButton.clicked.connect(self.Undo)
        self.bottomLeft.tree = TreeViewWidget()
        self.bottomLeft.saveButton = QtGui.QPushButton('Save', self)
        self.bottomLeft.saveButton.clicked.connect(self.Save)
        self.bottomLeft.statusBar = QtGui.QStatusBar(self)
        self.bottomLeft.statusBar.setSizeGripEnabled(False)
        self.bottomLeft.grid = QtGui.QGridLayout()
        self.bottomLeft.grid.setSpacing(10)
        self.bottomLeft.grid.addWidget(conflictLabel, 0, 0, 1, 1)
        self.bottomLeft.grid.addWidget(changeLabel, 0, 1, 1, 1)
        self.bottomLeft.grid.addWidget(addLabel, 0, 2, 1, 1)
        self.bottomLeft.grid.addWidget(self.bottomLeft.numberOfConflicts, 1, 0, 1, 1)
        self.bottomLeft.grid.addWidget(self.bottomLeft.numberOfChanges, 1, 1, 1, 1)
        self.bottomLeft.grid.addWidget(self.bottomLeft.numberOfAdds, 1, 2, 1, 1)
        self.bottomLeft.grid.addWidget(self.bottomLeft.undoButton, 1, 4, 1, 1)
        self.bottomLeft.grid.addWidget(self.bottomLeft.tree.GetWidget(), 2, 0, 1, 5)
        self.bottomLeft.grid.addWidget(self.bottomLeft.saveButton, 3, 0, 1, 2)
        self.bottomLeft.grid.addWidget(self.bottomLeft.statusBar, 3, 2, 1, 3)
        self.bottomLeft.setLayout(self.bottomLeft.grid)
        self.bottomLeft.tree.GetWidget().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.bottomLeft.tree.GetWidget().customContextMenuRequested.connect(self._RightClickOnResultTree)
        self.bottomLeft.tree.GetWidget().clicked.connect(self._ItemSelectedFromResultTree)

    def _SetupConflictTab(self):
        tabHeader = QtGui.QLabel('Conflict Locations')
        self.bottomRight.numberOfConflictsLabel = QtGui.QLabel('')
        tabHeader.setToolTip('Select a conflict to move to location in tree')
        self.bottomRight.useMineButton = QtGui.QPushButton('Use mine')
        self.bottomRight.useMineButton.clicked.connect(self._UseMineButtonClicked)
        self.bottomRight.useBaseButton = QtGui.QPushButton('Use base')
        self.bottomRight.useBaseButton.clicked.connect(self._UseBaseButtonClicked)
        self.bottomRight.useTheirsButton = QtGui.QPushButton('Use theirs')
        self.bottomRight.useTheirsButton.clicked.connect(self._UseTheirsButtonClicked)
        self.bottomRight.conflictList = QtGui.QListWidget()
        self.bottomRight.conflictList.clicked.connect(self._ConflictSelectedFromList)
        self.bottomRight.myConflictTree = TreeViewWidget()
        self.bottomRight.baseConflictTree = TreeViewWidget()
        self.bottomRight.theirConflictTree = TreeViewWidget()
        conflictTabGrid = QtGui.QGridLayout()
        conflictTabGrid.addWidget(tabHeader, 0, 0, 1, 4)
        conflictTabGrid.addWidget(self.bottomRight.numberOfConflictsLabel, 0, 4, 1, 2)
        conflictTabGrid.addWidget(self.bottomRight.conflictList, 1, 0, 1, 6)
        conflictTabGrid.addWidget(self.bottomRight.useMineButton, 2, 0, 1, 2)
        conflictTabGrid.addWidget(self.bottomRight.useBaseButton, 2, 2, 1, 2)
        conflictTabGrid.addWidget(self.bottomRight.useTheirsButton, 2, 4, 1, 2)
        conflictTabGrid.addWidget(self.bottomRight.myConflictTree.GetWidget(), 3, 0, 1, 2)
        conflictTabGrid.addWidget(self.bottomRight.baseConflictTree.GetWidget(), 3, 2, 1, 2)
        conflictTabGrid.addWidget(self.bottomRight.theirConflictTree.GetWidget(), 3, 4, 1, 2)
        self.bottomRight.currentConflict = None
        self._HideSolveConflictButtons()
        return conflictTabGrid

    def _SetupChangesTab(self):
        tabHeader = QtGui.QLabel('Change Locations')
        tabHeader.setToolTip('Select a change to move to location in tree')
        tabDescription = QtGui.QLabel("These are changes that were safely merged and you shouldn't worry about them, but you can review them here")
        self.bottomRight.changeList = QtGui.QListWidget()
        self.bottomRight.changeList.clicked.connect(self._ChangeSelectedFromList)
        self.bottomRight.currentDataTree = TreeViewWidget()
        self.bottomRight.baseDataTree = TreeViewWidget()
        self.bottomRight.currentDataLabel = QtGui.QLabel('')
        baseDataLabel = QtGui.QLabel('Base:')
        changeTabGrid = QtGui.QGridLayout()
        changeTabGrid.addWidget(tabHeader, 0, 0, 1, 2)
        changeTabGrid.addWidget(tabDescription, 1, 0, 1, 2)
        changeTabGrid.addWidget(self.bottomRight.changeList, 2, 0, 1, 2)
        changeTabGrid.addWidget(self.bottomRight.currentDataLabel, 3, 0, 1, 1)
        changeTabGrid.addWidget(baseDataLabel, 3, 1, 1, 1)
        changeTabGrid.addWidget(self.bottomRight.currentDataTree.GetWidget(), 4, 0, 1, 1)
        changeTabGrid.addWidget(self.bottomRight.baseDataTree.GetWidget(), 4, 1, 1, 1)
        return changeTabGrid

    def _SetupBottomRight(self):
        self.bottomRight = QtGui.QFrame(self)
        self.bottomRight.setFrameShape(QtGui.QFrame.StyledPanel)
        self.bottomRight.tabs = QtGui.QTabWidget()
        self.bottomRight.conflictTab = QtGui.QWidget()
        self.bottomRight.changeTab = QtGui.QWidget()
        self.bottomRight.tabs.addTab(self.bottomRight.conflictTab, 'Conflicts')
        self.bottomRight.tabs.addTab(self.bottomRight.changeTab, 'Safe Merge Changes')
        conflictTabGrid = self._SetupConflictTab()
        changeTabGrid = self._SetupChangesTab()
        self.bottomRight.conflictTab.setLayout(conflictTabGrid)
        self.bottomRight.changeTab.setLayout(changeTabGrid)
        self.bottomRight.grid = QtGui.QGridLayout()
        self.bottomRight.grid.addWidget(self.bottomRight.tabs)
        self.bottomRight.setLayout(self.bottomRight.grid)
        self.bottomRight.conflictList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.bottomRight.conflictList.customContextMenuRequested.connect(self._RightClickOnConflictList)
        self.bottomRight.changeList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.bottomRight.changeList.customContextMenuRequested.connect(self._RightClickOnChangeList)

    def _SetupSplitterBetweenBottomLeftAndBottomRight(self):
        self.bottomSplitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        self.bottomSplitter.addWidget(self.bottomLeft)
        self.bottomSplitter.addWidget(self.bottomRight)

    def _SetupSplitterBetweenTopAndBottom(self):
        self.topBottomSplitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.topBottomSplitter.addWidget(self.top)
        self.topBottomSplitter.addWidget(self.bottomSplitter)

    def _SetupConflictMenu(self):
        self.conflictMenu = QtGui.QMenu()
        self.mergeMineAction = self.conflictMenu.addAction('Use Mine')
        self.mergeBaseAction = self.conflictMenu.addAction('Use Base')
        self.mergeTheirsAction = self.conflictMenu.addAction('Use Theirs')

    def _SetupChangeMenu(self):
        self.changeMenu = QtGui.QMenu()
        self.revertBaseAction = self.changeMenu.addAction('Revert to base')
        self.markAcceptedAction = self.changeMenu.addAction('Mark as accepted')

    def _FinalizeWindowLayout(self):
        self.hBox.addWidget(self.topBottomSplitter)
        self.setLayout(self.hBox)

    def _SetWindowDetails(self):
        self.setGeometry(50, 50, 1200, 800)
        self.setWindowTitle('FSD-DiffMerge')
        self.setWindowIcon(QtGui.QIcon('img/octo_logo.png'))
        self.show()

    def InitUI(self):
        self.hBox = QtGui.QHBoxLayout(self)
        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('plastique'))
        self.setStyleSheet(APP_STYLE)
        self._SetupTop()
        self._SetupBottomLeft()
        self._SetupBottomRight()
        self._SetupSplitterBetweenBottomLeftAndBottomRight()
        self._SetupSplitterBetweenTopAndBottom()
        self._SetupConflictMenu()
        self._SetupChangeMenu()
        self._FinalizeWindowLayout()
        self._SetWindowDetails()

    def _LogTime(self, message, start):
        print message, time.time() - start, 'seconds'

    def _UpdateAddsLabel(self):
        if len(self.diffs['added']) > 0:
            self.bottomLeft.numberOfAdds.setText("<font color='#66CC00'>(%s)</font>" % len(self.diffs['added']))
        else:
            self.bottomLeft.numberOfAdds.setText('')

    def SafeMerge(self):
        start = time.time()
        self.uiBase = yaml.load(self.top.base.toPlainText(), Loader=yaml.CSafeLoader)
        self.uiMine = yaml.load(self.top.mine.toPlainText(), Loader=yaml.CSafeLoader)
        self.uiTheirs = yaml.load(self.top.theirs.toPlainText(), Loader=yaml.CSafeLoader)
        self._LogTime('Time spent at yaml.load():', start)
        if self.uiMine is not None and self.uiTheirs is not None:
            if self.uiBase is None:
                self.uiBase = {}
            start = time.time()
            self.merger = FsdDiffMerger(self.uiBase, self.uiMine, self.uiTheirs)
            self.merger.PerformConflictSearch()
            self.merger.PerformSafeMerge()
            self.merger.PerformDifferenceCheck()
            self.conflicts = self.merger.GetConflicts()
            self.mergedDict = self.merger.GetResultData()
            self.diffs = self.merger.GetDifferences()
            self.bottomLeft.undoList = []
            self.UpdateUndoButton()
            self._LogTime('Time spent processing by framework:', start)
            self._ClearConflictTabDiffTrees()
            self.UpdateUI()
            self._UpdateAddsLabel()
            self.top.hide()

    def _ClearConflictTabDiffTrees(self):
        self.bottomRight.myConflictTree.BuildTree({})
        self.bottomRight.baseConflictTree.BuildTree({})
        self.bottomRight.theirConflictTree.BuildTree({})
        self._HideSolveConflictButtons()
        self.bottomRight.currentConflict = None

    def _ClearChangeTabDiffTrees(self):
        self.bottomRight.currentDataTree.BuildTree({})
        self.bottomRight.baseDataTree.BuildTree({})
        self.bottomRight.currentDataLabel.setText('')

    def _FetchNewData(self):
        self.mergedDict = self.merger.GetResultData()
        self._ClearConflictTabDiffTrees()
        self._ClearChangeTabDiffTrees()

    def UpdateUndoButton(self):
        numberOfUndosLeft = len(self.bottomLeft.undoList)
        self.bottomLeft.undoButton.setEnabled(numberOfUndosLeft != 0)
        undoButtonValue = 'Undo'
        if numberOfUndosLeft != 0:
            undoButtonValue += ' (%s)' % numberOfUndosLeft
        self.bottomLeft.undoButton.setText(undoButtonValue)

    def AddToUndoList(self, location, data, originType):
        self.bottomLeft.undoList.append(UndoData(location, data, originType))
        self.UpdateUndoButton()

    def Undo(self):
        if len(self.bottomLeft.undoList) > 0:
            item = self.bottomLeft.undoList.pop(len(self.bottomLeft.undoList) - 1)
            InsertItemToDictionaryAtLocation(self.mergedDict, item.location, item.data)
            if item.IsConflict():
                self.conflicts.append(item.location)
            elif item.IsChange():
                self.diffs['changed'].append(item.location)
            self.GetNewDataAndRefreshUI(item.location)
            self.UpdateUndoButton()
            if item.IsConflict():
                self._DisplayDiffTreesForConflictTab(item.location)
            elif item.IsChange():
                self._DisplayDiffTreesForChangeTab(item.location)

    def AddConflictToUndoList(self, index):
        location = self.conflicts.pop(index)
        data = self.merger.GetObjectAtLocation(self.mergedDict, location)
        self.AddToUndoList(location, data, 'conflict')

    def SolveConflictUsingCorrectVersion(self, conflict, useVersion):
        if useVersion == 0:
            self.merger.SolveConflictUsingMine(conflict)
        elif useVersion == 1:
            self.merger.SolveConflictUsingBase(conflict)
        elif useVersion == 2:
            self.merger.SolveConflictUsingTheirs(conflict)

    def SolveConflict(self, conflict, useVersion):
        index = self._FindIndexOfConflict(conflict)
        if index != -1:
            self.AddConflictToUndoList(index)
            self.SolveConflictUsingCorrectVersion(conflict, useVersion)
            self.UpdateUIForSingleObject(conflict)

    def _RemoveChangeFromChangeList(self, changeLocationKeys):
        for index, diff in enumerate(self.diffs['changed']):
            if AreEqual(diff, changeLocationKeys):
                self.diffs['changed'].pop(index)
                break

    def GetNewDataAndRefreshUI(self, location):
        self._FetchNewData()
        self.UpdateUI()
        self.bottomLeft.tree.ExpandAndMoveTo(location)

    def _AddChangeDataToUndoList(self, location):
        data = self.merger.GetObjectAtLocation(self.mergedDict, location)
        self.AddToUndoList(location, data, 'change')

    def RevertChange(self, location):
        self._AddChangeDataToUndoList(location)
        self.merger.SolveConflictUsingBase(location)
        self._RemoveChangeFromChangeList(location)
        self.UpdateUIForSingleObject(location)

    def KeepChange(self, location):
        self._AddChangeDataToUndoList(location)
        self._RemoveChangeFromChangeList(location)
        self.UpdateUIForSingleObject(location)

    def _DisplayHowManyConflictsExist(self):
        value = '%s conflict%s' % (str(len(self.conflicts)), '' if len(self.conflicts) == 1 else 's')
        self.bottomRight.numberOfConflictsLabel.setText(value)
        if len(self.conflicts) > 0:
            self.bottomLeft.numberOfConflicts.setText("<font color='#ff0000'>(%s)</font>" % len(self.conflicts))
        else:
            self.bottomLeft.numberOfConflicts.setText("<font color='#787878'>(0)</font>")

    def _DisplayHowManyChangesExist(self):
        if len(self.diffs['changed']) > 0:
            self.bottomLeft.numberOfChanges.setText("<font color='#f9e9aa'>(%s)</font>" % len(self.diffs['changed']))
        else:
            self.bottomLeft.numberOfChanges.setText("<font color='#787878'>(0)</font>")

    def _ShowSolveConflictButtons(self):
        self.bottomRight.useMineButton.show()
        self.bottomRight.useBaseButton.show()
        self.bottomRight.useTheirsButton.show()

    def _HideSolveConflictButtons(self):
        self.bottomRight.useMineButton.hide()
        self.bottomRight.useBaseButton.hide()
        self.bottomRight.useTheirsButton.hide()

    def _BuildConflictLists(self):
        self._BuildConflictList()
        self._BuildChangeList()
        self._DisplayHowManyConflictsExist()

    def UpdateUI(self):
        start = time.time()
        self.bottomLeft.tree.BuildTree(self.mergedDict)
        if self.uiBase != {}:
            self.bottomLeft.tree.ColorAddedItems(self.diffs['added'])
        self.bottomLeft.tree.ColorChangedItems(self.diffs['changed'])
        if self.conflicts:
            self.bottomLeft.tree.ColorLocationsInTree(self.conflicts)
        self._BuildConflictLists()
        self._LogTime('Updating the UI took: ', start)

    def _PartsOfListsAreEqual(self, conflict, location):
        for index, key in enumerate(conflict):
            if str(key) != str(location[index]):
                if index > 0:
                    return True
                return False

        return True

    def FindSimilarLists(self, comparingList, searchList):
        itemsFound = []
        for item in searchList:
            if self._PartsOfListsAreEqual(item, comparingList):
                itemsFound.append(item)

        return itemsFound

    def _ColorItemsInPathChanged(self, location):
        self.bottomLeft.tree.ClearPathToItem(location)
        addsFound = self.FindSimilarLists(location, self.diffs['added'])
        self.bottomLeft.tree.ColorAddedItems(addsFound)
        changesFound = self.FindSimilarLists(location, self.diffs['changed'])
        self.bottomLeft.tree.ColorChangedItems(changesFound)
        conflictsFound = self.FindSimilarLists(location, self.conflicts)
        self.bottomLeft.tree.ColorLocationsInTree(conflictsFound)
        self._BuildConflictLists()

    def UpdateUIForSingleObject(self, location):
        dataToInsert = self.merger.GetObjectAtLocation(self.mergedDict, location)
        self.bottomLeft.tree.UpdateSingleItem(dataToInsert)
        self._ColorItemsInPathChanged(location)
        self._ClearChangeTabDiffTrees()
        self._ClearConflictTabDiffTrees()

    def _BuildChangeList(self):
        self.bottomRight.changeList.clear()
        for keyList in self.diffs['changed']:
            item = QtGui.QListWidgetItem(','.join([ str(x) for x in keyList ]))
            self.bottomRight.changeList.addItem(item)

        self._DisplayHowManyChangesExist()

    def _BuildConflictList(self):
        self.bottomRight.conflictList.clear()
        for conflictKeys in self.conflicts:
            item = QtGui.QListWidgetItem(','.join([ str(x) for x in conflictKeys ]))
            self.bottomRight.conflictList.addItem(item)

    def _ColorConflictsInLists(self, diffTreeMerger, conflictBeingChecked, conflicts, otherConflict):
        conflictsToAdd = []
        for conflict in conflicts:
            lastItem = diffTreeMerger.GetObjectAtLocation(conflictBeingChecked, conflict)
            lastItemOther = diffTreeMerger.GetObjectAtLocation(otherConflict, conflict)
            if type(lastItem) is list and type(lastItemOther) is list:
                for index, data in enumerate(lastItem):
                    if len(lastItemOther) > index:
                        if data != lastItemOther[index]:
                            conflictsToAdd.append(conflict + [index])

        return conflictsToAdd

    def _ColorConflictsInDiffTree(self, conflictBeingChecked, otherConflict, originTree):
        diffTreeMerger = FsdDiffMerger({}, conflictBeingChecked, otherConflict)
        diffTreeMerger.PerformConflictSearch()
        conflicts = diffTreeMerger.GetConflicts()
        if conflicts:
            conflictsToAdd = self._ColorConflictsInLists(diffTreeMerger, conflictBeingChecked, conflicts, otherConflict)
            originTree.ColorLocationsInTree(conflicts + conflictsToAdd)
            return conflicts + conflictsToAdd
        return []

    def _AddTooltipDiffs(self, baseConflict, conflicts, otherConflict, originTree):
        diffLocationsWithBaseData = []
        for location in conflicts:
            if baseConflict is None:
                data = self.merger.GetObjectAtLocation(otherConflict, location)
            else:
                data = self.merger.GetObjectAtLocation(baseConflict, location)
            diffLocationsWithBaseData.append((location, data))

        originTree.AddDiffTooltipToLocations(diffLocationsWithBaseData)

    def _ColorDiffTreeOfConflict(self, currentConflict, otherConflict, baseConflict, originTree):
        if type(currentConflict) in (list, dict):
            conflicts = []
            if baseConflict is None:
                conflicts += self._ColorConflictsInDiffTree(currentConflict, otherConflict, originTree)
            elif baseConflict is not None:
                conflicts += self._ColorConflictsInDiffTree(currentConflict, baseConflict, originTree)
            self._AddTooltipDiffs(baseConflict, conflicts, otherConflict, originTree)
        elif baseConflict is None:
            originTree.AddDiffTooltipToLocations([([], otherConflict)])
        else:
            originTree.AddDiffTooltipToLocations([([], baseConflict)])

    def _ColorDiffTreesIfThereAreConflicts(self, baseConflict, myConflict, theirConflict):
        self._ColorDiffTreeOfConflict(myConflict, theirConflict, baseConflict, self.bottomRight.myConflictTree)
        self._ColorDiffTreeOfConflict(theirConflict, myConflict, baseConflict, self.bottomRight.theirConflictTree)
        if type(baseConflict) in (list, dict):
            if myConflict is None:
                self._ColorConflictsInDiffTree(baseConflict, theirConflict, self.bottomRight.baseConflictTree)
            if theirConflict is None:
                self._ColorConflictsInDiffTree(baseConflict, myConflict, self.bottomRight.baseConflictTree)

    def _DisplayDiffInBaseIfItExists(self, baseConflict, columnWidth = -1):
        if baseConflict is not None:
            self.bottomRight.baseConflictTree.BuildTree(baseConflict, columnWidth=columnWidth)
        else:
            self.bottomRight.baseConflictTree.BuildTree(DOES_NOT_EXIST_STRING, columnWidth=columnWidth)

    def _DisplayDiffTreesForConflictTab(self, conflictLocation):
        self.bottomRight.currentConflict = conflictLocation
        self.bottomRight.tabs.setCurrentPage(0)
        myConflict = self.merger.GetObjectAtLocation(self.uiMine, conflictLocation)
        baseConflict = self.merger.GetObjectAtLocation(self.uiBase, conflictLocation)
        theirConflict = self.merger.GetObjectAtLocation(self.uiTheirs, conflictLocation)
        columnWidth = int(0.8 * (self.bottomRight.width() / 3))
        self.bottomRight.myConflictTree.BuildTree(myConflict, columnWidth=columnWidth)
        self._DisplayDiffInBaseIfItExists(baseConflict, columnWidth=columnWidth)
        self.bottomRight.theirConflictTree.BuildTree(theirConflict, columnWidth=columnWidth)
        self._ColorDiffTreesIfThereAreConflicts(baseConflict, myConflict, theirConflict)
        self._ShowSolveConflictButtons()

    def _DisplayDiffTreesForChangeTab(self, location):
        self.bottomRight.tabs.setCurrentPage(1)
        currentData = self.merger.GetObjectAtLocation(self.mergedDict, location)
        baseData = self.merger.GetObjectAtLocation(self.uiBase, location)
        if currentData == self.merger.GetObjectAtLocation(self.uiMine, location):
            self.bottomRight.currentDataLabel.setText('Mine:')
        else:
            self.bottomRight.currentDataLabel.setText('Theirs:')
        columnWidth = int(0.8 * (self.bottomRight.width() / 3))
        self.bottomRight.currentDataTree.BuildTree(currentData, columnWidth=columnWidth)
        self.bottomRight.baseDataTree.BuildTree(baseData, columnWidth=columnWidth)
        merger = FsdDiffMerger({}, currentData, baseData)
        merger.PerformDifferenceCheck(seeAddsInLists=True)
        diffs = merger.GetDifferences()
        self.bottomRight.currentDataTree.ColorAddedItems(diffs['added'])
        self.bottomRight.currentDataTree.ColorLocationsInTree([], baseData)
        self.bottomRight.currentDataTree.AddDiffTooltipToLocations([([], baseData)])

    def _GetChangeByLocation(self, location):
        locationAsStrList = [ str(x) for x in location ]
        for keyList in self.diffs['changed']:
            if AreEqual([ str(x) for x in keyList ], locationAsStrList):
                return keyList

    def TryDisplayChangeByLocation(self, location):
        changeLocation = self._GetChangeByLocation(location)
        if changeLocation is not None:
            self.bottomLeft.tree.ExpandAndMoveTo(changeLocation)
            self._DisplayDiffTreesForChangeTab(changeLocation)
        else:
            self._ClearChangeTabDiffTrees()

    def _ChangeSelectedFromList(self, item):
        changeLocation = item.data(0).split(',')
        self.TryDisplayChangeByLocation(changeLocation)
        self._ClearConflictTabDiffTrees()

    def _ConflictSelectedFromList(self, item):
        conflictLocation = self._GetConflictIfConflicted(item.data(0).split(','))
        self.bottomLeft.tree.ExpandAndMoveTo(conflictLocation)
        self._DisplayDiffTreesForConflictTab(conflictLocation)
        self._ClearChangeTabDiffTrees()

    def _ItemSelectedFromResultTree(self, index):
        item = self.bottomLeft.tree.model.itemFromIndex(index)
        if item is not None:
            keyList = self._GetKeyPathToTreeItem(item)
            conflictLocation = self._GetConflictIfConflicted(keyList)
            if conflictLocation is not None:
                self._DisplayDiffTreesForConflictTab(conflictLocation)
                self._ClearChangeTabDiffTrees()
            else:
                self._ClearConflictTabDiffTrees()
                self.TryDisplayChangeByLocation(keyList)

    def _FindIndexOfConflict(self, conflictLocation):
        conflictAsStr = [ str(x) for x in conflictLocation ]
        for index, conflictKeys in enumerate(self.conflicts):
            currentConflictKeysAsStr = [ str(x) for x in conflictKeys ]
            if AreEqual(currentConflictKeysAsStr, conflictAsStr):
                return index

        return -1

    def _GetConflictIfConflicted(self, keys):
        index = self._FindIndexOfConflict(keys)
        if index != -1:
            return self.conflicts[index]

    def _GetKeyPathToTreeItem(self, item):
        dataList = []
        traverseItem = item
        while traverseItem is not None:
            data = traverseItem.data(0).split(':')
            itemValue = unicodedata.normalize('NFKD', data[0]).encode('ascii', 'ignore')
            dataList.append(itemValue)
            traverseItem = traverseItem.parent()

        return [ x for x in reversed(dataList) ]

    def _SpawnConflictMenu(self, conflict, pos, origin):
        action = self.conflictMenu.exec_(origin.mapToGlobal(pos))
        if action == self.mergeMineAction:
            self.SolveConflict(conflict, 0)
        elif action == self.mergeBaseAction:
            self.SolveConflict(conflict, 1)
        elif action == self.mergeTheirsAction:
            self.SolveConflict(conflict, 2)

    def _SpawnChangeMenu(self, location, pos, origin):
        action = self.changeMenu.exec_(origin.mapToGlobal(pos))
        if action == self.revertBaseAction:
            self.RevertChange(location)
        elif action == self.markAcceptedAction:
            self.KeepChange(location)

    def _GetLocationAndSolveConflictBy(self, conflictLocation, version):
        self.SolveConflict(conflictLocation, version)

    def _UseMineButtonClicked(self):
        if self.bottomRight.currentConflict is not None:
            self._GetLocationAndSolveConflictBy(self.bottomRight.currentConflict, 0)

    def _UseBaseButtonClicked(self):
        if self.bottomRight.currentConflict is not None:
            self._GetLocationAndSolveConflictBy(self.bottomRight.currentConflict, 1)

    def _UseTheirsButtonClicked(self):
        if self.bottomRight.currentConflict is not None:
            self._GetLocationAndSolveConflictBy(self.bottomRight.currentConflict, 2)

    def _RightClickOnResultTree(self, pos):
        index = self.bottomLeft.tree.GetWidget().indexAt(pos)
        item = self.bottomLeft.tree.model.itemFromIndex(index)
        if item is not None:
            keyList = self._GetKeyPathToTreeItem(item)
            conflictLocation = self._GetConflictIfConflicted(keyList)
            if conflictLocation is not None:
                self._SpawnConflictMenu(conflictLocation, pos, self.bottomLeft.tree.GetWidget())
            else:
                changeLocation = self._GetChangeByLocation(keyList)
                if changeLocation is not None:
                    self._SpawnChangeMenu(changeLocation, pos, self.bottomLeft.tree.GetWidget())

    def _RightClickOnConflictList(self, pos):
        item = self.bottomRight.conflictList.indexAt(pos)
        if item.data(0) is not None:
            conflictLocation = self._GetConflictIfConflicted(item.data(0).split(','))
            if conflictLocation is not None:
                self._SpawnConflictMenu(conflictLocation, pos, self.bottomRight.conflictList)

    def _RightClickOnChangeList(self, pos):
        item = self.bottomRight.changeList.indexAt(pos)
        if item.data(0) is not None:
            changeLocation = self._GetChangeByLocation(item.data(0).split(','))
            if changeLocation is not None:
                self._SpawnChangeMenu(changeLocation, pos, self.bottomRight.changeList)

    def _ClearStatusBar(self):
        self.bottomLeft.statusBar.showMessage('')

    def _DisplayStatusBarMessage(self, message, waitSeconds):
        self.bottomLeft.statusBar.showMessage(message)
        CountDownThread(waitSeconds, self._ClearStatusBar).start()

    def _SaveResultToFile(self):
        with open(self.resultFile, 'w') as f:
            yaml.dump(self.mergedDict, f, allow_unicode=True, Dumper=FsdYamlDumper, default_flow_style=False)
            self._DisplayStatusBarMessage('Saved successfully', 3)

    def _ResultFileStringIsEmpty(self):
        return self.resultFile == u''

    def LoadFileToMine(self):
        self.LoadFile(self.top.mine)

    def LoadFileToBase(self):
        self.LoadFile(self.top.base)

    def LoadFileToTheirs(self):
        self.LoadFile(self.top.theirs)

    def LoadFile(self, target):
        chosenFile = QtGui.QFileDialog.getOpenFileName(self)[0]
        if chosenFile != u'':
            self.LoadArgument(chosenFile, target)

    def Save(self):
        if self.resultFile is not None:
            if self._ResultFileStringIsEmpty():
                self.resultFile = None
            else:
                if len(self.conflicts) != 0:
                    message = 'There are still conflicts to be resolved, do you wish to save?'
                    reply = QtGui.QMessageBox.question(self, 'Message', message, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                    if reply != QtGui.QMessageBox.Yes:
                        return
                self._SaveResultToFile()
        elif self.resultFile is None:
            self.resultFile = QtGui.QFileDialog.getSaveFileName(self)[0]
            self.Save()


class UndoData(object):

    def __init__(self, location, data, originType):
        self.location = location
        self.data = data
        self.originType = 0 if originType == 'conflict' else 1

    def IsConflict(self):
        return self.originType == 0

    def IsChange(self):
        return self.originType == 1


class CountDownThread(threading.Thread):

    def __init__(self, durationInSeconds, endOfDurationCallback):
        threading.Thread.__init__(self)
        self.durationInSeconds = durationInSeconds
        self.callBack = endOfDurationCallback
        self.startTime = time.time()

    def run(self):
        while time.time() - self.startTime < self.durationInSeconds:
            pass

        self.callBack()


APP_STYLE = '\nQToolTip {\n     border: 1px solid black;\n     background-color: #222;\n     border-radius: 3px;\n     color: #fff;\n     opacity: 100;\n}\n\nQWidget {\n    color: #b1b1b1;\n    background-color: #323232;\n}\n\nQWidget:pressed {\n    border: 1px solid #d7801a;\n    background: none;\n}\n\nQWidget:item:hover {\n    font-weight: bold;\n}\n\nQMenuBar::item {\n    background: transparent;\n}\n\nQMenuBar::item:selected {\n    background: transparent;\n    border: 1px solid #ffaa00;\n}\n\nQMenuBar::item:pressed {\n    background: #444;\n    border: 1px solid #000;\n    background-color: QLinearGradient(\n        x1:0, y1:0,\n        x2:0, y2:1,\n        stop:1 #212121,\n        stop:0.4 #343434/*,\n        stop:0.2 #343434,\n        stop:0.1 #ffaa00*/\n    );\n    margin-bottom:-1px;\n    padding-bottom:1px;\n}\n\nQMenu {\n    border: 1px solid #000;\n}\n\nQMenu::item {\n    padding: 2px 20px 2px 20px;\n}\n\nQMenu::item:selected {\n\n}\n\nQWidget:disabled {\n    color: #404040;\n    background-color: #323232;\n}\n\nQAbstractItemView {\n    background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #4d4d4d, stop: 0.1 #646464, stop: 1 #5d5d5d);\n}\n\nQWidget:focus {\n    /*border: 2px solid QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffa02f, stop: 1 #d7801a);*/\n}\n\nQLineEdit {\n    background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #4d4d4d, stop: 0 #646464, stop: 1 #5d5d5d);\n    padding: 1px;\n    border-style: solid;\n    border: 1px solid #1e1e1e;\n    border-radius: 5;\n}\n\nQPushButton {\n    color: #b1b1b1;\n    background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #565656, stop: 0.1 #525252, stop: 0.5 #4e4e4e, stop: 0.9 #4a4a4a, stop: 1 #464646);\n    border-width: 1px;\n    border-color: #1e1e1e;\n    border-style: solid;\n    border-radius: 6;\n    padding: 3px;\n    font-size: 12px;\n    padding-left: 5px;\n    padding-right: 5px;\n}\n\nQPushButton:pressed {\n    background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #2d2d2d, stop: 0.1 #2b2b2b, stop: 0.5 #292929, stop: 0.9 #282828, stop: 1 #252525);\n}\n\nQComboBox {\n    selection-background-color: #ffaa00;\n    background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #565656, stop: 0.1 #525252, stop: 0.5 #4e4e4e, stop: 0.9 #4a4a4a, stop: 1 #464646);\n    border-style: solid;\n    border: 1px solid #1e1e1e;\n    border-radius: 5;\n}\n\nQComboBox:hover,QPushButton:hover {\n    border: 2px solid QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffa02f, stop: 1 #d7801a);\n}\n\n\nQComboBox:on {\n    padding-top: 3px;\n    padding-left: 4px;\n    background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #2d2d2d, stop: 0.1 #2b2b2b, stop: 0.5 #292929, stop: 0.9 #282828, stop: 1 #252525);\n    selection-background-color: #ffaa00;\n}\n\nQComboBox QAbstractItemView {\n    border: 2px solid darkgray;\n    selection-background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffa02f, stop: 1 #d7801a);\n}\n\nQComboBox::drop-down {\n     subcontrol-origin: padding;\n     subcontrol-position: top right;\n     width: 15px;\n\n     border-left-width: 0px;\n     border-left-color: darkgray;\n     border-left-style: solid; /* just a single line */\n     border-top-right-radius: 3px; /* same radius as the QComboBox */\n     border-bottom-right-radius: 3px;\n }\n\nQComboBox::down-arrow {\n     image: url(:/down_arrow.png);\n}\n\nQGroupBox:focus {\nborder: 2px solid QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffa02f, stop: 1 #d7801a);\n}\n\nQTextEdit:focus {\n    border: 2px solid QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffa02f, stop: 1 #d7801a);\n}\n\nQScrollBar:horizontal {\n     border: 1px solid #222222;\n     background: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0.0 #121212, stop: 0.2 #282828, stop: 1 #484848);\n     height: 7px;\n     margin: 0px 16px 0 16px;\n}\n\nQScrollBar::handle:horizontal {\n      background: QLinearGradient( x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #ffa02f, stop: 0.5 #d7801a, stop: 1 #ffa02f);\n      min-height: 20px;\n      border-radius: 2px;\n}\n\nQScrollBar::add-line:horizontal {\n      border: 1px solid #1b1b19;\n      border-radius: 2px;\n      background: QLinearGradient( x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #ffa02f, stop: 1 #d7801a);\n      width: 14px;\n      subcontrol-position: right;\n      subcontrol-origin: margin;\n}\n\nQScrollBar::sub-line:horizontal {\n      border: 1px solid #1b1b19;\n      border-radius: 2px;\n      background: QLinearGradient( x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #ffa02f, stop: 1 #d7801a);\n      width: 14px;\n     subcontrol-position: left;\n     subcontrol-origin: margin;\n}\n\nQScrollBar::right-arrow:horizontal, QScrollBar::left-arrow:horizontal {\n      border: 1px solid black;\n      width: 1px;\n      height: 1px;\n      background: white;\n}\n\nQScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {\n      background: none;\n}\n\nQScrollBar:vertical {\n      background: QLinearGradient( x1: 0, y1: 0, x2: 1, y2: 0, stop: 0.0 #121212, stop: 0.2 #282828, stop: 1 #484848);\n      width: 7px;\n      margin: 16px 0 16px 0;\n      border: 1px solid #222222;\n}\n\nQScrollBar::handle:vertical {\n      background: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffa02f, stop: 0.5 #d7801a, stop: 1 #ffa02f);\n      min-height: 20px;\n      border-radius: 2px;\n}\n\nQScrollBar::add-line:vertical {\n      border: 1px solid #1b1b19;\n      border-radius: 2px;\n      background: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffa02f, stop: 1 #d7801a);\n      height: 14px;\n      subcontrol-position: bottom;\n      subcontrol-origin: margin;\n}\n\nQScrollBar::sub-line:vertical {\n      border: 1px solid #1b1b19;\n      border-radius: 2px;\n      background: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #d7801a, stop: 1 #ffa02f);\n      height: 14px;\n      subcontrol-position: top;\n      subcontrol-origin: margin;\n}\n\nQScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {\n      border: 1px solid black;\n      width: 1px;\n      height: 1px;\n      background: white;\n}\n\n\nQScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {\n      background: none;\n}\n\nQTextEdit {\n    background-color: #242424;\n}\n\nQPlainTextEdit {\n    background-color: #242424;\n}\n\nQHeaderView::section {\n    background-color: QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:0 #616161, stop: 0.5 #505050, stop: 0.6 #434343, stop:1 #656565);\n    color: white;\n    padding-left: 4px;\n    border: 1px solid #6c6c6c;\n}\n\nQCheckBox:disabled {\ncolor: #414141;\n}\n\nQDockWidget::title {\n    text-align: center;\n    spacing: 3px; /* spacing between items in the tool bar */\n    background-color: QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:0 #323232, stop: 0.5 #242424, stop:1 #323232);\n}\n\nQDockWidget::close-button, QDockWidget::float-button {\n    text-align: center;\n    spacing: 1px; /* spacing between items in the tool bar */\n    background-color: QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:0 #323232, stop: 0.5 #242424, stop:1 #323232);\n}\n\nQDockWidget::close-button:hover, QDockWidget::float-button:hover {\n    background: #242424;\n}\n\nQDockWidget::close-button:pressed, QDockWidget::float-button:pressed {\n    padding: 1px -1px -1px 1px;\n}\n\nQMainWindow::separator {\n    background-color: QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:0 #161616, stop: 0.5 #151515, stop: 0.6 #212121, stop:1 #343434);\n    color: white;\n    padding-left: 4px;\n    border: 1px solid #4c4c4c;\n    spacing: 3px; /* spacing between items in the tool bar */\n}\n\nQMainWindow::separator:hover {\n\n    background-color: QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:0 #d7801a, stop:0.5 #b56c17 stop:1 #ffa02f);\n    color: white;\n    padding-left: 4px;\n    border: 1px solid #6c6c6c;\n    spacing: 3px; /* spacing between items in the tool bar */\n}\n\nQToolBar::handle {\n     spacing: 3px; /* spacing between items in the tool bar */\n     background: url(:/images/handle.png);\n}\n\nQMenu::separator {\n    height: 2px;\n    background-color: QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:0 #161616, stop: 0.5 #151515, stop: 0.6 #212121, stop:1 #343434);\n    color: white;\n    padding-left: 4px;\n    margin-left: 10px;\n    margin-right: 5px;\n}\n\nQProgressBar {\n    border: 2px solid grey;\n    border-radius: 5px;\n    text-align: center;\n}\n\nQProgressBar::chunk {\n    background-color: #d7801a;\n    width: 2.15px;\n    margin: 0.5px;\n}\n\nQTabBar::tab {\n    color: #b1b1b1;\n    border: 1px solid #444;\n    border-bottom-style: none;\n    background-color: #323232;\n    padding-left: 10px;\n    padding-right: 10px;\n    padding-top: 3px;\n    padding-bottom: 2px;\n    margin-right: -1px;\n}\n\nQTabWidget::pane {\n    border: 1px solid #444;\n    top: 1px;\n}\n\nQTabBar::tab:last {\n    margin-right: 0; /* the last selected tab has nothing to overlap with on the right */\n    border-top-right-radius: 3px;\n}\n\nQTabBar::tab:first:!selected {\n margin-left: 0px; /* the last selected tab has nothing to overlap with on the right */\n\n\n    border-top-left-radius: 3px;\n}\n\nQTabBar::tab:!selected {\n    color: #b1b1b1;\n    border-bottom-style: solid;\n    margin-top: 3px;\n    background-color: QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:1 #212121, stop:.4 #343434);\n}\n\nQTabBar::tab:selected {\n    border-top-left-radius: 3px;\n    border-top-right-radius: 3px;\n    margin-bottom: 0px;\n}\n\nQTabBar::tab:!selected:hover {\n    /*border-top: 2px solid #ffaa00;\n    padding-bottom: 3px;*/\n    border-top-left-radius: 3px;\n    border-top-right-radius: 3px;\n    background-color: QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:1 #212121, stop:0.4 #343434, stop:0.2 #343434, stop:0.1 #ffaa00);\n}\n\nQRadioButton::indicator:checked, QRadioButton::indicator:unchecked {\n    color: #b1b1b1;\n    background-color: #323232;\n    border: 1px solid #b1b1b1;\n    border-radius: 6px;\n}\n\nQRadioButton::indicator:checked {\n    background-color: qradialgradient(\n        cx: 0.5, cy: 0.5,\n        fx: 0.5, fy: 0.5,\n        radius: 1.0,\n        stop: 0.25 #ffaa00,\n        stop: 0.3 #323232\n    );\n}\n\nQCheckBox::indicator {\n    color: #b1b1b1;\n    background-color: #323232;\n    border: 1px solid #b1b1b1;\n    width: 9px;\n    height: 9px;\n}\n\nQRadioButton::indicator{\n    border-radius: 6px;\n}\n\nQRadioButton::indicator:hover, QCheckBox::indicator:hover{\n    border: 1px solid #ffaa00;\n}\n\nQCheckBox::indicator:checked{\n    image:url(:/images/checkbox.png);\n}\n\nQCheckBox::indicator:disabled, QRadioButton::indicator:disabled{\n    border: 1px solid #444;\n}\n\nQTreeView {\n\n}\nQTreeView::item {\n    background: none;\n}\nQTreeView::item:selected {\n    background-color: transparent;\n}\nQTreeView::item:selected:active {\n    background-color: transparent;\n    border: none;\n}\nQTreeView::item:focus {\n    border: none;\n    background-color: transparent;\n}\nQTreeView::branch {\n    background: none;\n}\nQListWidget::item:selected {\n    background-color: transparent;\n}\nQListWidget::item:selected:active {\n    background-color: transparent;\n}\nQWidget::item:selected {\n    background: none;\n}\n\n'

def main():
    app = QtGui.QApplication(sys.argv)
    ex = FsdDiffMergeUI(sys.argv[1:])
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
