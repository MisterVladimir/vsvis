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
import h5py
import numpy as np
import sys
from pandas import concat, DataFrame
from os.path import extsep, join, splitext
from copy import copy
# from qtpy import QtCore, QtWidgets, uic

from qtpy.QtCore import Property, Qt, Signal, Slot
from qtpy.QtWidgets import QFileDialog, QWidget

from collections import OrderedDict
from typing import Sequence, Dict
from vladutils.data_structures import EnumDict

from .file_inspection_dialog import make_dialog
from .config import (
    DataType, Shape, EXTENSIONS, FILETYPES, MARKER_ICONS, UI_DIR, loadUiType)
from .datasource import HDF5Request1D, HDF5Request2D, HDF5DataSource
from .models.scene import VGraphicsScene, MarkerFactory
from .models.table import HDF5TableModel
from .widgets import VTabWidget, VMarkerOptionsWidget, VErrorMessageBox
from .controller import Controller

# TODO: use this same loadUiType function in the rest of the program
Ui_VMainWindowClass, VMainWindowBaseClass = loadUiType(
    join(UI_DIR, 'main_window3.ui'))


class VMainWindow(VMainWindowBaseClass, Ui_VMainWindowClass):
    #                      str, DataFrame, DataType
    data_selected = Signal(str, object, object)
    predicted_data_selected = Signal(dict)
    ground_truth_data_selected = Signal(dict)
    image_data_selected = Signal([str, list], [str])
    file_loaded = Signal(object)
    # filename_accepted = Signal(str, object)
    # filename_rejected = Signal()

    def __init__(self):
        super(VMainWindow, self).__init__()
        self.setupUi(self)

        self._widget_setup()
        self._signals_setup()

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        try:
            self.controller.cleanup()
        except AttributeError:
            pass

    def _widget_setup(self):
        self._error_dialog = VErrorMessageBox(self)

        self._file_dialog = QFileDialog(self, self.tr('Open File'), '')
        self._file_dialog.setOption(QFileDialog.DontUseNativeDialog)

        # type(self.marker_options_groupbox) -> widgets.VMarkerOptionsGroupBox
        self.marker_options_groupbox.add_widget(
            'Predicted', DataType.PREDICTED)
        self.marker_options_groupbox.add_widget(
            'Ground Truth', DataType.GROUND_TRUTH)
        for ow in self.marker_options_groupbox.widgets.values():
            for s in Shape:
                ow.add_marker_shape(s, MARKER_ICONS[s][0])

        scene = VGraphicsScene()
        self.graphics_view.setScene(scene)

        self.controller = Controller(scene, self.tables_tab_widget, self.marker_options_groupbox)

    def _signals_setup(self) -> None:
        self.action_open_ground_truth.triggered.connect(
            lambda: self.open(DataType.GROUND_TRUTH))
        self.action_open_predicted.triggered.connect(
            lambda: self.open(DataType.PREDICTED))
        self.action_open_image.triggered.connect(
            lambda: self.open(DataType.IMAGE))

        self.graphics_view_scrollbar.value_changed[int].connect(
            self.controller.set_index)

        self.file_loaded[object].connect(self.marker_options_groupbox.enable)

    def _parse_filename(self, filelist: Sequence[str], dtype: DataType):
        def create_error_dialog(message):
            self._error_dialog.message = message
            self._error_dialog.exec_()
            self.filename_rejected.emit()

        if len(filelist) > 1:
            return create_error_dialog(
                '{} files were selected '.format(len(filelist)) +
                'but we can only load one file at a time.')
        elif len(filelist) == 0:
            return create_error_dialog('No files were selected.')
        else:
            filename = filelist[0]
        # temporary to reject loaded tif images because loading them
        # hasn't been implemented yet
        print('***parsing filename***')
        filename_ext = splitext(filename)[-1]
        if filename_ext in EXTENSIONS[DataType.TIFF_IMAGE][0]:
            create_error_dialog('tiff files not yet supported.')
        else:
            return filename

    def open(self, dtype: DataType) -> None:
        """
        Opens a Dialog in which the user selects a (HDF5 or TIFF) file. To
        achieve this, we must first create a regexp-containing string for
        the 'filter' argument to the 'getOpenFileName' method.
        """
        extensions = OrderedDict(zip(FILETYPES[dtype], EXTENSIONS[dtype]))
        ext = [[''] + list(ext) for ext in extensions.values()]
        extlist = [self.tr(k) + " (" + ' *'.join(e) + ")" for k, e in zip(extensions, ext)]
        filter_ = ';;'.join(extlist)
        # example filter_ string:
        # Tiff Files (*.tif, *.tiff, *.ome.tif);;HDF5 Files (*.h5, *.hdf5, *.hf5, *.hd5)
        self._file_dialog.setNameFilter(filter_)
        result = self._file_dialog.exec_()
        if result == QFileDialog.Accepted:
            filename = self._parse_filename(
                self._file_dialog.selectedFiles(), dtype)
            self.open_inspection_widget(filename, dtype)

    def open_inspection_widget(self, filename: str, dtype: DataType):
        list_widget_columns = ['name', 'directory']
        ground_truth_titles = OrderedDict(
            [('Ground Truth Coordinates', list_widget_columns)])
        predicted_titles = OrderedDict(
            [('Predicted Coordinates', list_widget_columns),
             ('Probabilities', list_widget_columns)])
        image_titles = OrderedDict(
            [('Images', list_widget_columns)])

        list_widget_args = EnumDict([
            (DataType.GROUND_TRUTH, ground_truth_titles),
            (DataType.PREDICTED, predicted_titles),
            (DataType.HDF_IMAGE, image_titles)])

        args = list_widget_args[dtype][0]
        dialog = make_dialog(filename, args, dtype)
        result = dialog.exec_()
        if result == QFileDialog.Accepted:
            self.load(filename, dtype, dialog.get_data('directory'))

    def load(self, filename: str, dtype: DataType, handles: DataFrame):
        if dtype & DataType.HDF_IMAGE:
            req = HDF5Request1D(filename, handles, axis=0)
            self.graphics_view_scrollbar.setEnabled(True)
        elif dtype & DataType.DATA:
            req = HDF5Request2D(filename, handles)
        else:
            raise NotImplementedError('Loading {} not yet implemented.'.format(dtype))

        print(filename)
        print(dtype)
        print(handles)
        source = HDF5DataSource(filename, req)
        self.controller.set_datasource(source, dtype)
        self.graphics_view_scrollbar.setMaximum(len(source) - 1)
        self.file_loaded.emit(dtype)

    @Slot()
    def save(self):
        pass

    @Slot()
    def save_as(self):
        pass

    @Slot()
    def quit(self):
        sys.exit(0)
