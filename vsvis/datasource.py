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
from typing import Optional, Sequence, Tuple, Union
from collections.abc import Callable


"""
This API is written to be (somewhat) consistent with FileDataSource objects
found in vladutils.io.datasource's modules, e.g.
tiff_datasource.TiffDataSource.
"""


class HDF5Request(Callable):
    """
    Index along a list of HDF5 Datasets as if they were stacked along
    the 'axis' parameter.

    Parameters
    -------------
    filename: str
        Filename of HDF5 file that holds data.

    axis: int, None
        For a given h5py.Dataset, which axis do we want to index on? For
        example, if our h5py.Dataset has shape [4, 3, 128, 128], selecting
        axis=0 would produce outputs of shape [3, 128, 128]. If axis is None,
        return the whole h5py.Dataset values.

    dataset_names: str
        Name of the h5py.Datasets, such that h5file[name] -> h5py.Dataset
    """
    def __init__(self, filename: str, axis: Optional[int] = None, *dataset_names: str):
        if len(dataset_names) < 1:
            raise ValueError('Please enter at least one dataset name.')
        self.filename = filename
        self.dataset_names = dataset_names
        self.axis = axis

        self._dims, self._cum_lengths = self._get_axis_lengths(
            filename, axis, dataset_names)

    def _get_axis_lengths(self, filename, axis, handles):
        axis_lengths = []
        with h5py.File(filename) as h5file:
            dims = [h5file[h].ndim for h in handles]
            if axis is not None:
                axis_lengths = [h5file[h].shape[axis] for h in handles]
                return dims, np.cumsum(axis_lengths)
            else:
                return dims, None

    def __call__(self, index: int) -> Tuple[str, Tuple[Union[slice, int]]]:
        """
        """
        if index > self._cum_lengths[-1]:
            raise IndexError('Index out of range.')
        elif self.axis is None:
            return self.dataset_names[index], (slice(None), )

        mask = index < self._cum_lengths
        dataset_index = np.arange(len(self.dataset_names))[mask][-1]
        dataset_name = self.dataset_names[dataset_index]
        if not sum(mask) == 1:
            masked_cum_lengths = self._cum_lengths[mask]
            index = index - masked_cum_lengths[-2]

        slice_index = (slice(None), ) * self._dims[dataset_index]
        slice_index[self.axis] = index

        return dataset_name, index


class HDF5DataSource(object):
    """
    Together with HDF5Request, allows indexing into a list of
    h5py.Dataset objects as if they were stacked together.
    """
    def __init__(self, filename: str, request: HDF5Request):
        self.filename = filename
        self._request = request
        self.h5file = h5py.File(filename)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.cleanup()

    def cleanup(self):
        self.h5file.close()

    def request(self, index: int):
        name, sl = self._request(index)
        return self.h5file[name][sl].value
