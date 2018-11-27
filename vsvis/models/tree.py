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
from typing import Union, Sequence
from qtpy import QtCore
from anytree import Node
from ordered_set import OrderedSet


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
