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
from collections import namedtuple
from itertools import repeat, count
from vladutils.iteration import isiterable

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
            dims = [[h5file[h].ndim for h in li] for li in handles]
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


Index = namedtuple('Index', ['handle', 'i'])


class _HDF5Request(Callable):
    # XXX: maybe it'd be better to implement HDF5DataSource with a
    # __getitem__-style interface instead of using the current 'request' method
    # to request data.
    pass


class HDF5Request1D(_HDF5Request):
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
    def __init__(self, filename: str, dataset_names: Sequence[str], axis: Optional[int] = None):
        self.filename = filename
        self.axis = axis

        # if axis is None:
        #     self.dataset_names = np.concatenate(dataset_names)
        # else:
        #     self.dataset_names = np.squeeze(dataset_names)
        self.dataset_names = np.concatenate(dataset_names)
        if not self.dataset_names.ndim == 1:
            raise ValueError('dataset_names must be one-dimensional '
                             '(or squeezable to one dimension).')

        self.length, self._cum_lengths = self._get_axis_lengths(
            filename, self.dataset_names, axis)

    def _get_axis_lengths(self, filename, handles, axis):
        # TODO: add gui_error for ValueError and a warning if axis_lengths are not all equal along axis
        axis_lengths = []
        if axis is None:
            ret = [{c: Index(h, i)} for h, i, c
                   in zip(handles, repeat(slice(None)), range(len(handles)))]
            return len(handles), ret
        else:
            with h5py.File(filename) as h5file:
                ndims = [h5file[h].ndim for h in handles]
                if not np.min(ndims) == np.max(ndims):
                    raise ValueError('All Datasets must have the same '
                                     'number of dimensions.')
                ndims = ndims[0]
                # length of each Dataset along the desired axis
                axis_lengths = [h5file[h].shape[axis] for h in handles]
                cum = np.cumsum(axis_lengths)

                # pair up appropriate 'index' argument to the Dataset name and
                # slice within the Dataset
                _handles = np.concatenate([list(repeat(h, n)) for h, n in zip(handles, cum)])
                _indices = np.concatenate([np.arange(c) for c in cum])
                _slices = (tuple([slice(i, i+1) if d == axis else slice(None)
                           for d in range(ndims)]) for i in _indices)
                ret = {c: Index(h, i) for h, i, c in zip(_handles, _slices, count())}
                return cum[-1], ret

    def __call__(self, index: int) -> Index:
        """
        """
        try:
            return self._cum_lengths[index]
        except KeyError as e:
            raise IndexError('Index out of range.') from e


class HDF5Request2D(_HDF5Request):
    """
    Used in HDF5DataSource.

    Parameters
    -------------
    filename: str
        Filename of HDF5 file that holds data.

    dataset_names
        A 2D array containing the names of Datasets to be concatenated. Names
        in the last dimension are concatenated along the axis determined by
        HDF5DataSource. For example,

        >>> fn = 'example.hdf5'
        >>> names == [['/a/0', '/a/1'], ['/b/0', '/b/1']]
        >>> req = HDF5Request2D(fn, names)
        >>> req(0)
        (['/a/0', '/a/1'], None)
        >>> req(1)
        (['/b/0', '/b/1'], None)

        If constructing HDF5DataSource with req as the 'request' parameter,
        calling the HDF5DataSource instance's 'request' function with index=0
        will return the concatenated Datasets, h5file['/a/0'] and
        h5file['/a/1'].
    """
    def __init__(self, filename: str, dataset_names: np.ndarray):
        self.filename = filename
        self.dataset_names = np.array(dataset_names, dtype=str)
        self.length = len(dataset_names)

    def __call__(self, index: int) -> Tuple[Sequence[str], None]:
        """
        """
        if index >= len(self.dataset_names):
            raise IndexError('Index out of range.')

        name = self.dataset_names[index]
        return name, None


class HDF5DataSource(object):
    """
    Together with HDF5Request, allows indexing into a list of
    h5py.Dataset objects as if they were stacked together.
    """
    def __init__(self, filename: str, request: _HDF5Request):
        self.filename = filename
        self._request = request
        self.h5file = h5py.File(filename)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.cleanup()

    def __len__(self):
        return self._request.length

    def cleanup(self):
        self.h5file.close()

    def request(self, index: int, axis: int = 0):
        name, sl = self._request(index)
        if isiterable(name):
            return np.concatenate([self.h5file[n] for n in name], axis)
        else:
            return self.h5file[name][sl]
