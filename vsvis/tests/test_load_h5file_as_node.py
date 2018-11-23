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
import pytestqt
import pytest
import pandas as pd
import os
import h5py
from abc import ABC

from .. import TEST_DIR
from ..utils import load_node_from_hdf5


class Test(object):
    filename = os.path.join(TEST_DIR, 'data', 'test_file_info_dialog.h5')

    @pytest.mark.dependency
    def test_no_extra_args(self):
        root = load_node_from_hdf5(self.filename)

        assert root.parent is None
        assert root.name == 'root'
        assert len(root.children) == 3
        grp3 = root.children[2]
        assert grp3.name == 'grp3'
        dset3_1 = grp3.children[0]
        assert dset3_1.name == 'dset3_1'

    @pytest.mark.dependency(depends=['Test::test_no_extra_args'])
    def test_with_args(self):
        args = ['shape', 'dtype']
        root = load_node_from_hdf5(self.filename, *args)

        grp1 = root.children[0]
        grp11 = grp1.children[0]
        dset11_1 = grp11.children[0]
        assert dset11_1.name == 'dset11_1'
        assert dset11_1.shape == (11, 1)
        assert str(dset11_1.dtype) == 'float32'

        grp2 = root.children[1]
        grp22 = grp2.children[1]
        dset22_1, dset22_2 = grp22.children

        assert dset22_1.name == 'dset22_1'
        assert dset22_1.shape == (22, 1)
        assert str(dset22_1.dtype) == 'float32'

        assert dset22_2.name == 'dset22_2'
        assert dset22_2.shape == (22, 2)
        assert str(dset22_2.dtype) == 'float32'

    @pytest.mark.dependency(depends=['Test::test_no_extra_args'])
    def test_with_kwargs(self):
        kwargs = {'directory': lambda item: getattr(item, 'name')}
        root = load_node_from_hdf5(self.filename, **kwargs)

        grp1 = root.children[0]
        grp11 = grp1.children[0]
        dset11_1 = grp11.children[0]
        assert dset11_1.name == 'dset11_1'
        assert dset11_1.directory == '/grp1/grp11/dset11_1'

        grp2 = root.children[1]
        grp22 = grp2.children[1]
        dset22_1, dset22_2 = grp22.children

        assert dset22_1.name == 'dset22_1'
        assert dset22_1.directory == '/grp2/grp22/dset22_1'

        assert dset22_2.name == 'dset22_2'
        assert dset22_2.directory == '/grp2/grp22/dset22_2'
