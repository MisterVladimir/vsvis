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
import pandas as pd
from anytree import Node, PreOrderIter
from io import BytesIO
from qtpy import QtCore
from collections import namedtuple
from itertools import count
from collections import OrderedDict
from typing import Optional, Union, Sequence
from ordered_set import OrderedSet


from .contrib.qtpandas.models import DataFrameModel as _DataFrameModel

# NodeInfo = namedtuple('NodeInfo', ['name', 'path'])


class NodeTreeModel(QtCore.QAbstractItemModel):
    def __init__(self, root: Node, parent: QtCore.QObject = None):
        super().__init__(parent)
        self.root = root

    def get_node(self, index: QtCore.QModelIndex):
        if index.isValid():
            # print('internal pointer: {}'.format(index.internalPointer()))
            return index.internalPointer()
        else:
            return self.root

    def rowCount(self, parent: QtCore.QModelIndex):
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
    def __init__(self, root: Node, attributes: Sequence[str], parent=None):
        super().__init__(root, parent)
        self.attributes = attributes

    def _encode_nodes(self, keys=None, *nodes: Node) -> QtCore.QMimeData:
        if keys is None:
            keys = self.attributes
            attributes = self.attributes
        elif isinstance(keys, dict):
            keys = [keys[attr] if attr in keys else None for attr in self.attributes]
            indices = np.flatnonzero(keys)
            attributes = np.array(self.attributes)[indices]
        elif set(keys).intersection(self.attributes):
            keys = OrderedSet(keys)
            attributes = OrderedSet(self.attributes)
            keys = attributes = keys.intersection(attributes)

        node_info = ([str(getattr(node, attr)) if hasattr(node, attr) else '' for node in nodes]
                     for attr in attributes)
        return dict(zip(keys, node_info))


    def flags(self, index: QtCore.QModelIndex):
        default = super().flags(index)
        if index.isValid():
            default |= (QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled)
        return default

    def mimeTypes(self):
        return ['application/node']

    def get_nodes_as_dict(self, indices, keys=None):
        nodes = [self.get_node(index) for index in indices]
        return self._encode_nodes(keys, *nodes)

    def mimeData(self, indices) -> QtCore.QMimeData:
        data = self.get_nodes_as_dict(indices)
        mime = QtCore.QMimeData()
        mime.setData('application/node', pickle.dumps(data))
        return mime


class DataFrameModel(_DataFrameModel):
    def __init__(self, dataframe=None):
        super().__init__(dataframe)
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
        self._dataFrame = pd.DataFrame(columns=cols)
        self.endRemoveRows()
        return True


class ItemInfoTableModel(DataFrameModel):
    """
    """
    def __init__(self, source_selection_model, source_model, columns):
        self._column_to_attribute = \
            OrderedDict(zip(['Path', 'Name'], ['directory', 'name']))
        self._column_to_attribute.update(columns)

        super().__init__(pd.DataFrame(columns=self._column_to_attribute.keys()))

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
    item_dropped = QtCore.Signal()

    def _parse_dropped_data(self, mime_data):
        byte_data = mime_data.data('application/node')
        as_dict = pickle.loads(byte_data)
        as_dataframe = pd.DataFrame.from_dict(as_dict)
        columns = np.isin(as_dataframe.columns, self._dataFrame.columns)
        as_dataframe = as_dataframe.loc[:, columns]
        as_dataframe = as_dataframe.loc[as_dataframe.all(1), :]
        as_dataframe.astype(self._dataFrame.dtypes.to_dict(), copy=False)
        return as_dataframe

    def supportedDropActions(self):
        return QtCore.Qt.CopyAction

    def flags(self, index: QtCore.QModelIndex):
        default = super().flags(index)
        return default | QtCore.Qt.ItemIsDropEnabled

    def mimeTypes(self):
        return ['application/node']

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
            begin_row = self.rowCount()
            # parsed is a named tuple whose items are the string displayed
            # in the list, and the path to the data in the HDF5 file
            parsed = self._parse_dropped_data(data)
            if not self.addDataFrameRows(len(parsed.index)):
                # BUG: need to remove extraneous rows if the addDataFrameRows
                # operation failed halfway through
                print('adding row failed')
                return False

            self._dataFrame.iloc[begin_row:, :] = parsed.values
            self.item_dropped.emit()
            self.layoutChanged.emit()
            return True

            for r, tup in zip(count(begin_row), parsed):
                name_index = self.index(r, 0, QtCore.QModelIndex())
                self.setData(name_index, tup.name)
                path_index = self.index(r, 1, QtCore.QModelIndex())
                self.setData(path_index, tup.path)

            self.item_dropped.emit()
            return True

        else:
            return False
