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
import h5py
import sys
import traceback
from anytree import Node
from abc import abstractmethod
from vladutils.data_structures import EnumDict

from .widgets import VErrorMessageBox


def load_node_from_hdf5(filename: str, *args, **kwargs) -> Node:
    """
    Load the contents of an HDF5 file into an anytree.Node object. The result
    is a graph whose root is a Node('root') and the leaves are Datasets.
    Dataset attributes that we want to load store may be passed into *args.

    Parameters
    ------------
    filename : str
        Filename of HDF5 file.

    args : str
        Attributes of Dataset objects to store in each leaf node.
    """
    with h5py.File(filename, 'r') as h5file:
        root = _recursively_load_as_node(h5file, '/', Node('root'), *args, **kwargs)

    while root.parent is not None:
        root = root.parent
    return root


def _recursively_load_as_node(grp, path, node, *args, **kwargs):
    """
    """
    def nodepath(node):
        """
        >>> root = Node('root')
        >>> group1 = Node('group1', parent=root)
        >>> group2 = Node('group2', parent=group1)
        >>> dataset1 = Node('dataset1', parent=group2)
        >>> str(dataset1)
        "Node('/root/group1/group2/dataset1')"
        >>> nodepath(dataset1)
        '/group1/group2/dataset1/'
        """
        return str(node).split("'")[1][5:] + '/'

    row = 0
    for key, item in grp[path].items():
        if isinstance(item, h5py.Dataset):
            _kwargs = {'name': key, 'parent': node, 'row': row}
            _kwargs.update({k: fn(item) for k, fn in kwargs.items()})
            _kwargs.update({arg: getattr(item, arg) for arg in args})
            child = Node(**_kwargs)
            # child.directory = nodepath(child)
            row += 1

        elif isinstance(item, h5py.Group):
            # backtrack to common branchpoint
            while node.parent is not None:
                # print(nodepath(node))
                # print(path)
                if nodepath(node) == path:
                    break
                else:
                    node = node.parent

            child = Node(name=key, parent=node, row=row)
            node = _recursively_load_as_node(
                grp, path + key + '/', child, *args, **kwargs)
            row += 1
    return node


def gui_error(message: str):
    """
    Wrapper
    """
    def wrapper(func):
        def wrapped(self, *args, **kwargs):
            try:
                ret = func(*args, **kwargs)
            except Exception:
                typ, value, tb = sys.exc_info()
                li = traceback.format_exception(typ, value, tb)
                detailed = ''.join(li)
                dialog = VErrorMessageBox()
                dialog.message = message
                dialog.traceback = detailed
                dialog.exec_()
            else:
                return ret
        return wrapped
    return wrapper
