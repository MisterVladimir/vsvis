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
from qtpy import QtCore

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
