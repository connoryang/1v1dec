#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\fsd\diffMergeTool\treeview.py
from PySide import QtGui, QtCore
from PySide.QtGui import QStandardItemModel
from PySide.QtGui import QStandardItem
from PySide.QtCore import Qt
import difflib

class TreeViewWidget:

    def __init__(self):
        self.tree = QtGui.QTreeView()
        self.keys = {}
        self.data = None
        self.model = QStandardItemModel()
        self.tree.setHeaderHidden(True)
        self.brushConflictInChild = QtGui.QBrush(QtGui.QColor(255, 136, 139))
        self.brushConflictInChild.setStyle(QtCore.Qt.SolidPattern)
        self.brushConflictInItem = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        self.brushConflictInItem.setStyle(Qt.SolidPattern)
        self.brushChangedItem = QtGui.QBrush(QtGui.QColor(249, 233, 170))
        self.brushChangedItem.setStyle(Qt.SolidPattern)
        self.brushAddedItem = QtGui.QBrush(QtGui.QColor(221, 252, 199))
        self.brushAddedItem.setStyle(Qt.SolidPattern)
        self.whiteBrush = QtGui.QBrush(QtGui.QColor(177, 177, 177))
        self.whiteBrush.setStyle(Qt.SolidPattern)

    def _GetStyleSheet(self):
        return '\n\n                QTreeView {\n\n                }\n                QTreeView::item {\n                    background: none;\n                }\n                QTreeView::item:selected {\n                    background: none;\n                }\n                QTreeView::item:selected:active {\n                    background: none;\n                }\n                QTreeView::item:focus\n                {\n                    background: none;\n                }\n                QTreeView::branch {\n                    background: none;\n                }\n                QListWidget::item:selected {\n                    background: none;\n                }\n                QListWidget::item:selected:active {\n                    background: none;\n                }\n                QWidget::item:selected {\n                    background: none;\n                }\n\n               '

    def _WrapWord(self, columnWidth, value):
        valueAsList = list(value)
        currentIndex = 0
        doInsert = False
        for i in range(0, len(valueAsList)):
            if currentIndex * 7 > columnWidth and i > 0:
                doInsert = True
                currentIndex = 0
            currentIndex += 1
            if doInsert and valueAsList[i] == ' ':
                valueAsList[i] = '\n'
                doInsert = False

        value = ''.join(valueAsList)
        return value

    def BuildTree(self, data, columnWidth = 0):
        self.model = QStandardItemModel()
        self.data = data
        self.AddItems(self.model, data, columnWidth=columnWidth)
        self.tree.setModel(self.model)

    def ClearPathToItem(self, location):
        self.ColorItemInLocation(location, self.whiteBrush)

    def UpdateSingleItem(self, data):
        itemIndex = self.tree.selectedIndexes()[0]
        item = self.model.itemFromIndex(itemIndex)
        if item is not None:
            if data is not None:
                item.removeRows(0, item.rowCount())
                itemData = item.data(0).split(': ')
                if type(data) in (dict, list):
                    item.setText(itemData[0])
                    self.AddItems(item, data)
                else:
                    if type(data) is unicode:
                        dataValue = data
                    else:
                        dataValue = str(data)
                    item.setText(itemData[0] + ': ' + dataValue)
            elif item.parent() is None:
                self.model.removeRow(itemIndex.row())
            else:
                item.parent().removeRow(itemIndex.row())

    def ConvertDataToString(self, data):
        value = ''
        if type(data) not in (list, dict):
            if type(data) is unicode:
                value = data
            elif data is None:
                value = '(DELETED)'
            else:
                value = str(data)
        return value

    def _MakeItemUneditable(self, item):
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)

    def _AddDictToTree(self, data, parent, columnWidth = 0):
        sortedKeys = sorted(data.keys())
        for key in sortedKeys:
            value = self.ConvertDataToString(data[key])
            if value == '':
                item = QStandardItem(str(key))
            else:
                item = QStandardItem(str(key) + ': ' + value)
                if len(value) > 10:
                    item.setToolTip(value)
            self._MakeItemUneditable(item)
            parent.appendRow(item)
            if type(data[key]) in (dict, list):
                self.AddItems(item, data[key], columnWidth=columnWidth)

    def _AddListToTree(self, data, parent):
        for attribute in data:
            item = QStandardItem(str(attribute))
            self._MakeItemUneditable(item)
            parent.appendRow(item)

    def _AddPrimitiveToTree(self, data, parent, columnWidth = 0):
        if type(data) in (str, unicode):
            value = self._WrapWord(columnWidth, data)
        else:
            value = self.ConvertDataToString(data)
        item = QStandardItem(value)
        self._MakeItemUneditable(item)
        parent.appendRow(item)

    def AddItems(self, parent, data, columnWidth = 0):
        if type(data) is dict:
            self._AddDictToTree(data, parent, columnWidth=columnWidth)
        elif type(data) is list:
            self._AddListToTree(data, parent)
        else:
            self._AddPrimitiveToTree(data, parent, columnWidth=columnWidth)

    def _BinarySearchKeys(self, keys, key, currentMin, currentMax):
        while currentMax >= currentMin:
            mid = currentMin + (currentMax - currentMin) / 2
            if keys[mid] < key:
                currentMin = mid + 1
            elif keys[mid] > key:
                currentMax = mid - 1
            else:
                return mid

        return -1

    def _FindIndexOfKey(self, currentData, key):
        if type(currentData) is dict:
            sortedKeys = sorted(currentData.keys())
            return self._BinarySearchKeys(sortedKeys, key, 0, len(sortedKeys) - 1)
        else:
            for index, data in enumerate(currentData):
                if index == key:
                    return key

            return -1

    def _GetNextRoot(self, index, root):
        if root is None:
            root = self.model.index(index, 0)
        else:
            root = root.child(index, 0)
        return root

    def _GetChildDataByKey(self, currentData, key):
        if type(currentData) is dict:
            return currentData.get(key, None)
        else:
            return key + 1

    def ColorItem(self, item, brush):
        item.setData(QtGui.QBrush(QtGui.QColor(brush.color())), Qt.ForegroundRole)

    def ColorItemInLocation(self, location, brush):
        root = None
        currentData = self.data
        for key in location:
            index = self._FindIndexOfKey(currentData, key)
            root = self._GetNextRoot(index, root)
            if root is not None:
                item = self.model.itemFromIndex(root)
                if item is not None:
                    self.ColorItem(item, brush)
            else:
                break
            currentData = self._GetChildDataByKey(currentData, key)

    def ColorAddedItems(self, locations):
        for location in locations:
            self.ColorItemInLocation(location, self.brushAddedItem)

    def ColorChangedItems(self, locations):
        for location in locations:
            self.ColorItemInLocation(location, self.brushChangedItem)

    def _ColorText(self, data, color):
        return "<b><font style='font-size: 14px; color: " + color + ";'>" + data + '</font></b>'

    def _DiffTreeDataIsValid(self, data):
        if data is None:
            return False
        if data == '(DELETED)':
            return False
        if data == '(DOES NOT EXIST)':
            return False
        return True

    def _AddDiffInfoAsTooltipForItem(self, item, itemData, base):
        result = ''
        if self._DiffTreeDataIsValid(itemData) and self._DiffTreeDataIsValid(base):
            if not item.hasChildren():
                if ':' in itemData:
                    diffTreeData = itemData.split(':')[1]
                else:
                    diffTreeData = itemData
            else:
                diffTreeData = itemData
            diffBaseData = base
            if type(itemData) is not unicode:
                diffTreeData = str(diffTreeData)
            if type(base) is not unicode:
                diffBaseData = str(diffBaseData)
            for diff in difflib.ndiff(diffTreeData, diffBaseData):
                if diff.startswith('- '):
                    result += self._ColorText(diff.split('- ')[1], '#00ff00')
                elif diff.startswith('+ '):
                    result += self._ColorText(diff.split('+ ')[1], '#ff0000')
                else:
                    result += diff.split('  ')[1]

            item.setToolTip(result)

    def _FindItemByLocation(self, location):
        root = None
        currentData = self.data
        item = None
        for key in location:
            index = self._FindIndexOfKey(currentData, key)
            root = self._GetNextRoot(index, root)
            if root is not None:
                item = self.model.itemFromIndex(root)
            currentData = self._GetChildDataByKey(currentData, key)

        return item

    def AddDiffTooltipToLocations(self, locations):
        for data in locations:
            location = data[0]
            baseData = data[1]
            item = self._FindItemByLocation(location)
            if item is None:
                item = self.model.itemFromIndex(self.model.index(0, 0))
            if type(baseData) is list:
                lastItemIndex = 0
                if len(location) > 0:
                    lastItemIndex = len(location) - 1
                self._AddDiffInfoAsTooltipForItem(item, item.data(lastItemIndex), baseData[lastItemIndex])
            else:
                self._AddDiffInfoAsTooltipForItem(item, item.data(0), baseData)

    def _ColorLocationWithKeys(self, finalKey, keys):
        root = None
        currentData = self.data
        for key in keys:
            index = self._FindIndexOfKey(currentData, key)
            root = self._GetNextRoot(index, root)
            if root is not None:
                try:
                    item = self.model.itemFromIndex(root)
                    if key == finalKey:
                        brush = self.brushConflictInItem
                    else:
                        brush = self.brushConflictInChild
                    self.ColorItem(item, brush)
                except AttributeError:
                    pass

            else:
                break
            currentData = self._GetChildDataByKey(currentData, key)

    def ColorLocationsInTree(self, conflicts, base = None):
        if self.data is not None:
            for keys in conflicts:
                try:
                    finalKey = keys[-1]
                except IndexError:
                    continue

                self._ColorLocationWithKeys(finalKey, keys)

    def ExpandAndMoveTo(self, keys):
        if self.data is not None:
            root = None
            currentData = self.data
            for key in keys:
                if currentData is not None:
                    index = self._FindIndexOfKey(currentData, key)
                    root = self._GetNextRoot(index, root)
                    self.tree.setExpanded(root, True)
                    currentData = currentData.get(key, None)

            if root is not None:
                self.tree.setCurrentIndex(root)

    def GetWidget(self):
        return self.tree
