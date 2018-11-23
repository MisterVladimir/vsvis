# -*- coding: utf-8 -*-
"""
@author: Vladimir Shteyn
@email: vladimir.shteyn@googlemail.com

Copyright Vladimir Shteyn, 2018

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import pickle
import numpy as np
from anytree import Node, PreOrderIter
from io import BytesIO
from PyQt5 import QtCore
from collections import namedtuple
from itertools import count
from collections import OrderedDict
from pandas import DataFrame
from qtpandas.models.DataFrameModel import DataFrameModel as _DataFrameModel
from typing import Optional, Union

NodeInfo = namedtuple('NodeInfo', ['name', 'path'])


class NodeTreeModel(QtCore.QAbstractItemModel):
    def __init__(self, root, parent=None):
        super().__init__(parent)
        self.root = root

    def get_node(self, index):
        if index.isValid():
            # print('internal pointer: {}'.format(index.internalPointer()))
            return index.internalPointer()
        else:
            return self.root

    def rowCount(self, parent):
        """
        Parameters
        ------------
        parent : QtCore.QModelIndex
            Index of parent item.

        Returns
        -----------
        int : number of children in parent
        """
        if not parent.isValid():
            parentNode = self.root
        else:
            parentNode = parent.internalPointer()

        return len(parentNode.children)

    def columnCount(self, parent):
        return 1

    def parent(self, index):
        node = self.get_node(index)
        parent_node = node.parent
        if parent_node == self.root:
            return QtCore.QModelIndex()
        else:
            return self.createIndex(parent_node.row, 0, parent_node)

    def data(self, index: QtCore.QModelIndex, role: int) -> Union[str, None]:
        if not index.isValid():
            return None
        node = index.internalPointer()

        if role == QtCore.Qt.DisplayRole:
            return node.name

    def flags(self, index: QtCore.QModelIndex):
        if index.isValid():
            return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
        else:
            return QtCore.Qt.NoItemFlags

    def index(self, row: int, column: int, parent: QtCore.QModelIndex) -> QtCore.QModelIndex:
        """
        Returns an index at the given row, column of the parent.

        Parameters
        ------------
        row : int
        column : int
        parent : QtCore.QModelIndex
        """
        parentNode = self.get_node(parent)

        childItem = parentNode.children[row]

        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()


class DraggableTreeModel(NodeTreeModel):
    def __init__(self, root, parent=None):
        super().__init__(root, parent)

    def _encode_nodes(self, *nodes: Node) -> QtCore.QMimeData:
        # namedtuple masquerading as Node with the relevant info
        node_info = [NodeInfo(node.name, node.path) for node in nodes]
        byte = BytesIO()
        pickle.dump(node_info, byte)
        byte.seek(0)
        qbyte = QtCore.QByteArray(byte.read())
        mime = QtCore.QMimeData()
        mime.setData('application/node', qbyte)
        return mime

    def flags(self, index: QtCore.QModelIndex):
        default = super().flags(index)
        if index.isValid():
            return default | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled
        else:
            return default

    def mimeTypes(self):
        return ['application/node']

    def mimeData(self, indices) -> QtCore.QMimeData:
        nodes = [self.get_node(index) for index in indices]
        return self._encode_nodes(*nodes)


class DataFrameModel(_DataFrameModel):
    def __init__(self, dataframe=None, copy=True):
        super().__init__(dataframe, copy)
        if dataframe is not None:
            self.enableEditing()

    def clear(self):
        """
        Remove all data from model except for column names.
        """
        if not self.editable:
            return False

        cols = self._dataFrame.columns
        nrows = self._dataFrame.shape[0]
        self.beginRemoveRows(QtCore.QModelIndex(), 0, nrows)
        self._dataFrame = DataFrame(columns=cols)
        self.endRemoveRows()
        return True


class ItemInfoTableModel(DataFrameModel):
    """
    """
    def __init__(self, source_selection_model, source_model, columns):
        self._column_to_attribute = \
            OrderedDict(zip(['Path', 'Name'], ['directory', 'name']))
        self._column_to_attribute.update(columns)

        super().__init__(DataFrame(columns=self._column_to_attribute.keys()))

        self.source_selection_model = source_selection_model
        self.source_model = source_model
        self.source_selection_model.selectionChanged[
            QtCore.QItemSelection, QtCore.QItemSelection].connect(
                lambda i, j: self.selection_changed(i, j))

    def selection_changed(self, selected, deselected):
        def filter_indices(indices):
            nodes = (self.source_model.get_node(index) for index in indices)
            mask = [hasattr(n, 'directory') for n in nodes]
            indices = list(np.array(indices)[mask])
            return indices

        def get_rows(indices):
            nodes = (self.source_model.get_node(index) for index in indices)
            paths = [n.directory for n in nodes]
            mask = np.isin(self._dataFrame['Path'], paths)
            return self._dataFrame.index[mask].values

        def get_data(indices):
            columns = self._dataFrame.columns
            nodes = (self.source_model.get_node(index) for index in indices)
            data = [[str(getattr(node, self._column_to_attribute[c])) for c in columns] for node in nodes]

            return data

        selected = filter_indices(selected.indexes())
        deselected = filter_indices(deselected.indexes())

        dif = len(selected) - len(deselected)

        if dif > 0:
            self.addDataFrameRows(dif)
        elif dif < 0:
            rows = get_rows(deselected[-abs(dif):])
            deselected = deselected[-abs(dif):]
            self.removeDataFrameRows(rows)

        # at this point all we need to do is replace
        if len(deselected) > 0:
            rows = get_rows(deselected)
            data = get_data(selected[:len(deselected)])
            self._dataFrame.iloc[rows, :] = data
            selected = selected[len(deselected):]
        if len(selected) > 0:
            data = get_data(selected)
            self._dataFrame.iloc[-abs(dif):, :] = data

        self.layoutChanged.emit()
        self._dataFrame.reset_index(drop=True, inplace=True)
        return True
        # adding selected indices


class ListModel(DataFrameModel):
    def headerData(self, *args):
        return None

    def supportedDropActions(self):
        return QtCore.Qt.CopyAction

    def data(self, index, role=QtCore.Qt.DisplayRole):
        roles = (QtCore.Qt.DisplayRole,
                 QtCore.Qt.EditRole,
                 QtCore.Qt.CheckStateRole)

        if role in roles and index.column() > 1:
            return None
        else:
            return super().data(index, role)


class DroppableListModel(ListModel):
    """
    """
    item_dropped = QtCore.pyqtSignal()

    def __init__(self, dataframe: Optional[DataFrame] = None,
                 copy: bool = False):
        super().__init__(dataframe, copy)

    def _parse_dropped_data(self, byte):
        readable = BytesIO(byte.data('application/node'))
        return pickle.load(readable)

    def flags(self, index: QtCore.QModelIndex):
        default = super().flags(index)
        return default | QtCore.Qt.ItemIsDropEnabled

    def mimeTypes(self):
        return ['application/node']

    def supportedDropActions(self):
        return QtCore.Qt.CopyAction

    def canDropMimeData(self, data: QtCore.QMimeData, *args):
        if any([data.hasFormat(typ) for typ in self.mimeTypes()]):
            return True
        else:
            return False

    def dropMimeData(self, data, action, *args):
        if not self.canDropMimeData(data):
            return False
        elif action == QtCore.Qt.IgnoreAction:
            return True
        elif action == QtCore.Qt.CopyAction:
            begin_row = self.rowCount(QtCore.QModelIndex())
            # parsed is a named tuple whose items are the string displayed
            # in the list, and the path to the data in the HDF5 file
            parsed = self._parse_dropped_data(data)
            if not self.addDataFrameRows(len(parsed)):
                # BUG: need to remove extraneous rows
                return False

            for r, tup in zip(count(begin_row), parsed):
                name_index = self.index(r, 0, QtCore.QModelIndex())
                self.setData(name_index, tup.name)
                path_index = self.index(r, 1, QtCore.QModelIndex())
                self.setData(path_index, tup.path)

            self.item_dropped.emit()
            return True

        else:
            return False
