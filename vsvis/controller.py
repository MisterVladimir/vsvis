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
from typing import Dict, Any

from .models.table import HDF5TableModel
from .datasource import HDF5DataSource
from .enums import DataType
from .widgets import VTabWidget


class Controller(QtCore.QObject):
    """
    Coördinates the display of markers and images.

    Parameters
    ------------
    scene : QtWidgets.QGraphicsScene
    tabwidget : widgets.VTabWidget
    columns : EnumDict
    datasources : EnumDict
    """
    def __init__(self, scene: QtWidgets.QGraphicsScene, tabwidget: VTabWidget,
                 columns: Dict[DataType, Any], datasources: Dict[DataType, Any]):
        start_index = 0
        self.scene = scene
        self.tabwidget = tabwidget
        self.datasources = datasources
        self.current_index = start_index
        assert len(self.tabwidget) == len(datasources)
        assert len(columns) == len(self.tabwidget)

    def _signals_setup(self):
        self.tabwidget.currentChanged[int].connect(self._tab_changed)
        for table in self.tabwidget.values():
            table.selection_changed[
                'QItemSelection', 'QItemSelection', object].connect(
                self.toggle_visible_graphics_items)

    @QtCore.Slot('QItemSelection', 'QItemSelection', object)
    def toggle_visible_graphics_items(self, visible, invisible, dtype):
        visible = [ind.row() for ind in visible.indexes()]
        invisible = [ind.row() for ind in invisible.indexes()]

        index = self.currentIndex
        self.scene.set_markers_visible(index, dtype, True, visible)
        self.scene.set_markers_visible(index, dtype, False, invisible)

    @QtCore.Slot(int)
    def _tab_changed(self, i):
        if i == -1:
            return None

        index = self.currentIndex
        for dtype in self.tabwidget.keys():
            self.scene.set_markers_visible(index, dtype, False)

        dtype = self.dtypes[i]
        table = self.tabwidget[dtype]
        ind = [ind.row() for ind in table.selectedIndexes()]
        self.scene.set_markers_visible(index, dtype, True, ind)

    @QtCore.Slot(int)
    def set_index(self, index: int):
        # for dtype in (DataType.GROUND_TRUTH, DataType.PREDICTED):
        #     self.scene.set_markers_visible(index, dtype, False)
        # for table in self.tabwidget.values():
        #     table.setSelection(QtCore.QRect(0, 0, 0, 0),
        #                        QtCore.QItemSelectionModel.Clear)
        self._set_image(index)
        self._set_table_models(index)
        self.currentIndex = index

    def _set_image(self, index: int):
        source = self.datasources[DataType.IMAGE][0]
        image = source.request(index)
        pixmap = self.scene.array2pixmap(image, rescale=True)
        self.scene.pixmap = pixmap

    def _set_table_models(self, index: int):
        views = self.tabwidget.values()
        sources = self.datasources[DataType.DATA]
        columns = self.columns[DataType.DATA]

        for view, source, col in zip(views, sources, columns):
            dsets = [s.request(index) for s in source]
            model = HDF5TableModel(dsets, col, show_row_index=True)
            view.setModel(model)

    def getCurentIndex(self):
        return self._current_index

    @QtCore.Slot(int)
    def setCurrentIndex(self, value):
        self._current_index = value

    def resetCurrentIndex(self):
        self._current_index = 0

    currentIndex = QtCore.Property(
        int, 'getCurentIndex', 'setCurrentIndex', 'resetCurrentIndex')

    def _get_dtypes(self):
        return list(self.tabwidget.keys())

    dtypes = QtCore.Property(list, '_get_dtypes')
