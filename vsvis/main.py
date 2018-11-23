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
import sys
import os
import h5py
import numpy as np
from pandas import DataFrame
from anytree import Node, RenderTree
from collections import OrderedDict, namedtuple
from PyQt5 import QtCore, QtGui, QtWidgets

from ui.file_inspection_dialog2 import Ui_file_inspection_dialog
from vsvis import models
from vsvis.utils import load_node_from_hdf5
from vsvis.views import DropListView

tr = QtCore.QObject.tr
DatasetInfo = namedtuple('DatasetInfo', ['shape', 'path', 'name'])


class VMainWindow(QtWidgets.QMainWindow):
    def __init__(self, central_widget_class):
        super().__init__()
        self._setup(central_widget_class)
        self._menubar_setup()
        self._signals_setup()
        self.retranslateUi()

    def _setup(self, WidgetClass):
        self.resize(800, 600)
        self.setObjectName("main_window")
        self.central_widget = WidgetClass(parent=self)
        self.central_widget.setObjectName("central_widget")
        self.setCentralWidget(self.central_widget)

    def _menubar_setup(self):
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 25))
        self.menubar.setObjectName("menubar")
        self.menu_file = QtWidgets.QMenu(self.menubar)
        self.menu_file.setObjectName("menu_file")
        self.setMenuBar(self.menubar)

        self.action_open = QtWidgets.QAction(self)
        self.action_open.setObjectName("action_open")
        self.menu_file.addAction(self.action_open)
        self.menubar.addAction(self.menu_file.menuAction())

    def _signals_setup(self):
        self.action_open.triggered.connect(self.open)

    def open(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(
            self, tr(self, 'Open File'), '', tr(self, 'HDF5 Files (*.h5 *.hdf5 *.hf5 *.hd5)'),
            None, QtWidgets.QFileDialog.DontUseNativeDialog)
        dialog = FileInspectionDialog(filename[0], parent=self)
        dialog.show()

    def retranslateUi(self):
        self.setWindowTitle(tr(self, "MainWindow"))
        self.menu_file.setTitle(tr(self, "File"))
        self.action_open.setText(tr(self, "Open..."))


class FileInspectionDialog(QtWidgets.QDialog, Ui_file_inspection_dialog):
    def __init__(self, filename, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self._setup_models()
        self._get_file_info(filename)

    def _setup_models(self):
        # mime_type = models.DraggableTreeModel.mime_type
        dataframe = DataFrame(columns=['node', 'path'])
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


def run():
    app = QtWidgets.QApplication(sys.argv)
    main_window = VMainWindow(QtWidgets.QWidget)
    main_window.show()
    sys.exit(app.exec_())


def test_file_info_dialog():
    from vsvis.file_inspection_dialog import FileInspectionDialog, FileLoadingParameter
    from vsvis import TEST_DIR

    filename = os.path.abspath(os.path.join(TEST_DIR, 'data', 'test_file_info_dialog.h5'))
    # print(filename)
    app = QtWidgets.QApplication(sys.argv)
    dialog = FileInspectionDialog()

    parameters = [
        FileLoadingParameter(attr='name', column='Name'),
        FileLoadingParameter(attr='directory',
                             column='Path',
                             function=lambda dset: getattr(dset, 'name')),
        FileLoadingParameter(attr='shape', column='Shape'),
        FileLoadingParameter(attr='dtype',
                             column="Type",
                             function=lambda dset: str(getattr(dset, 'dtype')))]

    dialog.load_file(filename, *parameters)
    dialog.add_list_widget('title', ['Name', "Path"])
    dialog.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    # run()
    test_file_info_dialog()
