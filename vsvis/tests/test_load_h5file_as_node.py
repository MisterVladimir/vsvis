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

from ..config import TEST_DIR
from ..utils import load_node_from_hdf5


class Test(object):
    filename = os.path.join(TEST_DIR, 'data', 'test.h5')

    @pytest.mark.dependency
    def test_no_extra_args(self):
        root = load_node_from_hdf5(self.filename)

        assert root.parent is None
        assert root.name == 'root'
        assert len(root.children) == 3
        grp1 = root.children[1]
        assert grp1.name == 'image'
        dset1_1 = grp1.children[0]
        assert dset1_1.name == 'data'

    @pytest.mark.dependency(depends=['Test::test_no_extra_args'])
    def test_with_args(self):
        args = ['shape', 'dtype']
        root = load_node_from_hdf5(self.filename, *args)

        grp0 = root.children[0]
        dset0_0 = grp0.children[0]
        assert dset0_0.name == '0'
        assert dset0_0.shape == (28, 2)
        assert str(dset0_0.dtype) == 'float32'

        grp2 = root.children[2]
        grp21 = grp2.children[1]
        dset21_0, dset21_1, dset21_2 = grp21.children

        assert dset21_1.name == '1'
        assert dset21_1.shape == (10, )
        assert str(dset21_1.dtype) == 'float32'

    @pytest.mark.dependency(depends=['Test::test_no_extra_args'])
    def test_with_kwargs(self):
        kwargs = {'directory': lambda item: getattr(item, 'name')}
        root = load_node_from_hdf5(self.filename, **kwargs)

        grp0 = root.children[0]
        dset0_0 = grp0.children[0]
        assert dset0_0.name == '0'
        assert dset0_0.directory == '/ground_truth/0'

        grp2 = root.children[2]
        grp21 = grp2.children[1]
        dset21_0, dset21_1, dset21_2 = grp21.children

        assert dset21_1.name == '1'
        assert dset21_1.directory == '/predicted/probabilities/1'

        assert dset21_2.name == '2'
        assert dset21_2.directory == '/predicted/probabilities/2'
