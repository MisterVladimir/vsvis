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
from qtpy import QtCore, QtWidgets, uic
import os

from .file_inspection_dialog import make_dialog
from . import UI_DIR
from .models.scene import VScene


tr = QtCore.QObject.tr
DataInspectorClass, DataInspectorBaseClass = uic.loadUiType(
    os.path.join(UI_DIR, 'data_inspector_widget.ui'))


class DataInspectorWidget(DataInspectorClass, DataInspectorBaseClass):
    def __init__(self, parent=None):
        super(DataInspectorBaseClass, self).__init__(parent)
        self.setupUi(self)


class VMainWindow(QtWidgets.QMainWindow):
    def __init__(self, central_widget_class, *args, **kwargs):
        super().__init__()
        self._setup(central_widget_class, *args, **kwargs)
        self._menubar_setup()
        self._signals_setup()
        self.retranslateUi()

    def _setup(self, WidgetClass, *args, **kwargs):
        self.resize(800, 600)
        self.setObjectName("main_window")
        self.central_widget = WidgetClass(parent=self, *args, **kwargs)
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
            self, tr(self, 'Open File'), '',
            tr(self, 'HDF5 Files (*.h5 *.hdf5 *.hf5 *.hd5)'),
            None, QtWidgets.QFileDialog.DontUseNativeDialog)
        dialog = make_dialog(filename[0])
        dialog.show()

    def retranslateUi(self):
        self.setWindowTitle(tr(self, "MainWindow"))
        self.menu_file.setTitle(tr(self, "File"))
        self.action_open.setText(tr(self, "Open..."))


def make_main_window(central_widget_class, *args, **kwargs):
    window = VMainWindow(central_widget_class)
    scene = VScene(['ground_truth', 'predicted'])
    window.central_widget.graphics_view.setScene(scene)
    return window
