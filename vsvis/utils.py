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
from anytree import Node


def load_node_from_hdf5(filename: str, *args):
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
        root = _recursively_load_as_node(h5file, '/', Node('root'), *args)

    while root.parent is not None:
        root = root.parent
    return root


def _recursively_load_as_node(grp, path, node, *args):
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
        '/group1/group2/dataset1'
        """
        return str(node).split("'")[1][5:]

    row = 0
    for key, item in grp[path].items():
        if isinstance(item, h5py.Dataset):
            kwargs = {arg: getattr(item, arg) for arg in args}
            child = Node(key, node, row=row, **kwargs)
            row += 1

        elif isinstance(item, h5py.Group):
            while node.parent is not None:
                if nodepath(node) == path[:-1]:
                    break
                else:
                    node = node.parent
            child = Node(key, node, row=row)
            node = _recursively_load_as_node(
                grp, path + key + '/', child, *args)
            row += 1
    return node
