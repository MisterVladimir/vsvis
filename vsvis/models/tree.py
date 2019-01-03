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
from collections import OrderedDict
from typing import Union, Sequence, Optional, Dict, Iterator
from qtpy.QtCore import QObject, QMimeData, QAbstractItemModel, QModelIndex, Qt
# from qtpy.QtWidgets import QWidget
from anytree import Node
from ordered_set import OrderedSet


class NodeTreeModel(QAbstractItemModel):
    def __init__(self, root: Node, parent: QObject = None):
        super().__init__(parent)
        self.root = root

    def get_node(self, index: QModelIndex):
        if index.isValid():
            # print('internal pointer: {}'.format(index.internalPointer()))
            return index.internalPointer()
        else:
            return self.root

    def rowCount(self, parent: QModelIndex):
        """
        Parameters
        ------------
        parent : QModelIndex
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
            return QModelIndex()
        else:
            return self.createIndex(parent_node.row, 0, parent_node)

    def data(self, index: QModelIndex, role: int) -> Union[str, None]:
        if not index.isValid():
            return None
        node = index.internalPointer()

        if role == Qt.DisplayRole:
            return node.name

    def flags(self, index: QModelIndex):
        if index.isValid():
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled
        else:
            return Qt.NoItemFlags

    def index(self, row: int, column: int, parent: QModelIndex) -> QModelIndex:
        """
        Returns an index at the given row, column of the parent.

        Parameters
        ------------
        row : int
        column : int
        parent : QModelIndex
        """
        parentNode = self.get_node(parent)

        childItem = parentNode.children[row]

        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()


class DraggableTreeModel(NodeTreeModel):
    """
    Parameters
    ------------
    root : anytree.Node
        Base node of the tree.

    encodable : Sequence[str]
        Node's attributes that are encoded into the mimed data when a mouse
        drag event is initiated at an item in the TreeView associated with
        this model.

    parent : Optional[QObject]
        Parent item. Usually this is left as None.
    """
    def __init__(self, root: Node, encodable: Sequence[str],
                 parent: Optional[QObject] = None):
        super().__init__(root, parent)
        self.encodable = encodable

    def _encode_nodes(self, nodes: Sequence[Node],
                      keys: Optional[Union[Dict, Sequence]] = None) -> QMimeData:
        """
        Encodes data from anytree.Node object as strings.
        """
        if keys is None:
            # encode all attributes
            keys = self.encodable
            encodable = self.encodable
        elif isinstance(keys, dict):
            # in the dictionary returned by this method, replace the keys with
            # the corresponding values in this dictionary
            # e.g. if keys = {'old_name': 'new_name'}, the Node's 'old_name'
            # attribute will be mapped to the 'new_name' key in the output
            # dictionary
            keys = [keys[attr] if attr in keys else None for attr in self.encodable]
            indices = np.flatnonzero(keys)
            encodable = np.array(self.encodable)[indices]
            keys = filter(None, keys)
        elif set(keys).intersection(self.encodable):
            # check that the keys list that was passed can be encoded
            keys = OrderedSet(keys)
            encodable = OrderedSet(self.encodable)
            encodable = keys.intersection(encodable)
        else:
            return OrderedDict()

        node_info = ([str(getattr(node, attr)) if hasattr(node, attr) else ''
                      for node in nodes] for attr in encodable)
        return OrderedDict(zip(keys, node_info))

    def flags(self, index: QModelIndex):
        default = super().flags(index)
        if index.isValid():
            default |= (Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)
        return default

    def mimeTypes(self):
        return ['application/node']

    def get_nodes_as_dict(self, indices: Sequence[QModelIndex],
                          keys: Optional[Union[Dict, Sequence]]=None) -> Dict[str, str]:
        """
        For each Node corresponding to the QModelIndex, encode the Node's data
        as a dictionary.
        """
        nodes = [self.get_node(index) for index in indices]
        return self._encode_nodes(nodes, keys)

    def mimeData(self, indices) -> QMimeData:
        data = dict(self.get_nodes_as_dict(indices))
        mime = QMimeData()
        mime.setData('application/node', pickle.dumps(data))
        return mime
