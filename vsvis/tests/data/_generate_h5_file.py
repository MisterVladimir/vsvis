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
import numpy as np


def generate_h5_file(filename):
    """
    Script to generate the tests/data/test.h5 file.


    Its structure is:

        ground_truth <HDF5 group "/ground_truth" (3 members)>
            0 <HDF5 dataset "0": shape (A, 2), type "<f4">
            1 <HDF5 dataset "1": shape (B, 2), type "<f4">
            2 <HDF5 dataset "2": shape (C, 2), type "<f4">
        image <HDF5 group "/image" (1 members)>
            data <HDF5 dataset "data": shape (3, 128, 128), type "<u2">
        predicted <HDF5 group "/predicted" (2 members)>
            coordinates <HDF5 group "/predicted/coordinates" (3 members)>
                0 <HDF5 dataset "0": shape (D, 2), type "<f4">
                1 <HDF5 dataset "1": shape (E, 2), type "<f4">
                2 <HDF5 dataset "2": shape (F, 2), type "<f4">
            probabilities <HDF5 group "/predicted/probabilities" (3 members)>
                0 <HDF5 dataset "0": shape (D,), type "<f4">
                1 <HDF5 dataset "1": shape (E,), type "<f4">
                2 <HDF5 dataset "2": shape (F,), type "<f4">

    where A, B, C, D, E, and F are random integers between 1 and 50.
    """
    with h5py.File(filename) as f:
        def add_random_coordinate_set(name, n, grp, m=2):
            grp.create_dataset(name, data=np.random.rand(n, m).astype(np.float32)*122+3)

        imgrp = f.create_group('image')
        im = np.random.randint(0, 65536, size=(3, 128, 128), dtype=np.uint16)
        imgrp.create_dataset('data', data=im)
        gt_group = f.create_group('ground_truth')
        for name, n in zip(('0', '1', '2'), np.random.randint(1, 50, 3)):
            add_random_coordinate_set(name, n, gt_group)

        pred_group = f.create_group('predicted')
        coord = pred_group.create_group('coordinates')
        for name, n in zip(('0', '1', '2'), np.random.randint(1, 50, 3)):
            add_random_coordinate_set(name, n, coord)

        prob = pred_group.create_group('probabilities')
        lengths = [
            dset.shape[0] for dset in f['/predicted/coordinates'].values()]
        for name, n in zip(('0', '1', '2'), lengths):
            prob.create_dataset(name, data=np.random.rand(n).astype(np.float32))
