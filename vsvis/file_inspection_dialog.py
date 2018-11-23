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
import numpy as np
import sys
import os
from PyQt5 import QtCore, QtWidgets, uic
import pandas as pd
from typing import Union, Sequence
from anytree import Node
from collections import OrderedDict, namedtuple

from . import models
from .utils import load_node_from_hdf5
from . import UI_DIR


DialogClass, DialogBaseClass = uic.loadUiType(
    os.path.join(UI_DIR, 'file_inspection_dialog.ui'))

GroupBoxClass, GroupBoxBaseClass = uic.loadUiType(
    os.path.join(UI_DIR, 'listbox.ui'))


class LabeledListWidget(GroupBoxClass, GroupBoxBaseClass):
    def __init__(self, title: str, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        self.setupUi(self)
        self.groupbox.setTitle(title)

    def setModel(self, model: models.DroppableListModel) -> None:
        self.list_view.setModel(model)

    def get_data(self, column: Union[int, slice]) -> np.ndarray:
        model = self.list_view.model()
        df = model.dataFrame()
        data = df.iloc[:, column]
        return data.values

FileLoadingParameter = namedtuple(
    'FileLoadingParameter', ['attr', 'column', 'function'], defaults=[None])


class FileInspectionDialog(DialogClass, DialogBaseClass):
    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        self.setupUi(self)
        self.list_widgets = {}
        self.filename = None
        self.columns = []
        self.attributes = []
        self._model_setup()

    def _model_setup(self):
        root = Node('root')
        model = models.DraggableTreeModel(root)
        self.file_structure_tree_view.setModel(model)

    def load_file(self, filename: str, *parameters):
        self.filename = filename
        self.attributes, self.columns, functions = zip(*parameters)

        args = [attr for attr, col, func in zip(self.attributes, self.columns, functions) if func is None]
        kwargs = {attr: func for attr, col, func in zip(self.attributes, self.columns, functions)
                  if func is not None}
        root = load_node_from_hdf5(filename, *args, **kwargs)

        tree_model = self.file_structure_tree_view.model()
        tree_model.root = root
        tree_model.layoutChanged.emit()

        dataframe = pd.DataFrame(columns=self.columns)
        table_model = models.DataFrameModel(dataframe)
        self.data_info_table_view.setModel(table_model)

        selection_model = self.file_structure_tree_view.selectionModel()
        try:
            selection_model.disconnect(self.file_selection_changed)
        except Exception:
            pass
        selection_model.selectionChanged[
            QtCore.QItemSelection, QtCore.QItemSelection].connect(
                lambda i, j: self.file_selection_changed(i, j))

    def add_list_widget(
            self, title: str, columns: Sequence[str]) -> bool:

        # columns = np.array(columns)
        if not np.all(np.isin(columns, self.columns)):
            print('{} not a subset of {}'.format(columns, self.columns))
            return False

        widget = LabeledListWidget(title, self.data_info_groupbox)
        self.list_layout.addWidget(widget)
        dataframe = pd.DataFrame(columns=columns)
        model = models.DroppableListModel(dataframe)
        widget.setModel(model)

        widget.sort_button.clicked.connect(lambda: model.sort(0))
        widget.delete_button.clicked.connect(
            lambda: model.removeDataFrameRows(widget.list_view.selectedIndexes()))
        widget.clear_button.clicked.connect(lambda: model.clear())

        self.list_layout.addWidget(widget)
        self.list_widgets[title] = widget

        return True

    def file_selection_changed(self, selected, deselected):
        def filter_indices(indices):
            model = self.file_structure_tree_view.model()
            nodes = (model.get_node(index) for index in indices)
            mask = [hasattr(n, 'directory') for n in nodes]
            indices = list(np.array(indices)[mask])
            return indices

        def get_rows(indices):
            dataframe = self.data_info_table_view.model()._dataFrame
            model = self.file_structure_tree_view.model()
            nodes = (model.get_node(index) for index in indices)
            paths = [n.directory for n in nodes]
            mask = np.isin(dataframe['Path'], paths)
            return mask

        def get_data(indices):
            model = self.file_structure_tree_view.model()
            nodes = (model.get_node(index) for index in indices)
            data = [[str(getattr(node, attr)) for attr in self.attributes] for node in nodes]

            return data

        selected = filter_indices(selected.indexes())
        deselected = filter_indices(deselected.indexes())

        dif = len(selected) - len(deselected)
        model = self.data_info_table_view.model()
        dataframe = model.dataFrame()

        if dif > 0:
            model.addDataFrameRows(dif)
        elif dif < 0:
            rows = get_rows(deselected[-abs(dif):])
            deselected = deselected[-abs(dif):]
            model.removeDataFrameRows(rows)

        # at this point all we need to do is replace
        if len(deselected) > 0:
            rows = get_rows(deselected)
            data = get_data(selected[:len(deselected)])
            dataframe.iloc[rows, :] = data
            selected = selected[len(deselected):]
        if len(selected) > 0:
            data = get_data(selected)
            dataframe.iloc[-abs(dif):, :] = data

        model.layoutChanged.emit()
        dataframe.reset_index(drop=True, inplace=True)
        return True
