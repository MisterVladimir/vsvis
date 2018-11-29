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
import pandas as pd
import numpy as np
import pickle
import h5py
import numbers
from itertools import count
from qtpy import QtCore
from typing import Sequence, Optional

from ..contrib.qtpandas.models import DataFrameModel as _DataFrameModel


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


class ListModel(DataFrameModel):
    """
    A list modeled as a pandas DataFrame. Visible items are in the first
    column. Additional unseen data may be added in other columns.
    """
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
    A list model that can accept items dropped from the DraggableTreeModel.
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
                return False

            self._dataFrame.iloc[begin_row:, :] = parsed.values
            self.item_dropped.emit()
            self.layoutChanged.emit()
            return True


class HDF5TableModel(QtCore.QAbstractTableModel):
    decimals = 1

    def __init__(self, datasets: Sequence[h5py.Dataset],
                 columns: Optional[Sequence[str]] = None,
                 show_row_index: bool = True):

        self._datasets = datasets
        self._show_row_index = show_row_index

        column_lengths = [dset.shape[1] for dset in datasets]
        self._cum_col_lengths = np.cumsum(column_lengths)

        if columns is None:
            self._columns = [None] * self._cum_col_lengths[-1]
        else:
            self._columns = list(columns)

        assert self._cum_col_lengths[-1] == len(self._columns)

    def rowCount(self):
        return self._root.shape[0]

    def columnCount(self):
        return len(self._columns)

    def headerData(self, section: int, orientation: int = QtCore.Qt.Horizontal,
                   role: int = QtCore.Qt.DisplayRole):

        if role == QtCore.Qt.DisplayRole and section < self.columnCount():
            return self._columns[section]
        else:
            return None

    def data(self, index: QtCore.QModelIndex,
             role: int = QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        elif role == QtCore.Qt.DisplayRole:
            row = index.row()
            col = index.column()
            if col > self.columnCount() or row > self.rowCount():
                return None
            elif col == 0 and self._show_row_index:
                return row
            # offset the index's column number if the first column is
            # the row number
            col = col - int(self._show_row_index)
            # identify which dataset to display values from
            mask = col < self._cum_col_lengths
            dset = self._datasets[mask][-1]
            # determine the column index within the desired dataset
            # if sum(mask) == 1, the column number is high, meaning we're
            # selecting from the last dataset
            if sum(mask) == 1:
                ind = col
            # otherwise, determine the column number within the dataset
            else:
                cum = self._cum_col_lengths[mask]
                ind = cum[-1] - cum[-2]
            value = dset[row, ind]

            # round floating point values to make the table compact
            if isinstance(value, numbers.Integral):
                return value
            elif isinstance(value, numbers.Real):
                return np.round(value, self.decimals)
            else:
                return value
        else:
            return None

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.NoItemFlags
        else:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
