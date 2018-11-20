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

from . import models
from .utils import load_node_from_hdf5
from . import UI_DIR


DialogClass, DialogBaseClass = uic.loadUiType(
    os.path.join('ui', 'file_inspection_dialog.ui'))

GroupBoxClass, GroupBoxBaseClass = uic.loadUiType(os.path.join('ui', 'groupbox.ui'))


class LabeledListWidget(GroupBoxClass, GroupBoxBaseClass):
    def __init__(self, title: str, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        self.groupbox.setTitle(title)

    def setModel(self, model: models.DroppableListModel) -> None:
        self.list_view.setModel(model)

    def get_data(self, column: Union(int, slice)) -> np.ndarray:
        model = self.list_view.model()
        df = model.dataFrame()
        data = df.iloc[:, column]
        return data.values


class FileInspectionDialog(DialogClass, DialogBaseClass):
    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        self.list_widgets = {}
        self.filename = None
        self.columns = []
        self.attributes = []
        self._model_setup()

    def _model_setup(self):
        root = Node('root')
        model = models.DraggableTreeModel(root)
        self.file_structure_tree_view.setModel(model)

    def load_file(self, filename: str, **attributes):
        self.filename = filename
        self.columns = list(attributes.keys())
        self.attributes = list(attributes.values())
        root = load_node_from_hdf5(filename, *self.attributes)
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

        columns = np.array(columns)
        if not np.all(np.isin(columns, self.columns)):
            print('{} not a subset of {}'.format(columns, self.columns))
            return False

        widget = LabeledListWidget(title)
        dataframe = pd.DataFrame(columns=columns)
        model = models.DroppableListModel(dataframe)
        widget.setModel(model)

        widget.sort_button.clicked.connect(lambda: model.sort(0))
        widget.delete_button.clicked(
            lambda: model.removeDataFrameRows(widget.selectedIndexes()))
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
            model = self.file_structure_tree_view.model()
            nodes = (self.source_model.get_node(index) for index in indices)
            paths = [n.directory for n in nodes]
            mask = np.isin(self._dataFrame['Path'], paths)
            return self._dataFrame.index[mask].values

        def get_data(indices):
            model = self.file_structure_tree_view.model()
            nodes = (model.get_node(index) for index in indices)
            data = [[str(getattr(node, self._column_to_attribute[c])) for c in self.columns] for node in nodes]

            return data

        selected = filter_indices(selected.indexes())
        deselected = filter_indices(deselected.indexes())

        dif = len(selected) - len(deselected)
        model = self.data_info_table_view.model()
        dataframe = model.dataFrame()
        print('model is view: {}'.format(model is self.data_info_table_view.model()))
        print('dataframe is view: {}'.format(dataframe is model._dataFrame))

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


class _FileInspectionDialog(QtWidgets.QDialog, Ui_file_inspection_dialog):
    def __init__(self, filename, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self._setup_models()
        self._get_file_info(filename)

    def _setup_models(self):
        # mime_type = models.DraggableTreeModel.mime_type
        dataframe = pd.DataFrame(columns=['node', 'path'])
        images_model = models.DroppableListModel(dataframe, copy=True)
        self.images_list_view.setModel(images_model)
        # self.images_list_view.set_drop_sources(self.file_structure_tree_view)
        roi_model = models.DroppableListModel(dataframe, copy=True)
        self.roi_list_view.setModel(roi_model)
        # self.roi_list_view.set_drop_sources(self.file_structure_tree_view)

    def _drop_signals_setup(self):
        image_model = self.images_list_view.model()
        image_model.item_dropped.connect(lambda: self.file_structure_tree_view.clearSelection())
        self.images_sort_button.clicked.connect(lambda: image_model.sort(0))
        self.images_clear_button.clicked.connect(lambda: image_model.clear())

        roi_model = self.roi_list_view.model()
        roi_model.item_dropped.connect(lambda: self.file_structure_tree_view.clearSelection())
        self.roi_sort_button.clicked.connect(lambda: roi_model.sort(0))
        self.roi_clear_button.clicked.connect(lambda: roi_model.clear())

    def _get_file_info(self, filename):
        extra_column_names = ['Shape', 'Type']
        extra_node_attributes = ['shape', 'dtype']
        root = load_node_from_hdf5(filename, *extra_node_attributes)
        model = models.DraggableTreeModel(root)
        self.file_structure_tree_view.setModel(model)

        self._drop_signals_setup()

        selection_model = self.file_structure_tree_view.selectionModel()
        columns_to_node_attributes = OrderedDict(zip(extra_column_names,
                                                     extra_node_attributes))
        table_model = models.ItemInfoTableModel(
            selection_model, model, columns_to_node_attributes)
        self.data_info_table_view.setModel(table_model)


def test():
    filename = os.path.join(UI_DIR, 'test_file_info_dialog.h5')
    filename = os.path.abspath(filename)
    # print(filename)
    app = QtWidgets.QApplication(sys.argv)
    dialog = FileInspectionDialog(filename)
    dialog.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    # run()
    test()
