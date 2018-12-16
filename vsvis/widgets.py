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
from qtpy import QtCore, QtWidgets
from typing import Optional
from vladutils.data_structures import EnumDict

from .enums import DataType


class VGraphicsView(QtWidgets.QGraphicsView):
    """
    Zoomable GraphicsView.
    """
    # minimum image view size
    minimum_size = (256, 256)
    # sensitivity to zoom
    zoom_rate = 1.1

    def wheelEvent(self, event):
        factor = self.zoom_rate**(event.angleDelta().y() / 120.)
        self.scale(factor, factor)

    @QtCore.Slot()
    def zoom_in(self):
        self.scale(self.zoom_rate, self.zoom_rate)

    @QtCore.Slot()
    def zoom_out(self):
        self.scale(1. / self.zoom_rate, 1. / self.zoom_rate)

    @QtCore.Slot()
    def fit_to_window(self):
        self.fitInView(self.sceneRect(), QtCore.Qt.KeepAspectRatio)


class VProbabilitySlider(QtWidgets.QSlider):
    def __init__(self, mask, parent=None):
        super().__init__(parent=parent)
        self._mask = mask

    @QtCore.Slot(int)
    def activate(self, index):
        enabled = self._mask[index]
        self.setEnabled(enabled)


class VTabTableView(QtWidgets.QTableView):
    selection_changed = QtCore.Signal(
        'QItemSelection', 'QItemSelection', object)

    def __init__(
            self, dtype: DataType, parent: Optional[QtCore.QObject] = None):
        super().__init__(parent)
        self.dtype = dtype
        self._signals_setup()

    def _signals_setup(self):
        model = self.selectionModel()
        model.selectionChanged['QItemSelection', 'QItemSelection'].connect(
            self._emit_selection_changed)

    @QtCore.Slot('QItemSelection', 'QItemSelection')
    def _emit_selection_changed(self, selected, deselected):
        self.selection_changed.emit(selected, deselected, self.dtype)


class VTabWidget(QtWidgets.QTabWidget):
    """
    Parameters
    ------------
    titles : EnumDict
        Keys are a DataType and values are the tab's label for that DataType.
    """
    dtypes = [DataType.GROUND_TRUTH, DataType.PREDICTED]

    def __init__(self, parent: Optional[QtCore.QObject] = None):
        super().__init__(parent)
        self._widgets = EnumDict([(k, None) for k in self.dtypes])
        self.tables = EnumDict([(k, None) for k in self.dtypes])

    def add_tab(self, dtype: DataType, name: str):
        if not any([dtype & d for d in self.dtypes]):
            raise KeyError('{} not in self.dtypes'.format(dtype))

        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        table = VTabTableView(dtype, parent=widget)
        table.setSizePolicy(QtWidgets.QSizePolicy.Preferred,
                            QtWidgets.QSizePolicy.Expanding)
        table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        table.horizontalHeader().setCascadingSectionResizes(True)
        layout.addWidget(table)
        self.addTab(widget, name)

        self.tables[dtype] = table
        self._widgets[dtype] = widget

    def __getitem__(self, dtype):
        return self.tables[dtype]

    def __setitem__(self, key, value):
        pass

    def __len__(self):
        return len(self.tables)

    def __iter__(self):
        return iter(self.tables)

    def keys(self):
        return self.tables.keys()

    def values(self):
        return self.tables.values()

    def items(self):
        return self.tables.items()

    def setModel(self, dtype, model):
        self.tables[dtype].setModel(model)
