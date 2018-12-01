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

from .models.table import HDF5TableModel
from .enums import DataType


class Controller(QtCore.QObject):
    """
    """
    table_selection_changed = QtCore.Signal(
        'QItemSelection', 'QItemSelection', object)

    def __init__(self, scene, tabwidget, columns, datasources):
        start_index = 0
        self.scene = scene
        self.tabwidget = tabwidget
        self.dtypes = list(self.tabwidget.keys())
        # self.tableviews = tabwidget.values()
        self.datasources = datasources
        self.current_index = start_index
        self._columns = columns
        assert len(self.tableviews) == len(datasources)
        assert len(columns) == len(self.tableviews)

        self.change_table_models(start_index)

    def _signals_setup(self):
        self.tabwidget.currentChanged[int].connect(self._tab_changed)
        for table in self.tabwidget.values():


    @QtCore.Slot('QItemSelection', 'QItemSelection')
    def _emit_table_selection_changed(self, selected, deselected):
        tab_index = self.tabwidget.currentIndex()
        dtype = self.dtypes[tab_index]
        self.table_selection_changed.emit(selected, deselected, dtype)

    def getCurentIndex(self):
        return self._current_index

    @QtCore.Slot(int)
    def setCurrentIndex(self, value):
        self._current_index = value

    def resetCurrentIndex(self):
        self._current_index = 0

    currentIndex = QtCore.Property(
        int, 'getCurentIndex', 'setCurrentIndex', 'resetCurrentIndex')

    @QtCore.Slot(int)
    def _tab_changed(self, i):
        index = self.currentIndex
        for dtype in self.tabwidget.keys():
            self.scene.set_markers_visible(index, dtype, False)

        dtype = self.dtypes[i]
        table = self.tabwidget[dtype]
        ind = [ind.row() for ind in table.selectedIndexes()]
        self.scene.set_markers_visible(index, dtype, True, ind)

    @QtCore.Slot(int)
    def set_index(self, index: int):
        for dtype in (DataType.GROUND_TRUTH, DataType.PREDICTED):
            self.scene.set_markers_visible(index, dtype, False)
        self._set_image(index)
        for table in self.tableviews.values():
            table.setSelection(QtCore.QRect(0, 0, 0, 0),
                               QtCore.QItemSelectionModel.Clear)
        self._set_table_models(index)
        self.currentIndex = index

    def _set_image(self, index: int):
        source = self.datasources[DataType.IMAGE]
        image = source.request(index)
        pixmap = self.scene.array2pixmap(image, rescale=True)
        self.scene.pixmap = pixmap

    def _set_table_models(self, index: int):
        views = self.tableviews
        sources = self.datasources

        for view, source, col in zip(views, sources, self._columns):
            dsets = [s.request(index) for s in source]
            model = HDF5TableModel(dsets, col, show_row_index=True)
            view.setModel(model)

    @QtCore.Slot('QItemSelection', 'QItemSelection', object)
    def toggle_visible_graphics_items(self, visible, invisible, dtype):
        visible = [ind.row() for ind in visible.indexes()]
        invisible = [ind.row() for ind in invisible.indexes()]

        index = self.currentIndex
        self.scene.set_markers_visible(index, dtype, True, visible)
        self.scene.set_markers_visible(index, dtype, False, invisible)
