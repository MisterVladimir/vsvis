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
import re
import sys
import os
from qtpy import QtCore, QtWidgets, uic
import pandas as pd
from typing import Sequence, Optional, Dict
from anytree import Node
from collections import OrderedDict, namedtuple
from vladutils.decorators import methdispatch as method_dispatch

from .models.tree import DraggableTreeModel
from .models.table import DroppableListModel, DataFrameModel
from .utils import load_node_from_hdf5
from . import UI_DIR, TEST_DIR
from .enums import DataType


DialogClass, DialogBaseClass = uic.loadUiType(
    os.path.join(UI_DIR, 'file_inspection_dialog.ui'))

GroupBoxClass, GroupBoxBaseClass = uic.loadUiType(
    os.path.join(UI_DIR, 'listbox.ui'))


class LabeledListWidget(GroupBoxClass, GroupBoxBaseClass):
    """
    A ListWidget inside a GroupBox, with buttons on the bottom to modify
    the contents of the list.
    """
    def __init__(self, title: str, parent: Optional[QtWidgets.QWidget] = None):
        super(GroupBoxBaseClass, self).__init__(parent)
        self.setupUi(self)
        self.groupbox.setTitle(title)

    def model(self):
        return self.list_view.model()

    def setModel(self, model: DroppableListModel) -> None:
        self.list_view.setModel(model)
        self._connect_buttons()

    def _delete(self, indices):
        model = self.model()
        _indices = [ind.row() for ind in indices]
        return model.removeDataFrameRows(_indices)

    def _connect_buttons(self):
        model = self.model()
        # https://stackoverflow.com/questions/21586643/pyqt-widget-connect-and-disconnect
        for button in (self.sort_button, self.delete_button, self.clear_button):
            while True:
                try:
                    button.clicked.disconnect()
                except TypeError:
                    break

        self.sort_button.clicked.connect(lambda: model.sort(0))
        self.delete_button.clicked.connect(
            lambda: self._delete(self.list_view.selectedIndexes()))
        self.clear_button.clicked.connect(lambda: model.clear())

    @method_dispatch
    def get_data(self, column=None):
        return self.model().dataFrame()

    @get_data.register(int)
    @get_data.register(slice)
    def _get_data(self, column):
        dataframe = self.list_view.model().dataFrame()
        return dataframe.iloc[:, column]

    @get_data.register(str)
    def _get_data(self, column):
        dataframe = self.list_view.model().dataFrame()
        return dataframe[column]

    @get_data.register(list)
    def _get_data(self, column):
        dataframe = self.list_view.model().dataFrame()
        # a hack until I figure out a way to dispatch by the type
        # contained within the list
        column = [dataframe.columns.get_loc(c) if isinstance(c, str) else c
                  for c in column]
        return dataframe.iloc[:, list(column)]

FileLoadingParameter = namedtuple(
    'FileLoadingParameter', ['attr', 'column', 'function'], defaults=[None])


class FileInspectionDialog(DialogClass, DialogBaseClass):
    def __init__(self, ID, parent: QtWidgets.QWidget = None):
        # XXX: might not need ID: DataType afterall
        super(DialogBaseClass, self).__init__(parent)
        self.setupUi(self)
        self.ID = ID
        self.list_widgets = dict()
        self.filename = None
        self.columns = []
        self.attributes = []
        self._model_setup()

    def _model_setup(self):
        # setup empty model for the tree view
        root = Node('root')
        model = DraggableTreeModel(root, [])
        self.file_structure_tree_view.setModel(model)

    def load_file(self, filename: str, *parameters: FileLoadingParameter):
        self.filename = filename
        self.attributes, self.columns, functions = zip(*parameters)

        args = [attr for attr, col, func in zip(self.attributes, self.columns, functions) if func is None]
        kwargs = {attr: func for attr, col, func in zip(self.attributes, self.columns, functions)
                  if func is not None}
        root = load_node_from_hdf5(filename, *args, **kwargs)

        tree_model = self.file_structure_tree_view.model()
        tree_model.layoutAboutToBeChanged.emit()
        tree_model.root = root
        tree_model.attributes = self.attributes
        tree_model.layoutChanged.emit()

        dataframe = pd.DataFrame(columns=self.columns)
        table_model = DataFrameModel(dataframe)
        self.data_preview_table_view.setModel(table_model)

        selection_model = self.file_structure_tree_view.selectionModel()
        try:
            selection_model.selectionChanged.disconnect(self.file_selection_changed)
        except TypeError:
            pass
        selection_model.selectionChanged.connect(lambda: self.file_selection_changed())

    def add_list_widget(
            self, title: str, columns: Sequence[str]) -> bool:

        # columns = np.array(columns)
        if not np.all(np.isin(columns, self.attributes)):
            print('{} not a subset of {}'.format(columns, self.attributes))
            return False

        widget = LabeledListWidget(title, self.data_preview_groupbox)
        self.list_layout.addWidget(widget)
        dataframe = pd.DataFrame(columns=columns)
        model = DroppableListModel(dataframe)
        widget.setModel(model)

        self.list_layout.addWidget(widget)
        self.list_widgets[title] = widget

        return True

    def file_selection_changed(self):
        """
        Every time the TreeView's selection is changed, update the TableModel
        to reflect the current selection. This isn't the most computatoinally
        efficient implementation -- it would be better to look for differnces,
        and update only those -- but this is much simpler.
        """
        table_model = self.data_preview_table_view.model()
        tree_model = self.file_structure_tree_view.model()
        indices = self.file_structure_tree_view.selectedIndexes()
        as_dict = tree_model.get_nodes_as_dict(indices, dict(zip(self.attributes, self.columns)))
        dataframe = pd.DataFrame.from_dict(as_dict)

        dif = len(indices) - table_model.rowCount()
        if dif < 0:
            table_model.removeDataFrameRows(np.arange(abs(dif)))
        elif dif > 0:
            table_model.addDataFrameRows(dif)

        table_model._dataFrame.iloc[:, :] = dataframe
        table_model.layoutChanged.emit()
        return True


def _make_dialog_base(filename, ID):
    dialog = FileInspectionDialog(ID)

    def get_name(dset):
        # pads numbers with zeros
        regexp = re.compile(r'[a-zA-Z]+')
        name = getattr(dset, 'name')
        name = name.split('/')[-1]
        if regexp.search(name):
            return name
        else:
            return '{:0>5}'.format(name)

    parameters = [
        FileLoadingParameter(
            attr='name',
            column='Name',
            function=get_name),
        FileLoadingParameter(
            attr='directory',
            column='Path',
            function=lambda dset: getattr(dset, 'name')),
        FileLoadingParameter(
            attr='shape', column='Shape'),
        FileLoadingParameter(
            attr='dtype',
            column="Type",
            function=lambda dset: str(getattr(dset, 'dtype')))]

    dialog.load_file(filename, *parameters)
    return dialog


def make_dialog(filename: str, names: Dict, ID: DataType) -> QtWidgets.QDialog:
    dialog = _make_dialog_base(filename, ID)
    for k, v in names.items():
        dialog.add_list_widget(k, v)
    return dialog
